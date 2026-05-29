"""
ml_analytics_service.py
Servicio de Machine Learning e Inteligencia de Datos para Saber Pro.
Implementa: clustering, predicción de tendencias, correlaciones y anomalías.
"""
from __future__ import annotations

import warnings
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.preprocessing import LabelEncoder, StandardScaler

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────
SCORE_COLS = [
    "avg_razonamiento",
    "avg_lectura_critica",
    "avg_ingles",
    "avg_global",
]

CLUSTER_LABELS = {
    0: "Desempeño Bajo",
    1: "Desempeño Medio",
    2: "Desempeño Alto",
}


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _to_df(records: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(records)


def _safe_float(value) -> Optional[float]:
    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return None


# ─────────────────────────────────────────────
# 1. CLUSTERING — Segmentación de entidades
# ─────────────────────────────────────────────
def cluster_entities(
    records: list[dict],
    entity_key: str,
    n_clusters: int = 3,
) -> list[dict]:
    """
    Agrupa instituciones / departamentos / municipios en clusters de
    desempeño usando K-Means sobre las 4 métricas de puntaje.

    Args:
        records:    Lista de dicts con avg_* y una clave de identidad.
        entity_key: Nombre de la clave de identidad (ej. 'institucion').
        n_clusters: Número de clusters (default 3).

    Returns:
        Lista de dicts enriquecidos con 'cluster_id' y 'cluster_label'.
    """
    if len(records) < n_clusters:
        return records

    df = _to_df(records).dropna(subset=SCORE_COLS)
    if df.empty:
        return records

    X = df[SCORE_COLS].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["cluster_id"] = kmeans.fit_predict(X_scaled)

    # Ordenar clusters por avg_global ascendente → 0=bajo, 1=medio, 2=alto
    centers = (
        df.groupby("cluster_id")["avg_global"].mean().sort_values().index.tolist()
    )
    rank_map = {old: new for new, old in enumerate(centers)}
    df["cluster_id"] = df["cluster_id"].map(rank_map)
    df["cluster_label"] = df["cluster_id"].map(CLUSTER_LABELS)

    return df.to_dict(orient="records")


# ─────────────────────────────────────────────
# 2. PREDICCIÓN — Tendencias futuras
# ─────────────────────────────────────────────
def predict_trends(
    trend_records: list[dict],
    periods_ahead: int = 4,
) -> dict:
    """
    Predice puntajes futuros usando Linear Regression sobre la serie
    temporal de promedios por periodo (ej. 20181, 20182, …).

    Args:
        trend_records:  Salida de get_trends() con campo 'periodo'.
        periods_ahead:  Cuántos periodos futuros predecir.

    Returns:
        Dict con predicciones por métrica y R² de cada modelo.
    """
    if len(trend_records) < 3:
        return {"error": "Se necesitan al menos 3 periodos para predecir."}

    df = _to_df(trend_records).dropna(subset=["periodo"])
    df = df.sort_values("periodo")
    df["periodo_num"] = range(len(df))

    predictions: dict = {"periodos_predichos": [], "metricas": {}, "r2_scores": {}}

    # Generar etiquetas de periodos futuros (ej. 20221 → 20222 → 20231…)
    last_periodo = str(df["periodo"].iloc[-1])
    predictions["periodos_predichos"] = _generate_future_periods(
        last_periodo, periods_ahead
    )

    X = df[["periodo_num"]].values
    X_future = np.array(
        [[len(df) + i] for i in range(1, periods_ahead + 1)]
    )

    for col in ["avg_razonamiento", "avg_lectura_critica", "avg_ingles", "avg_global"]:
        if col not in df.columns:
            continue
        y = df[col].values
        model = LinearRegression()
        model.fit(X, y)
        y_pred_future = model.predict(X_future)
        r2 = r2_score(y, model.predict(X))

        predictions["metricas"][col] = [_safe_float(v) for v in y_pred_future]
        predictions["r2_scores"][col] = _safe_float(r2)

    # Agregar histórico para que el frontend pueda graficar la línea completa
    predictions["historico"] = trend_records

    return predictions


def _generate_future_periods(last: str, n: int) -> list[str]:
    """Genera n periodos siguientes en formato YYYYS (ej. '20182' → '20191')."""
    periods = []
    year = int(last[:4])
    semester = int(last[4:]) if len(last) == 5 else 1
    for _ in range(n):
        if semester == 1:
            semester = 2
        else:
            semester = 1
            year += 1
        periods.append(f"{year}{semester}")
    return periods


# ─────────────────────────────────────────────
# 3. CORRELACIONES — Feature importance
# ─────────────────────────────────────────────
def compute_correlations(records: list[dict], target: str = "avg_global") -> dict:
    """
    Calcula la correlación de Pearson entre variables numéricas del dataset
    y el puntaje objetivo. Útil para detectar factores más influyentes.

    Args:
        records: Lista de dicts con múltiples columnas numéricas.
        target:  Columna objetivo (default 'avg_global').

    Returns:
        Dict con lista de {variable, correlacion} ordenada por |correlacion|.
    """
    if not records:
        return {"correlaciones": []}

    df = _to_df(records)
    numeric_df = df.select_dtypes(include=[np.number])

    if target not in numeric_df.columns:
        return {"correlaciones": []}

    corr = numeric_df.corr()[target].drop(target, errors="ignore")
    corr_sorted = corr.abs().sort_values(ascending=False)

    result = [
        {
            "variable": var,
            "correlacion": _safe_float(corr[var]),
            "correlacion_abs": _safe_float(corr_sorted[var]),
        }
        for var in corr_sorted.index
    ]
    return {"target": target, "correlaciones": result}


# ─────────────────────────────────────────────
# 4. IMPORTANCIA DE VARIABLES — Random Forest
# ─────────────────────────────────────────────
def compute_feature_importance(
    records: list[dict],
    target: str = "avg_global",
    categorical_cols: Optional[list[str]] = None,
) -> dict:
    """
    Entrena un Random Forest para estimar qué variables (estrato, género,
    internet, educación padres…) tienen más peso sobre el puntaje global.

    Args:
        records:          Lista de dicts con columnas mixtas.
        target:           Variable a predecir.
        categorical_cols: Columnas categóricas a codificar.

    Returns:
        Dict con lista de {feature, importancia} ordenada desc.
    """
    if len(records) < 10:
        return {"error": "Datos insuficientes (mínimo 10 registros)."}

    categorical_cols = categorical_cols or []
    df = _to_df(records).dropna(subset=[target])

    # Codificar categóricas
    le = LabelEncoder()
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Desconocido").astype(str)
            df[col] = le.fit_transform(df[col])

    feature_cols = [
        c for c in df.select_dtypes(include=[np.number]).columns if c != target
    ]
    if not feature_cols:
        return {"error": "No hay features numéricas disponibles."}

    X = df[feature_cols].fillna(0).values
    y = df[target].values

    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X, y)

    importance_df = pd.DataFrame(
        {"feature": feature_cols, "importancia": rf.feature_importances_}
    ).sort_values("importancia", ascending=False)

    return {
        "target": target,
        "features": importance_df.to_dict(orient="records"),
        "r2_train": _safe_float(r2_score(y, rf.predict(X))),
    }


# ─────────────────────────────────────────────
# 5. ANOMALÍAS — Isolation Forest
# ─────────────────────────────────────────────
def detect_anomalies(
    records: list[dict],
    entity_key: str,
    contamination: float = 0.1,
) -> dict:
    """
    Detecta instituciones / departamentos con puntajes atípicos usando
    Isolation Forest.

    Args:
        records:       Lista de dicts con avg_*.
        entity_key:    Clave de identidad del registro.
        contamination: Proporción esperada de anomalías (default 10%).

    Returns:
        Dict con listas 'anomalos' y 'normales'.
    """
    if len(records) < 5:
        return {"anomalos": [], "normales": records}

    df = _to_df(records).dropna(subset=SCORE_COLS)
    if df.empty:
        return {"anomalos": [], "normales": records}

    X = df[SCORE_COLS].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    iso = IsolationForest(contamination=contamination, random_state=42)
    df["anomaly"] = iso.fit_predict(X_scaled)  # -1 = anómalo, 1 = normal
    df["anomaly_score"] = iso.score_samples(X_scaled)

    anomalos = df[df["anomaly"] == -1].drop(columns=["anomaly"]).to_dict(orient="records")
    normales = df[df["anomaly"] == 1].drop(columns=["anomaly"]).to_dict(orient="records")

    return {
        "total": len(df),
        "total_anomalos": len(anomalos),
        "entity_key": entity_key,
        "anomalos": anomalos,
        "normales": normales,
    }


# ─────────────────────────────────────────────
# 6. RESUMEN EJECUTIVO — Estado actual del negocio
# ─────────────────────────────────────────────
def generate_business_summary(kpis: dict, trends: list[dict]) -> dict:
    """
    Genera un resumen descriptivo e interpretativo del estado actual
    del sistema educativo a partir de los KPIs y tendencias.

    Returns:
        Dict con métricas clave, tendencia general y alertas.
    """
    summary: dict = {"kpis": {}, "tendencia": {}, "alertas": []}

    # KPIs actuales
    for col in SCORE_COLS:
        val = kpis.get(col)
        if val is not None:
            summary["kpis"][col] = _safe_float(val)

    # Tendencia: comparar primer y último periodo disponible
    if len(trends) >= 2:
        first = trends[0]
        last = trends[-1]
        for col in ["avg_razonamiento", "avg_lectura_critica", "avg_ingles", "avg_global"]:
            f_val = first.get(col)
            l_val = last.get(col)
            if f_val and l_val:
                delta = l_val - f_val
                pct = (delta / f_val) * 100 if f_val else 0
                summary["tendencia"][col] = {
                    "inicio": _safe_float(f_val),
                    "fin": _safe_float(l_val),
                    "delta": _safe_float(delta),
                    "variacion_pct": _safe_float(pct),
                    "direccion": "↑ Mejora" if delta > 0 else "↓ Declive" if delta < 0 else "→ Estable",
                }

    # Alertas automáticas
    global_avg = kpis.get("avg_global")
    if global_avg and global_avg < 140:
        summary["alertas"].append(
            {"tipo": "critico", "mensaje": f"Puntaje global promedio bajo: {global_avg:.1f} (umbral: 140)"}
        )
    ingles = kpis.get("avg_ingles")
    if ingles and ingles < 120:
        summary["alertas"].append(
            {"tipo": "advertencia", "mensaje": f"Puntaje de inglés crítico: {ingles:.1f}"}
        )

    return summary
"""
ml_insights.py  —  Router FastAPI
Endpoints de Machine Learning e Inteligencia de Datos para Saber Pro.
Prefijo: /ml-insights
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends

from application.dtos.response_dto import ResponseDTO
from domain.entities.role import Role
from domain.entities.user import User
from infrastructure.repositories.mongo_analytics_repository import MongoAnalyticsRepository
from infrastructure.repositories.mongo_ml_repository import MongoMLRepository
from presentation.api.v1.dependencies import (
    get_analytics_repo,
    get_ml_repo,
    require_roles,
)
from infrastructure.services.ml_analytics_service import (
    cluster_entities,
    compute_correlations,
    compute_feature_importance,
    detect_anomalies,
    generate_business_summary,
    predict_trends,
)

router = APIRouter(prefix="/ml-insights", tags=["ml-insights"])
_AUTH = require_roles(Role.ANALISTA, Role.GERENTE, Role.ADMIN)


# ─────────────────────────────────────────────
# 1. CLUSTERING de instituciones
# ─────────────────────────────────────────────
@router.get(
    "/clustering/institutions",
    response_model=ResponseDTO[list],
    summary="Segmentación K-Means de instituciones por desempeño",
)
async def clustering_institutions(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    n_clusters: int = 3,
    limit: int = 200,
    _: User = _AUTH,
    ml_repo: MongoMLRepository = Depends(get_ml_repo),
):
    """
    Aplica K-Means para agrupar instituciones en N clusters
    según sus promedios en las 4 competencias genéricas.
    Cada institución recibe un `cluster_id` (0=bajo, 1=medio, 2=alto)
    y un `cluster_label` descriptivo.
    """
    records = await ml_repo.get_institution_scores_for_clustering(
        periodo, departamento, limit
    )
    data = cluster_entities(records, entity_key="institucion", n_clusters=n_clusters)
    return ResponseDTO(status_code=200, message="OK", data=data)


# ─────────────────────────────────────────────
# 2. CLUSTERING de departamentos
# ─────────────────────────────────────────────
@router.get(
    "/clustering/departments",
    response_model=ResponseDTO[list],
    summary="Segmentación K-Means de departamentos por desempeño",
)
async def clustering_departments(
    periodo: Optional[str] = None,
    n_clusters: int = 3,
    _: User = _AUTH,
    ml_repo: MongoMLRepository = Depends(get_ml_repo),
    analytics_repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    records = await analytics_repo.get_by_department(periodo=periodo, limit=100)
    data = cluster_entities(records, entity_key="departamento", n_clusters=n_clusters)
    return ResponseDTO(status_code=200, message="OK", data=data)


# ─────────────────────────────────────────────
# 3. PREDICCIÓN de tendencias
# ─────────────────────────────────────────────
@router.get(
    "/prediction/trends",
    response_model=ResponseDTO[dict],
    summary="Predicción de puntajes futuros con Regresión Lineal",
)
async def prediction_trends(
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    periods_ahead: int = 4,
    _: User = _AUTH,
    analytics_repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    """
    Usa Regresión Lineal sobre la serie temporal de promedios por periodo
    para predecir los próximos `periods_ahead` semestres.
    Incluye R² de cada modelo para evaluar confiabilidad.
    """
    trend_records = await analytics_repo.get_trends(
        departamento=departamento, institucion=institucion
    )
    data = predict_trends(trend_records, periods_ahead=periods_ahead)
    return ResponseDTO(status_code=200, message="OK", data=data)


# ─────────────────────────────────────────────
# 4. CORRELACIONES socioeconómicas
# ─────────────────────────────────────────────
@router.get(
    "/correlations/socioeconomic",
    response_model=ResponseDTO[dict],
    summary="Correlación de Pearson entre factores socioeconómicos y puntaje",
)
async def correlations_socioeconomic(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    target: str = "avg_global",
    sample_size: int = 5000,
    _: User = _AUTH,
    ml_repo: MongoMLRepository = Depends(get_ml_repo),
):
    """
    Calcula la correlación de Pearson entre variables numéricas del
    dataset (estrato, horas de trabajo, etc.) y el puntaje objetivo.
    Permite identificar los factores más relacionados al desempeño.
    """
    records = await ml_repo.get_socioeconomic_sample(periodo, departamento, sample_size)

    # Codificar variables binarias antes de correlacionar
    import pandas as pd
    df = pd.DataFrame(records)
    binary_map = {"Si": 1, "No": 0, "M": 1, "F": 0}
    for col in ["tiene_internet", "tiene_computador", "genero"]:
        if col in df.columns:
            df[col] = df[col].map(binary_map)

    # Codificar estrato numérico
    if "estrato" in df.columns:
        estrato_map = {
            "Sin estrato": 0, "Estrato 1": 1, "Estrato 2": 2,
            "Estrato 3": 3, "Estrato 4": 4, "Estrato 5": 5, "Estrato 6": 6,
        }
        df["estrato"] = df["estrato"].map(estrato_map)

    # Codificar horas de trabajo
    if "horas_trabajo" in df.columns:
        horas_map = {
            "0": 0, "Entre 0 y 10": 5, "Entre 11 y 20": 15,
            "Entre 21 y 30": 25, "Más de 30": 35,
        }
        df["horas_trabajo"] = df["horas_trabajo"].map(horas_map)

    # Añadir avg_global si no existe
    score_cols = ["avg_razonamiento", "avg_lectura_critica", "avg_ingles"]
    if "avg_global" not in df.columns and all(c in df.columns for c in score_cols):
        df["avg_global"] = df[score_cols].mean(axis=1)

    data = compute_correlations(df.to_dict(orient="records"), target=target)
    return ResponseDTO(status_code=200, message="OK", data=data)


# ─────────────────────────────────────────────
# 5. FEATURE IMPORTANCE con Random Forest
# ─────────────────────────────────────────────
@router.get(
    "/feature-importance",
    response_model=ResponseDTO[dict],
    summary="Importancia de variables con Random Forest",
)
async def feature_importance(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    target: str = "avg_global",
    sample_size: int = 3000,
    _: User = _AUTH,
    ml_repo: MongoMLRepository = Depends(get_ml_repo),
):
    """
    Entrena un Random Forest con variables socioeconómicas e institucionales
    para determinar cuáles tienen mayor poder predictivo sobre el puntaje.
    Retorna importancias normalizadas (suman 1.0) y R² del modelo.
    """
    records = await ml_repo.get_socioeconomic_sample(periodo, departamento, sample_size)

    categorical_cols = [
        "tiene_internet", "tiene_computador", "genero",
        "educacion_padre", "educacion_madre", "tipo_institucion",
        "horas_trabajo", "estrato", "departamento",
    ]

    import pandas as pd
    df = pd.DataFrame(records)
    score_cols = ["avg_razonamiento", "avg_lectura_critica", "avg_ingles"]
    if "avg_global" not in df.columns and all(c in df.columns for c in score_cols):
        df["avg_global"] = df[score_cols].mean(axis=1)

    data = compute_feature_importance(
        df.to_dict(orient="records"),
        target=target,
        categorical_cols=categorical_cols,
    )
    return ResponseDTO(status_code=200, message="OK", data=data)


# ─────────────────────────────────────────────
# 6. DETECCIÓN DE ANOMALÍAS por departamento
# ─────────────────────────────────────────────
@router.get(
    "/anomalies/departments",
    response_model=ResponseDTO[dict],
    summary="Detección de departamentos con puntajes atípicos (Isolation Forest)",
)
async def anomalies_departments(
    periodo: Optional[str] = None,
    contamination: float = 0.1,
    _: User = _AUTH,
    ml_repo: MongoMLRepository = Depends(get_ml_repo),
):
    """
    Usa Isolation Forest para detectar departamentos con puntajes
    significativamente diferentes a la media nacional.
    `contamination` controla qué porcentaje se considera anómalo (0.05–0.20).
    """
    records = await ml_repo.get_department_scores_for_anomaly(periodo)
    data = detect_anomalies(records, entity_key="departamento", contamination=contamination)
    return ResponseDTO(status_code=200, message="OK", data=data)


# ─────────────────────────────────────────────
# 7. ANOMALÍAS por institución
# ─────────────────────────────────────────────
@router.get(
    "/anomalies/institutions",
    response_model=ResponseDTO[dict],
    summary="Detección de instituciones con puntajes atípicos (Isolation Forest)",
)
async def anomalies_institutions(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    contamination: float = 0.1,
    limit: int = 200,
    _: User = _AUTH,
    ml_repo: MongoMLRepository = Depends(get_ml_repo),
):
    records = await ml_repo.get_institution_scores_for_clustering(
        periodo, departamento, limit
    )
    data = detect_anomalies(records, entity_key="institucion", contamination=contamination)
    return ResponseDTO(status_code=200, message="OK", data=data)


# ─────────────────────────────────────────────
# 8. RESUMEN EJECUTIVO — Estado del negocio
# ─────────────────────────────────────────────
@router.get(
    "/business-summary",
    response_model=ResponseDTO[dict],
    summary="Resumen ejecutivo del estado actual del sistema educativo",
)
async def business_summary(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    _: User = _AUTH,
    analytics_repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    """
    Consolida KPIs actuales, tendencias históricas y alertas automáticas
    en un resumen ejecutivo del estado del negocio educativo.
    Ideal para el panel gerencial / ejecutivo.
    """
    kpis = await analytics_repo.get_kpis(periodo, departamento, institucion)
    trends = await analytics_repo.get_trends(departamento=departamento, institucion=institucion)
    data = generate_business_summary(kpis, trends)
    return ResponseDTO(status_code=200, message="OK", data=data)
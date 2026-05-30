"""
ml_response_dto.py
Data Transfer Objects para las respuestas del módulo de Machine Learning.
"""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel


class ClusterItemDTO(BaseModel):
    cluster_id: int
    cluster_label: str
    avg_global: Optional[float] = None
    avg_razonamiento: Optional[float] = None
    avg_lectura_critica: Optional[float] = None
    avg_ingles: Optional[float] = None
    total: Optional[int] = None


class PredictionDTO(BaseModel):
    periodos_predichos: list[str]
    metricas: dict[str, list[Optional[float]]]
    r2_scores: dict[str, Optional[float]]
    historico: list[dict]


class CorrelacionItemDTO(BaseModel):
    variable: str
    correlacion: Optional[float]
    correlacion_abs: Optional[float]


class FeatureImportanceDTO(BaseModel):
    target: str
    features: list[dict[str, Any]]
    r2_train: Optional[float]


class AnomalyDTO(BaseModel):
    total: int
    total_anomalos: int
    entity_key: str
    anomalos: list[dict]
    normales: list[dict]


class BusinessSummaryDTO(BaseModel):
    kpis: dict[str, Optional[float]]
    tendencia: dict[str, Any]
    alertas: list[dict[str, str]]
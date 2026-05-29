"""
mongo_ml_repository.py
Repositorio de datos crudos para alimentar los modelos de ML.
Obtiene muestras representativas del dataset para entrenamiento.
"""
from __future__ import annotations

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from infrastructure.config.settings import settings


class MongoMLRepository:
    """Repositorio especializado en extraer muestras para análisis ML."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db[settings.ANALYTICS_COLLECTION]

    # ─────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────
    def _base_match(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
    ) -> dict:
        match: dict = {}
        if periodo:
            match["periodo"] = periodo
        if departamento:
            match["estu_inst_departamento"] = departamento
        if institucion:
            match["inst_nombre_institucion"] = institucion
        return match

    async def _run(self, pipeline: list) -> list:
        cursor = self._col.aggregate(pipeline)
        return [doc async for doc in cursor]

    # ─────────────────────────────────────────────
    # Datos para clustering de instituciones
    # ─────────────────────────────────────────────
    async def get_institution_scores_for_clustering(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        limit: int = 200,
    ) -> list:
        """Retorna promedios por institución para clustering K-Means."""
        match = self._base_match(periodo, departamento)
        pipeline = [
            {"$match": match},
            {
                "$group": {
                    "_id": {
                        "inst": "$inst_nombre_institucion",
                        "dept": "$estu_inst_departamento",
                        "origen": "$inst_origen",
                    },
                    "avg_razonamiento": {"$avg": "$mod_razona_cuantitat_punt"},
                    "avg_lectura_critica": {"$avg": "$mod_lectura_critica_punt"},
                    "avg_ingles": {"$avg": "$mod_ingles_punt"},
                    "avg_escritura": {"$avg": "$mod_comuni_escrita_punt"},
                    "avg_ciudadanas": {"$avg": "$mod_competen_ciudada_punt"},
                    "avg_global": {
                        "$avg": {
                            "$avg": [
                                "$mod_razona_cuantitat_punt",
                                "$mod_lectura_critica_punt",
                                "$mod_ingles_punt",
                            ]
                        }
                    },
                    "total": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "institucion": "$_id.inst",
                    "departamento": "$_id.dept",
                    "tipo": "$_id.origen",
                    "avg_razonamiento": 1,
                    "avg_lectura_critica": 1,
                    "avg_ingles": 1,
                    "avg_escritura": 1,
                    "avg_ciudadanas": 1,
                    "avg_global": 1,
                    "total": 1,
                }
            },
            {"$sort": {"total": -1}},
            {"$limit": limit},
        ]
        return await self._run(pipeline)

    # ─────────────────────────────────────────────
    # Datos socioeconómicos para feature importance
    # ─────────────────────────────────────────────
    async def get_socioeconomic_sample(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        sample_size: int = 5000,
    ) -> list:
        """
        Extrae muestra de estudiantes con variables socioeconómicas
        y puntajes para análisis de correlación y feature importance.
        """
        match = self._base_match(periodo, departamento)
        pipeline = [
            {"$match": match},
            {"$sample": {"size": sample_size}},
            {
                "$project": {
                    "_id": 0,
                    # Puntajes
                    "avg_razonamiento": "$mod_razona_cuantitat_punt",
                    "avg_lectura_critica": "$mod_lectura_critica_punt",
                    "avg_ingles": "$mod_ingles_punt",
                    "avg_escritura": "$mod_comuni_escrita_punt",
                    "avg_ciudadanas": "$mod_competen_ciudada_punt",
                    # Socioeconómico
                    "estrato": "$fami_estratovivienda",
                    "tiene_internet": "$fami_tieneinternet",
                    "tiene_computador": "$fami_tienecomputador",
                    "educacion_padre": "$fami_educacionpadre",
                    "educacion_madre": "$fami_educacionmadre",
                    # Personal
                    "genero": "$estu_genero",
                    "horas_trabajo": "$estu_horassemanatrabaja",
                    # Institucional
                    "tipo_institucion": "$inst_origen",
                    "departamento": "$estu_inst_departamento",
                    "periodo": 1,
                }
            },
        ]
        return await self._run(pipeline)

    # ─────────────────────────────────────────────
    # Datos para detección de anomalías
    # ─────────────────────────────────────────────
    async def get_department_scores_for_anomaly(
        self,
        periodo: Optional[str] = None,
    ) -> list:
        """Retorna promedios por departamento para detectar anomalías."""
        match = self._base_match(periodo)
        pipeline = [
            {"$match": match},
            {
                "$group": {
                    "_id": "$estu_inst_departamento",
                    "avg_razonamiento": {"$avg": "$mod_razona_cuantitat_punt"},
                    "avg_lectura_critica": {"$avg": "$mod_lectura_critica_punt"},
                    "avg_ingles": {"$avg": "$mod_ingles_punt"},
                    "avg_global": {
                        "$avg": {
                            "$avg": [
                                "$mod_razona_cuantitat_punt",
                                "$mod_lectura_critica_punt",
                                "$mod_ingles_punt",
                            ]
                        }
                    },
                    "total": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "departamento": "$_id",
                    "avg_razonamiento": 1,
                    "avg_lectura_critica": 1,
                    "avg_ingles": 1,
                    "avg_global": 1,
                    "total": 1,
                }
            },
        ]
        return await self._run(pipeline)
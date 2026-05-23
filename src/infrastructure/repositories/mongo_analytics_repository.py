from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from infrastructure.config.settings import settings


class MongoAnalyticsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db[settings.ANALYTICS_COLLECTION]

    def _build_match(
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

    def _score_group(self) -> dict:
        return {
            "avg_razonamiento": {"$avg": "$mod_razona_cuantitat_punt"},
            "avg_lectura_critica": {"$avg": "$mod_lectura_critica_punt"},
            "avg_ingles": {"$avg": "$mod_ingles_punt"},
            "avg_escritura": {"$avg": "$mod_comuni_escrita_punt"},
            "avg_ciudadanas": {"$avg": "$mod_competen_ciudada_punt"},
            "total": {"$sum": 1},
        }

    def _add_global(self) -> dict:
        return {
            "$addFields": {
                "avg_global": {
                    "$avg": ["$avg_razonamiento", "$avg_lectura_critica", "$avg_ingles"]
                }
            }
        }

    async def _run(self, pipeline: list) -> list:
        cursor = self._col.aggregate(pipeline)
        return [doc async for doc in cursor]

    async def get_kpis(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
    ) -> dict:
        match = self._build_match(periodo, departamento, institucion)
        pipeline = [
            {"$match": match},
            {"$group": {"_id": None, **self._score_group()}},
            self._add_global(),
            {"$project": {"_id": 0}},
        ]
        results = await self._run(pipeline)
        return results[0] if results else {}

    async def get_trends(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
    ) -> list:
        match = self._build_match(periodo, departamento, institucion)
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$periodo", **self._score_group()}},
            self._add_global(),
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "periodo": "$_id",
                    "avg_razonamiento": 1,
                    "avg_lectura_critica": 1,
                    "avg_ingles": 1,
                    "avg_global": 1,
                    "total": 1,
                }
            },
        ]
        return await self._run(pipeline)

    async def get_by_department(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
        limit: int = 50,
    ) -> list:
        match = self._build_match(periodo, departamento, institucion)
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$estu_inst_departamento", **self._score_group()}},
            self._add_global(),
            {"$sort": {"avg_global": -1}},
            {"$limit": limit},
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

    async def get_by_municipality(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
        limit: int = 50,
    ) -> list:
        match = self._build_match(periodo, departamento, institucion)
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$estu_inst_municipio", **self._score_group()}},
            self._add_global(),
            {"$sort": {"avg_global": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "municipio": "$_id",
                    "avg_razonamiento": 1,
                    "avg_lectura_critica": 1,
                    "avg_ingles": 1,
                    "avg_global": 1,
                    "total": 1,
                }
            },
        ]
        return await self._run(pipeline)

    async def get_by_institution(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
        limit: int = 50,
        tipo: Optional[str] = None,
    ) -> list:
        match = self._build_match(periodo, departamento, institucion)
        if tipo == "oficial":
            match["inst_origen"] = {"$regex": "^OFICIAL", "$options": "i"}
        elif tipo == "no_oficial":
            match["inst_origen"] = {"$regex": "^NO OFICIAL", "$options": "i"}
        pipeline = [
            {"$match": match},
            {
                "$group": {
                    "_id": {
                        "inst": "$inst_nombre_institucion",
                        "origen": "$inst_origen",
                    },
                    **self._score_group(),
                }
            },
            self._add_global(),
            {"$sort": {"avg_global": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "institucion": "$_id.inst",
                    "tipo": "$_id.origen",
                    "avg_razonamiento": 1,
                    "avg_lectura_critica": 1,
                    "avg_ingles": 1,
                    "avg_global": 1,
                    "total": 1,
                }
            },
        ]
        return await self._run(pipeline)

    async def get_by_program(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
        limit: int = 50,
    ) -> list:
        match = self._build_match(periodo, departamento, institucion)
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$estu_prgm_academico", **self._score_group()}},
            self._add_global(),
            {"$sort": {"avg_global": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "programa": "$_id",
                    "avg_razonamiento": 1,
                    "avg_lectura_critica": 1,
                    "avg_ingles": 1,
                    "avg_global": 1,
                    "total": 1,
                }
            },
        ]
        return await self._run(pipeline)

    async def get_by_stratum(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
    ) -> list:
        match = self._build_match(periodo, departamento, institucion)
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$fami_estratovivienda", **self._score_group()}},
            self._add_global(),
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "estrato": "$_id",
                    "avg_razonamiento": 1,
                    "avg_lectura_critica": 1,
                    "avg_ingles": 1,
                    "avg_global": 1,
                    "total": 1,
                }
            },
        ]
        return await self._run(pipeline)

    async def get_by_father_education(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
    ) -> list:
        match = self._build_match(periodo, departamento, institucion)
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$fami_educacionpadre", **self._score_group()}},
            self._add_global(),
            {"$sort": {"avg_global": -1}},
            {
                "$project": {
                    "_id": 0,
                    "educacion_padre": "$_id",
                    "avg_razonamiento": 1,
                    "avg_lectura_critica": 1,
                    "avg_ingles": 1,
                    "avg_global": 1,
                    "total": 1,
                }
            },
        ]
        return await self._run(pipeline)

    async def get_by_mother_education(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
    ) -> list:
        match = self._build_match(periodo, departamento, institucion)
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$fami_educacionmadre", **self._score_group()}},
            self._add_global(),
            {"$sort": {"avg_global": -1}},
            {
                "$project": {
                    "_id": 0,
                    "educacion_madre": "$_id",
                    "avg_razonamiento": 1,
                    "avg_lectura_critica": 1,
                    "avg_ingles": 1,
                    "avg_global": 1,
                    "total": 1,
                }
            },
        ]
        return await self._run(pipeline)

    async def get_by_internet_access(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
    ) -> list:
        match = self._build_match(periodo, departamento, institucion)
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$fami_tieneinternet", **self._score_group()}},
            self._add_global(),
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "tiene_internet": "$_id",
                    "avg_razonamiento": 1,
                    "avg_lectura_critica": 1,
                    "avg_ingles": 1,
                    "avg_global": 1,
                    "total": 1,
                }
            },
        ]
        return await self._run(pipeline)

    async def get_by_computer_access(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
    ) -> list:
        match = self._build_match(periodo, departamento, institucion)
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$fami_tienecomputador", **self._score_group()}},
            self._add_global(),
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "tiene_computador": "$_id",
                    "avg_razonamiento": 1,
                    "avg_lectura_critica": 1,
                    "avg_ingles": 1,
                    "avg_global": 1,
                    "total": 1,
                }
            },
        ]
        return await self._run(pipeline)

    async def get_by_payment_method(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
    ) -> list:
        base_match = self._build_match(periodo, departamento, institucion)
        methods = [
            ("Beca", "estu_pagomatriculabeca"),
            ("Crédito", "estu_pagomatriculacredito"),
            ("Pago propio", "estu_pagomatriculapropio"),
            ("Padres", "estu_pagomatriculapadres"),
        ]
        results = []
        for label, field in methods:
            match = {**base_match, field: "Si"}
            pipeline = [
                {"$match": match},
                {"$group": {"_id": None, **self._score_group()}},
                self._add_global(),
                {"$project": {"_id": 0}},
            ]
            docs = await self._run(pipeline)
            if docs:
                doc = dict(docs[0])
                doc["metodo_pago"] = label
                results.append(doc)
        return results

    async def get_by_work_hours(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
    ) -> list:
        match = self._build_match(periodo, departamento, institucion)
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$estu_horassemanatrabaja", **self._score_group()}},
            self._add_global(),
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "horas_trabajo": "$_id",
                    "avg_razonamiento": 1,
                    "avg_lectura_critica": 1,
                    "avg_ingles": 1,
                    "avg_global": 1,
                    "total": 1,
                }
            },
        ]
        return await self._run(pipeline)

    async def get_by_age_groups(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
    ) -> list:
        match = self._build_match(periodo, departamento, institucion)
        now = datetime.utcnow()
        pipeline = [
            {"$match": {**match, "estu_fechanacimiento": {"$exists": True, "$nin": [None, ""]}}},
            {
                "$addFields": {
                    "birth_parsed": {
                        "$dateFromString": {
                            "dateString": "$estu_fechanacimiento",
                            "format": "%d/%m/%Y",
                            "onError": None,
                            "onNull": None,
                        }
                    }
                }
            },
            {"$match": {"birth_parsed": {"$ne": None}}},
            {
                "$addFields": {
                    "age": {
                        "$floor": {
                            "$divide": [
                                {"$subtract": [now, "$birth_parsed"]},
                                1000 * 60 * 60 * 24 * 365.25,
                            ]
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "grupo_edad": {
                        "$switch": {
                            "branches": [
                                {"case": {"$lte": ["$age", 22]}, "then": "18-22"},
                                {"case": {"$lte": ["$age", 27]}, "then": "23-27"},
                                {"case": {"$lte": ["$age", 35]}, "then": "28-35"},
                            ],
                            "default": "36+",
                        }
                    }
                }
            },
            {"$group": {"_id": "$grupo_edad", **self._score_group()}},
            self._add_global(),
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "grupo_edad": "$_id",
                    "avg_razonamiento": 1,
                    "avg_lectura_critica": 1,
                    "avg_ingles": 1,
                    "avg_global": 1,
                    "total": 1,
                }
            },
        ]
        return await self._run(pipeline)

    async def get_by_gender(
        self,
        periodo: Optional[str] = None,
        departamento: Optional[str] = None,
        institucion: Optional[str] = None,
    ) -> list:
        match = self._build_match(periodo, departamento, institucion)
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$estu_genero", **self._score_group()}},
            self._add_global(),
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "genero": "$_id",
                    "avg_razonamiento": 1,
                    "avg_lectura_critica": 1,
                    "avg_ingles": 1,
                    "avg_global": 1,
                    "total": 1,
                }
            },
        ]
        return await self._run(pipeline)

    async def get_filter_periods(self) -> list:
        result = await self._col.distinct("periodo")
        return sorted(r for r in result if r)

    async def get_filter_departments(self) -> list:
        result = await self._col.distinct("estu_inst_departamento")
        return sorted(r for r in result if r)

    async def get_filter_institutions(self, departamento: Optional[str] = None) -> list:
        query = {"estu_inst_departamento": departamento} if departamento else {}
        result = await self._col.distinct("inst_nombre_institucion", query)
        return sorted(r for r in result if r)

from typing import Optional

from fastapi import APIRouter, Depends

from application.dtos.response_dto import ResponseDTO
from domain.entities.role import Role
from domain.entities.user import User
from infrastructure.repositories.mongo_analytics_repository import MongoAnalyticsRepository
from presentation.api.v1.dependencies import get_analytics_repo, require_roles

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

_AUTH = require_roles(Role.ANALISTA, Role.GERENTE, Role.ADMIN)


@router.get("/kpis", response_model=ResponseDTO[dict])
async def kpis(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_kpis(periodo, departamento, institucion)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/trends", response_model=ResponseDTO[list])
async def trends(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_trends(periodo, departamento, institucion)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/geo/departments", response_model=ResponseDTO[list])
async def geo_departments(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    limit: int = 50,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_by_department(periodo, departamento, institucion, limit)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/geo/municipalities", response_model=ResponseDTO[list])
async def geo_municipalities(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    limit: int = 50,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_by_municipality(periodo, departamento, institucion, limit)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/institutions", response_model=ResponseDTO[list])
async def institutions(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    limit: int = 50,
    tipo: Optional[str] = None,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_by_institution(periodo, departamento, institucion, limit, tipo)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/programs", response_model=ResponseDTO[list])
async def programs(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    limit: int = 50,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_by_program(periodo, departamento, institucion, limit)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/socioeconomic/stratum", response_model=ResponseDTO[list])
async def socioeconomic_stratum(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_by_stratum(periodo, departamento, institucion)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/socioeconomic/father-education", response_model=ResponseDTO[list])
async def socioeconomic_father_education(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_by_father_education(periodo, departamento, institucion)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/socioeconomic/mother-education", response_model=ResponseDTO[list])
async def socioeconomic_mother_education(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_by_mother_education(periodo, departamento, institucion)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/socioeconomic/internet-access", response_model=ResponseDTO[list])
async def socioeconomic_internet_access(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_by_internet_access(periodo, departamento, institucion)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/socioeconomic/computer-access", response_model=ResponseDTO[list])
async def socioeconomic_computer_access(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_by_computer_access(periodo, departamento, institucion)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/economic/payment-method", response_model=ResponseDTO[list])
async def economic_payment_method(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_by_payment_method(periodo, departamento, institucion)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/personal/work-hours", response_model=ResponseDTO[list])
async def personal_work_hours(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_by_work_hours(periodo, departamento, institucion)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/personal/age-groups", response_model=ResponseDTO[list])
async def personal_age_groups(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_by_age_groups(periodo, departamento, institucion)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/personal/gender", response_model=ResponseDTO[list])
async def personal_gender(
    periodo: Optional[str] = None,
    departamento: Optional[str] = None,
    institucion: Optional[str] = None,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_by_gender(periodo, departamento, institucion)
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/filters/periods", response_model=ResponseDTO[list])
async def filter_periods(
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_filter_periods()
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/filters/departments", response_model=ResponseDTO[list])
async def filter_departments(
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_filter_departments()
    return ResponseDTO(status_code=200, message="OK", data=data)


@router.get("/filters/institutions", response_model=ResponseDTO[list])
async def filter_institutions(
    departamento: Optional[str] = None,
    _: User = _AUTH,
    repo: MongoAnalyticsRepository = Depends(get_analytics_repo),
):
    data = await repo.get_filter_institutions(departamento)
    return ResponseDTO(status_code=200, message="OK", data=data)

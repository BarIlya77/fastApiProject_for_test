from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import aliased, selectinload
from .models import Organization as OrganizationModel, Building as BuildingModel, Activity as ActivityModel, Phone
from .schemas import Organization as OrganizationSchema, Building as BuildingSchema, Activity as ActivitySchema
from .database import async_session
from geopy.distance import geodesic
from typing import List

router = APIRouter()


async def get_db():
    async with async_session() as session:
        yield session


@router.get(
    "/organizations/",
    response_model=List[OrganizationSchema],
    summary="Получить список всех организаций",
    description="Возвращает полный список организаций с их зданиями, телефонами и видами деятельности",
    response_description="Список организаций"
)
async def get_organizations(db: AsyncSession = Depends(get_db)) -> List[OrganizationSchema]:
    result = await db.execute(
        select(OrganizationModel)
        .options(
            selectinload(OrganizationModel.building),
            selectinload(OrganizationModel.phones),
            selectinload(OrganizationModel.activities)
        )
    )
    return [OrganizationSchema.model_validate(org) for org in result.scalars().all()]


@router.get(
    "/organizations/{org_id}",
    response_model=OrganizationSchema,
    summary="Получить организацию по ID",
    description="Возвращает полную информацию об организации по её идентификатору",
    response_description="Данные организации",
    responses={404: {"description": "Организация не найдена"}}
)
async def get_organization(
    org_id: int,
    db: AsyncSession = Depends(get_db)
) -> OrganizationSchema:
    result = await db.execute(
        select(OrganizationModel)
        .where(OrganizationModel.id == org_id)
        .options(
            selectinload(OrganizationModel.building),
            selectinload(OrganizationModel.phones),
            selectinload(OrganizationModel.activities)
        )
    )
    org = result.scalars().first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrganizationSchema.model_validate(org)


@router.get(
    "/buildings/{building_id}/organizations/",
    response_model=List[OrganizationSchema],
    summary="Организации в здании",
    description="Возвращает организации, находящиеся в указанном здании",
    response_description="Список организаций"
)
async def get_orgs_by_building(
    building_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[OrganizationSchema]:
    result = await db.execute(
        select(OrganizationModel)
        .where(OrganizationModel.building_id == building_id)
        .options(
            selectinload(OrganizationModel.building),
            selectinload(OrganizationModel.phones),
            selectinload(OrganizationModel.activities)
        )
    )
    return [OrganizationSchema.model_validate(org) for org in result.scalars().all()]


@router.get(
    "/activities/{activity_id}/organizations/",
    response_model=List[OrganizationSchema],
    summary="Организации по виду деятельности",
    description="Возвращает организации, связанные с указанным видом деятельности",
    response_description="Список организаций"
)
async def get_orgs_by_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[OrganizationSchema]:
    result = await db.execute(
        select(OrganizationModel)
        .join(OrganizationModel.activities)
        .where(ActivityModel.id == activity_id)
        .options(
            selectinload(OrganizationModel.building),
            selectinload(OrganizationModel.phones),
            selectinload(OrganizationModel.activities)
        )
    )
    return [OrganizationSchema.model_validate(org) for org in result.scalars().all()]


@router.get(
    "/buildings/nearby/",
    response_model=List[BuildingSchema],
    summary="Поиск зданий в радиусе",
    description="Возвращает здания, находящиеся в указанном радиусе от точки",
    response_description="Список зданий"
)
async def get_buildings_nearby(
    lat: float = Query(..., description="Широта центра поиска"),
    lon: float = Query(..., description="Долгота центра поиска"),
    radius_km: float = Query(5.0, description="Радиус поиска в километрах"),
    db: AsyncSession = Depends(get_db)
) -> List[BuildingSchema]:
    buildings = (await db.execute(select(BuildingModel))).scalars().all()
    nearby = [
        BuildingSchema.model_validate(b)
        for b in buildings
        if geodesic((lat, lon), (b.latitude, b.longitude)).km <= radius_km
    ]
    return nearby


@router.get(
    "/organizations/by-activity-tree/{activity_id}",
    response_model=List[OrganizationSchema],
    summary="Организации по дереву видов деятельности",
    description="Возвращает организации, связанные с указанным видом деятельности и его подкатегориями",
    response_description="Список организаций"
)
async def get_orgs_by_activity_tree(
    activity_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[OrganizationSchema]:
    ActivityAlias = aliased(ActivityModel)
    subquery = (
        select(ActivityAlias.id)
        .where(ActivityAlias.id == activity_id)
        .cte(recursive=True)
    )
    subquery = subquery.union_all(
        select(ActivityModel.id)
        .join(subquery, ActivityModel.parent_id == subquery.c.id)
    )
    result = await db.execute(
        select(OrganizationModel)
        .join(OrganizationModel.activities)
        .where(ActivityModel.id.in_(select(subquery.c.id)))
        .options(
            selectinload(OrganizationModel.building),
            selectinload(OrganizationModel.phones),
            selectinload(OrganizationModel.activities)

        )
    )
    return [OrganizationSchema.model_validate(org) for org in result.scalars().all()]


@router.get(
    "/organizations/search/",
    response_model=List[OrganizationSchema],
    summary="Поиск организаций по названию",
    description="Возвращает организации, в названии которых содержится указанная строка",
    response_description="Список организаций"
)
async def search_organizations(
    name: str = Query(..., description="Строка для поиска в названии"),
    db: AsyncSession = Depends(get_db)
) -> List[OrganizationSchema]:
    result = await db.execute(
        select(OrganizationModel)
        .where(OrganizationModel.name.ilike(f"%{name}%"))
        .options(
            selectinload(OrganizationModel.building),
            selectinload(OrganizationModel.phones),
            selectinload(OrganizationModel.activities)
        )
    )
    return [OrganizationSchema.model_validate(org) for org in result.scalars().all()]

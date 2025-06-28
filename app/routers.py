from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import aliased, selectinload
from .models import Organization as OrganizationModel, Building as BuildingModel, Activity as ActivityModel, Phone
from .schemas import Organization as OrganizationSchema, Building, Activity
from .database import async_session
from geopy.distance import geodesic

router = APIRouter()


async def get_db():
    async with async_session() as session:
        yield session


@router.get("/organizations/")
async def get_organizations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(OrganizationModel)
        .options(
            selectinload(OrganizationModel.building),
            selectinload(OrganizationModel.phones),
            selectinload(OrganizationModel.activities)
        )
    )
    orgs = result.scalars().all()
    return [OrganizationSchema.model_validate(org) for org in orgs]


@router.get("/organizations/{org_id}") #, response_model=OrganizationSchema)
async def get_organization(
        org_id: int,
        db: AsyncSession = Depends(get_db)
):
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

    return org


@router.get("/buildings/{building_id}/organizations/")#, response_model=list[OrganizationSchema])
async def get_orgs_by_building(building_id: int, db: AsyncSession = Depends(get_db)):
    orgs = await db.execute(select(OrganizationModel).where(OrganizationModel.building_id == building_id))
    return orgs.scalars().all()


@router.get("/activities/{activity_id}/organizations/")#, response_model=list[OrganizationSchema])
async def get_orgs_by_activity(activity_id: int, db: AsyncSession = Depends(get_db)):
    orgs = await db.execute(select(OrganizationModel).join(OrganizationModel.activities).where(ActivityModel.id == activity_id))
    return orgs.scalars().all()


@router.get("/buildings/nearby/") #, response_model=list[Building])
async def get_buildings_nearby(lat: float, lon: float, radius_km: float = 5.0, db: AsyncSession = Depends(get_db)):
    buildings = (await db.execute(select(BuildingModel))).scalars().all()
    nearby = [b for b in buildings if geodesic((lat, lon), (b.latitude, b.longitude)).km <= radius_km]
    return nearby


@router.get("/organizations/by-activity-tree/{activity_id}") #, response_model=list[OrganizationSchema])
async def get_orgs_by_activity_tree(activity_id: int, db: AsyncSession = Depends(get_db)):
    ActivityAlias = aliased(ActivityModel)
    subquery = select(ActivityAlias.id).where(ActivityAlias.id == activity_id).cte(recursive=True)
    subquery = subquery.union_all(select(ActivityModel.id).join(subquery, ActivityModel.parent_id == subquery.c.id))
    orgs = await db.execute(select(OrganizationModel).join(OrganizationModel.activities).where(ActivityModel.id.in_(select(subquery.c.id))))
    return orgs.scalars().all()


@router.get("/organizations/search/") #, response_model=list[OrganizationSchema])
async def search_organizations(name: str, db: AsyncSession = Depends(get_db)):
    orgs = await db.execute(select(OrganizationModel).where(OrganizationModel.name.ilike(f"%{name}%")))
    return orgs.scalars().all()

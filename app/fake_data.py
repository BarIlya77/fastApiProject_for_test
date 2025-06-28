from faker import Faker
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Activity, Building, Organization, Phone, organization_activity
import random

fake = Faker("ru_RU")


async def create_fake_activities(db: AsyncSession):
    activities = [
        {"id": 1, "name": "Еда", "parent_id": None},
        {"id": 2, "name": "Мясная продукция", "parent_id": 1},
        {"id": 3, "name": "Молочная продукция", "parent_id": 1},
        {"id": 4, "name": "Автомобили", "parent_id": None},
        {"id": 5, "name": "Грузовые", "parent_id": 4},
        {"id": 6, "name": "Легковые", "parent_id": 4},
        {"id": 7, "name": "Запчасти", "parent_id": 6},
        {"id": 8, "name": "Аксессуары", "parent_id": 6},
    ]
    for activity in activities:
        db.add(Activity(**activity))
    await db.commit()


async def create_fake_buildings(db: AsyncSession, count: int = 5):
    for _ in range(count):
        db.add(Building(
            address=fake.address(),
            latitude=float(fake.latitude()),
            longitude=float(fake.longitude()),
        ))
    await db.commit()


async def create_fake_organizations(db: AsyncSession, count: int = 10):
    buildings = (await db.execute(select(Building))).scalars().all()
    activities = (await db.execute(select(Activity))).scalars().all()

    for _ in range(count):
        org = Organization(
            name=fake.company(),
            building_id=random.choice(buildings).id,
        )
        db.add(org)
        await db.flush()

        for _ in range(random.randint(1, 3)):
            db.add(Phone(
                number=fake.phone_number(),
                organization_id=org.id,
            ))

        selected_activities = random.sample(activities, min(random.randint(1, 3), len(activities)))
        for activity in selected_activities:
            stmt = insert(organization_activity).values(
                organization_id=org.id,
                activity_id=activity.id
            )
            await db.execute(stmt)

    await db.commit()


async def init_fake_data(db: AsyncSession):
    if not (await db.execute(select(Activity))).scalars().first():
        await create_fake_activities(db)
        await create_fake_buildings(db)
        await create_fake_organizations(db)

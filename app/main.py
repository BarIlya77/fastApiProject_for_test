from fastapi import FastAPI
from .routers import router
from .database import async_session, engine, Base
from .fake_data import init_fake_data

app = FastAPI()

app.include_router(router)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        await init_fake_data(db)


@app.get("/")
async def root():
    return {"message": "FastAPI Organizations API"}

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.checker import checker_loop
from app.config import settings
from app.db import SessionLocal, engine
from app.models import Base, User
from app.routes import admin
from app.security import hash_password


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # 1. Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Seed Admin User
    async with SessionLocal() as session:
        stmt = select(User).where(User.email == settings.admin_email)
        user = await session.scalar(stmt)
        if not user:
            new_user = User(
                email=settings.admin_email,
                password_hash=hash_password(settings.admin_password),
            )
            session.add(new_user)
            await session.commit()

    # 3. Start the background checker task
    checker_task = asyncio.create_task(checker_loop())

    yield

    # 4. Shut down gracefully
    checker_task.cancel()
    try:
        await checker_task
    except asyncio.CancelledError:
        pass
    await engine.dispose()


app = FastAPI(title="StatusWatch", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(admin.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

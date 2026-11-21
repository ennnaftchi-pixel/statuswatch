import asyncio

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Service


async def seed_data():
    async with SessionLocal() as session:
        # Check if we already have services to avoid duplicates
        stmt = select(Service)
        existing = (await session.scalars(stmt)).first()
        if existing:
            print("Database already has services. Skipping seed.")
            return

        print("Seeding database with demo services...")
        services = [
            Service(name="ISI Main Website", url="https://isi.rnu.tn", is_public=True),
            Service(name="Google Public DNS", url="https://8.8.8.8", is_public=True, expected_status=200),
            Service(name="GitHub", url="https://github.com", is_public=True),
            Service(name="Internal Club API (Private)", url="https://api.example.com", is_public=False),
        ]
        
        session.add_all(services)
        await session.commit()
        print("Successfully added 4 services!")

if __name__ == "__main__":
    asyncio.run(seed_data())

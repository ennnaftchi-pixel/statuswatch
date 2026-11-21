import asyncio

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Service


async def seed_data():
    async with SessionLocal() as session:
        # Check if we already have services to avoid duplicates
        existing = (await session.scalars(select(Service))).first()
        if existing:
            print("Database already has services. Skipping seed.")
            return

        print("Seeding database with demo services...")
        services = [
            Service(name="ISI Main Website", url="https://isi.rnu.tn", is_public=True),
            Service(name="Google Public DNS", url="https://dns.google", is_public=True),
            Service(name="GitHub", url="https://github.com", is_public=True),
            # Always fails (.invalid never resolves): shows an outage in the demo
            Service(
                name="Demo Outage (simulated)",
                url="https://demo-outage.invalid",
                is_public=True,
            ),
            Service(
                name="Internal Club API (Private)",
                url="https://api.example.com",
                is_public=False,
            ),
        ]

        session.add_all(services)
        await session.commit()
        print(f"Successfully added {len(services)} services!")


if __name__ == "__main__":
    asyncio.run(seed_data())

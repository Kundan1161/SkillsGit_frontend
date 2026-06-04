import asyncio
from sqlalchemy import text
from src.core.db import SessionLocal

async def main():
    categories = [
        ("robotics", "Robotics", "Robotics and hardware automation playbooks.", 130),
        ("biotech", "Biotech", "Biology and biotechnology workflows.", 140)
    ]
    async with SessionLocal() as session:
        for slug, name, desc, order in categories:
            await session.execute(
                text(
                    "INSERT INTO categories (slug, name, description, display_order) "
                    "VALUES (:slug, :name, :desc, :order) "
                    "ON CONFLICT (slug) DO NOTHING;"
                ),
                {"slug": slug, "name": name, "desc": desc, "order": order}
            )
        await session.commit()
        print("Missing categories seeded successfully!")

if __name__ == "__main__":
    asyncio.run(main())

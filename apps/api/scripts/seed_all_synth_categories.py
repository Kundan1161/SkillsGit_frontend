import asyncio
from pathlib import Path
from sqlalchemy import text
from src.core.db import SessionLocal
from src.skills.parser import split_frontmatter

SYNTH_DIR = Path(__file__).parent / "seed_data" / "synth"

async def main():
    if not SYNTH_DIR.exists():
        print(f"Synth directory {SYNTH_DIR} does not exist.")
        return

    candidates = sorted(
        p
        for p in SYNTH_DIR.glob("*.skills.md")
        if not p.name.startswith("_report_")
    )
    
    unique_categories = set()
    for file_path in candidates:
        try:
            raw = file_path.read_bytes()
            fm, _ = split_frontmatter(raw)
            cat = fm.get("category")
            if cat:
                unique_categories.add(str(cat))
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")

    print(f"Found unique categories in synth files: {unique_categories}")

    async with SessionLocal() as session:
        for cat in unique_categories:
            # Generate a nice name
            name = cat.replace("-", " ").title()
            desc = f"{name} related skills and playbooks."
            
            await session.execute(
                text(
                    "INSERT INTO categories (slug, name, description, display_order) "
                    "VALUES (:slug, :name, :desc, 150) "
                    "ON CONFLICT (slug) DO NOTHING;"
                ),
                {"slug": cat, "name": name, "desc": desc}
            )
        await session.commit()
    print("All required categories have been successfully seeded!")

if __name__ == "__main__":
    asyncio.run(main())

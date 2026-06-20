import asyncio, asyncpg, os

async def main():
    dsn = os.environ["DATABASE_URL"]
    conn = await asyncpg.connect(dsn)
    
    # List failed docs
    rows = await conn.fetch(
        "SELECT id, filename, status FROM knowledge_documents WHERE status='failed'"
    )
    print(f"Failed docs: {len(rows)}")
    for r in rows:
        print(f"  {r['id']} - {r['filename']} ({r['status']})")
    
    # Delete failed docs
    result = await conn.execute(
        "DELETE FROM knowledge_documents WHERE status='failed'"
    )
    print(f"Deleted: {result}")
    
    await conn.close()

asyncio.run(main())

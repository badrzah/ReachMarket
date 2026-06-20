import asyncio, asyncpg, os, sys

async def main():
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("No DATABASE_URL in env")
        sys.exit(1)
    
    # Use SSH tunnel host if provided
    host = os.environ.get("PGHOST", "localhost")
    port = int(os.environ.get("PGPORT", "5432"))
    
    print(f"Connecting via {host}:{port}...")
    conn = await asyncpg.connect(dsn.replace("postgres.railway.internal", host).replace(":5432", f":{port}"))
    
    rows = await conn.fetch("SELECT id, filename, status FROM knowledge_documents WHERE status='failed'")
    print(f"Found {len(rows)} failed docs")
    for r in rows:
        print(f"  {r['id']} - {r['filename']}")
    
    result = await conn.execute("DELETE FROM knowledge_documents WHERE status='failed'")
    print(f"Deleted: {result}")
    await conn.close()

asyncio.run(main())

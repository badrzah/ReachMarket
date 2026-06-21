import asyncio, asyncpg, os

async def main():
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("No DATABASE_URL")
        return
    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute("""
            INSERT INTO companies (id, name) 
            VALUES ('00000000-0000-0000-0000-000000000001', 'Demo Company')
            ON CONFLICT (id) DO NOTHING
        """)
        await conn.execute("""
            INSERT INTO users (id, company_id, email, hashed_password, role)
            VALUES ('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'demo@demo.com', 'does-not-matter', 'owner')
            ON CONFLICT (id) DO NOTHING
        """)
        print("Demo company and user inserted successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

asyncio.run(main())

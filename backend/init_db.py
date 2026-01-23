"""
Database initialization script.

This script creates all database tables defined in models.
Use this before Alembic migrations are implemented.

Usage:
    python init_db.py
"""
import asyncio

from app.database import Base, create_tables, engine
from app.models import AuditLog, Contact, ContactPhone, Phone, User


async def init_database():
    """
    Create all database tables.
    
    Warning: This will not create tables if they already exist.
    Use Alembic for production migrations.
    """
    print("🔧 Initializing database...")
    print(f"📊 Creating tables for models: User, Contact, Phone, ContactPhone, AuditLog")
    
    try:
        await create_tables()
        print("✅ Database tables created successfully!")
        
        # Verify tables
        async with engine.begin() as conn:
            from sqlalchemy import text
            
            result = await conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            )
            tables = [row[0] for row in result]
            
            print(f"\n📋 Created tables:")
            for table in sorted(tables):
                print(f"   - {table}")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise


async def main():
    await init_database()


if __name__ == "__main__":
    asyncio.run(main())

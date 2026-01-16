#!/usr/bin/env python3
"""
Script to test database connection to Supabase
"""
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def test_connection():
    """Test database connection"""
    try:
        print("🔍 Testing database connection...")
        print(f"📊 Database URL: {settings.DATABASE_URL[:50]}...")  # Show first 50 chars
        
        # Create engine
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            echo=False
        )
        
        # Test connection
        with engine.connect() as connection:
            # Execute a simple query
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"📦 PostgreSQL version: {version}")
            
            # Test if we can query
            result = connection.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"🗄️  Connected to database: {db_name}")
            
            # Check if tables exist
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"📋 Found {len(tables)} tables:")
                for table in tables[:10]:  # Show first 10
                    print(f"   - {table}")
                if len(tables) > 10:
                    print(f"   ... and {len(tables) - 10} more")
            else:
                print("⚠️  No tables found. You may need to run migrations.")
            
            return True
            
    except Exception as e:
        print(f"❌ Connection failed!")
        print(f"Error: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("1. Check if DATABASE_URL is set correctly in .env file")
        print("2. Verify Supabase database is accessible")
        print("3. Check network/firewall settings")
        print("4. Ensure password is correct in connection string")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)


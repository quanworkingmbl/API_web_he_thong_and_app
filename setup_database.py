#!/usr/bin/env python3
"""
Script to setup database: create tables and initial data
"""
import sys
from sqlalchemy import create_engine, text
from app.core.database import Base, engine
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import *  # Import all models

def create_tables():
    """Create all tables"""
    try:
        print("🔨 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {str(e)}")
        return False

def create_admin_user():
    """Create initial admin user"""
    try:
        from app.core.database import SessionLocal
        from app.models.user import User
        
        db = SessionLocal()
        
        # Check if admin already exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if admin:
            print("ℹ️  Admin user already exists")
            db.close()
            return True
        
        # Create admin user
        admin = User(
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            name="Admin User",
            type="admin",
            activated=1,
            created_by="system"
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("✅ Admin user created successfully!")
        print(f"   Email: admin@example.com")
        print(f"   Password: admin123")
        print("   ⚠️  Please change the password after first login!")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Failed to create admin user: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("=" * 50)
    print("🚀 Database Setup Script")
    print("=" * 50)
    
    # Test connection first
    from test_db_connection import test_connection
    if not test_connection():
        print("\n❌ Cannot proceed without database connection")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Create tables
    if not create_tables():
        print("\n❌ Setup failed")
        sys.exit(1)
    
    # Create admin user
    print("\n" + "=" * 50)
    create_admin_user()
    
    print("\n" + "=" * 50)
    print("✅ Database setup completed!")
    print("=" * 50)
    print("\n💡 Next steps:")
    print("1. Run migrations: alembic upgrade head")
    print("2. Start the API: uvicorn app.main:app --reload")
    print("3. Test login with admin credentials")

if __name__ == "__main__":
    main()


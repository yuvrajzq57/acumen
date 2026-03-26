import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.customer import Base

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/customer_db")

# SQLAlchemy Setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL - Railway will provide DATABASE_URL, fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./academic_events.db")

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Event Model
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)  # Our custom event ID
    name = Column(String, index=True)
    description = Column(Text)
    start_date = Column(String, index=True)
    end_date = Column(String)
    source = Column(String, index=True)
    source_group = Column(String, index=True)
    source_url = Column(String)
    source_name = Column(String)
    venue_name = Column(String)
    venue_type = Column(String)
    is_academic = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

# Create tables
Base.metadata.create_all(bind=engine)


import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from the project root .env file
load_dotenv()

# Read PostgreSQL connection URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is missing. Configure it in your .env file."
    )

# Create SQLAlchemy database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=15,
    max_overflow=5,
    pool_timeout=30,
    connect_args={"application_name": "ai-task-api-test"},
)
# Create database session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for future SQLAlchemy database models
Base = declarative_base()


# FastAPI database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

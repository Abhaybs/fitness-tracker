from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Replace with your actual PostgreSQL credentials
# Format: postgresql://user:password@host:port/database_name
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost:5432/fitness"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    import models  # ensure models are registered before table creation
    Base.metadata.create_all(bind=engine)

# Dependency to get the database session in our API routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
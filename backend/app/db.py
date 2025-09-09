from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from common.config import settings
class Base(DeclarativeBase): pass
DATABASE_URL = f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

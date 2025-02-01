from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import os

# Use naming convention for constraints to help with migrations
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

# Async engine for better performance
engine = create_async_engine(
    os.getenv("DATABASE_URL"),
    echo=True,
    pool_pre_ping=True
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
) 
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from database.models import *

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
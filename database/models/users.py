from typing import Sequence
from sqlalchemy import Boolean, Column, Integer, String, select, BIGINT
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal, Base
from sqlalchemy.exc import SQLAlchemyError

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'anonbot'}

    id = Column(BIGINT, nullable=False, index=True, unique=True, primary_key=True, autoincrement=False)
    message_id = Column(String, nullable=False, index=True, unique=True)
    number = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    is_banned = Column(Boolean, nullable=False, default=False)
    getted_messages = Column(Integer, nullable=False, default=0)
    sended_messages = Column(Integer, nullable=False, default=0)

    async def update(self, **kwargs):
        session: AsyncSession
        async with AsyncSessionLocal() as session:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            try:
                session.add(self)
                await session.commit()
                return self
            except SQLAlchemyError as e:
                print(f"Error updating user: {e}")
                await session.rollback()

async def get_users() -> Sequence[User]:
    session: AsyncSession
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users
    
async def create_user(**kwargs):
    session: AsyncSession
    async with AsyncSessionLocal() as session:
        user = User(**kwargs)
        try:
            session.add(user)
            await session.commit()
            return user
        except SQLAlchemyError as e:
            print(f"Error creating user: {e}")
            await session.rollback()
            return None
    
async def get_user_by_id(id: int) -> User | None:
    session: AsyncSession
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalars().first()
        return user
    
async def get_user_by_message_id(message_id: str) -> User | None:
    session: AsyncSession
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.message_id == message_id))
        user = result.scalars().first()
        return user
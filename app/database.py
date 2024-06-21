from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

engine = create_async_engine(
    "sqlite+aiosqlite:///timetable.db"
)
new_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    username: Mapped[str]
    timetable_entries = relationship("Timetable", back_populates="user")

class Timetable(Base):
    __tablename__ = 'timetable'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey('users.user_id'))
    timestamp_in: Mapped[datetime] = Column(DateTime)
    timestamp_out: Mapped[datetime] = Column(DateTime)
    breakfast: Mapped[bool] = mapped_column(default=False)
    user = relationship("UserORM", back_populates="timetable_entries")

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
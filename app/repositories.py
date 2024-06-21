from app.database import new_session, UserORM, Timetable
from sqlalchemy import select, update
from datetime import datetime, timezone, timedelta

class UserRepository:

    @classmethod
    async def add_user(cls, user_id: int, username: str):
        async with new_session() as session:

            q = select(UserORM).filter_by(user_id=user_id)
            result = await session.execute(q)
            user = result.scalars().first()
            if user:
                return
            append = UserORM(user_id=user_id, username=username)
            session.add(append)
            await session.commit()

    @classmethod
    async def add_start_time(cls, user_id: int, breakfast: bool):
        async with new_session() as session:
            check = breakfast
            # timezone
            perm_tz = timezone(timedelta(hours=5))
            current_time = datetime.now(perm_tz)

            timetable_entry = Timetable(user_id=user_id, timestamp_in=current_time, breakfast = check)
            session.add(timetable_entry)
            await session.commit()

    @classmethod
    async def add_end_time(cls, user_id: int, breakfast: bool):
        async with new_session() as session:
            # timezone
            perm_tz = timezone(timedelta(hours=5))
            current_time = datetime.now(perm_tz)

            check = breakfast

            existing_entry = await session.execute(
                select(Timetable).where(
                    Timetable.breakfast == check,
                    Timetable.user_id == user_id,
                    Timetable.timestamp_out == None
                )
            )
            existing_entry = existing_entry.scalars().first()
            if existing_entry:
                await session.execute(
                    update(Timetable).where(Timetable.user_id == user_id,  Timetable.timestamp_out == None, Timetable.breakfast == check).values(
                            timestamp_out=current_time)
                )
                await session.commit()
            else:
                print("Произошла неизвестная ошибка")

    @classmethod
    async def get_user_info_by_date(cls, date: datetime):
        current_date = date.date()
        async with new_session() as session:
            q = select(Timetable).where(
                Timetable.timestamp_in >= current_date,
                Timetable.timestamp_in < current_date + timedelta(days=1)
            )
            result = await session.execute(q)
            user = result.scalars().all()
            return user

    @classmethod
    async def check_user_info(cls, user_id: int):
        current_date = datetime.now().date()
        async with new_session() as session:
            q = select(Timetable).where(
                Timetable.user_id == user_id,
                Timetable.timestamp_in >= current_date,
                Timetable.timestamp_in < current_date + timedelta(days=1)
            )
            result = await session.execute(q)
            user = result.scalars().first()
            if user: return False
            else: return True

    @classmethod
    async def check_start_time(cls, user_id: int, breakfast: bool):
        async with new_session() as session:
            q = select(Timetable).where(
                Timetable.user_id == user_id,
                Timetable.breakfast == breakfast,
                Timetable.timestamp_out == None
            )
            result = await session.execute(q)
            user = result.scalars().first()
            if user: return True
            else: return False
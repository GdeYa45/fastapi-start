from src.schemas.hotels import Hotel
from src.models.hotels import HotelsORM
from src.repositories.base import BaseRepository
from sqlalchemy import select


class HotelsRepository(BaseRepository):
    model = HotelsORM
    schema = Hotel

    async def get_all(self, location, title, limit, offset):
        query = select(HotelsORM)
        if title:
            query = query.where(HotelsORM.title.ilike(f"%{title}%"))
        if location:
            query = query.where(HotelsORM.location.ilike(f"%{location}%"))
        query = query.limit(limit).offset(offset)
        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)

        return [
            Hotel.model_validate(hotel, from_attributes=True)
            for hotel in result.scalars().all()
        ]

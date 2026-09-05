from fastapi.exceptions import HTTPException
from fastapi import Query, APIRouter
from src.repositories.hotels import HotelsRepository
from src.database import async_session_maker
from src.schemas.hotels import HotelAdd, HotelPATCH
from src.api.dependencies import PaginationDep

router = APIRouter(prefix="/hotels", tags=["Отели"])

@router.get("")
async def get_hotels(
        pagination: PaginationDep,
        title: str | None = Query(None, description="Название отеля в базе"),
        location: str | None = Query(None, description="Локация")
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_all(
            location,
            title,
            limit=per_page or 5,
            offset=per_page * ((pagination.page or 1) - 1)
        )

@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).get_one_or_none(id=hotel_id)
    if hotel is None:
        raise HTTPException(
            status_code=404,
            detail="Отель не найден"
        )
    return hotel

@router.post("")
async def create_hotel(hotel_data: HotelAdd):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).add(hotel_data)
        await session.commit()
    return {"status" : "Ok", "data": hotel}

@router.put("/{hotel_id}", summary="Полное обновление данных")
async def full_update_hotel(
        hotel_id: int,
        hotel_data: HotelAdd
):
    async with async_session_maker() as session:
        hotel_repository = HotelsRepository(session)
        hotel = await hotel_repository.edit(hotel_data, id=hotel_id)
        if hotel is None:
            raise HTTPException(status_code=404, detail=f"Отель с id {hotel_id} не найден")
        await session.commit()
    return {"status" : "Ok", "data": hotel}

@router.patch("/{hotel_id}", summary="Частичное обновление данных")
async def partially_edit_hotel(
        hotel_id: int,
        hotel_data: HotelPATCH
):
    async with async_session_maker() as session:
        await HotelsRepository(session).edit(hotel_data, exclude_unset=True, id=hotel_id)
        await session.commit()
    return {"status" : "Ok"}

@router.delete("/{hotel_id}", summary='Удаление данных отеля')
async def delete_hotel(hotel_id: int):
    async with async_session_maker() as session:
        hotels_repository = HotelsRepository(session)
        deleted_hotel = await hotels_repository.delete(id=hotel_id)
        if deleted_hotel is None:
            raise HTTPException(status_code=404, detail=f"Отель с id {hotel_id} не найден")
        await session.commit()
    return {"status" : "Ok", "data": deleted_hotel}

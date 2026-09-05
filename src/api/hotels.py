from fastapi.exceptions import HTTPException
from fastapi import Query, Body, APIRouter
from src.repositories.hotels import HotelsRepository
from src.database import async_session_maker
from src.schemas.hotels import Hotel, HotelPATCH
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

@router.post("")
async def create_hotel(hotel_data: Hotel):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).add(hotel_data)
        await session.commit()
    return {"status" : "Ok", "data": hotel}

@router.put("/{hotel_id}", summary="Полное обновление данных")
async def full_update_hotel(
        hotel_id: int,
        hotel_data: Hotel
):
    async with async_session_maker() as session:
        hotel_repository = HotelsRepository(session)
        hotel = await hotel_repository.edit(hotel_data, id = hotel_id)
        if hotel is None:
            raise HTTPException(status_code=404, detail=f"Отель с id {hotel_id} не найден")
        await session.commit()
    return {"status" : "Ok", "data": hotel}

@router.patch("/{hotel_id}", summary="Частичное обновление данных")
def one_update_hotel(
        hotel_id: int,
        hotel_data: HotelPATCH
):
    # global hotels
    # for hotel in hotels:
    #     if hotel["id"] == hotel_id:
    #         if hotel_data.title is None and hotel_data.location is None:
    #             raise HTTPException(
    #                 status_code=400,
    #                 detail="Нельзя обновить отель, если не передано ни одного нового значения"
    #             )
    #         if hotel_data.title is not None:
    #             hotel["title"] = hotel_data.title
    #         if hotel_data.location is not None:
    #             hotel["name"] = hotel_data.location
    #         return {"message": f"Данные отеля id - {hotel_id} изменены"}
    # raise HTTPException(
    #     status_code=404,
    #     detail=f"Отель с id {hotel_id} не найден"
    # )
    pass

@router.delete("/{hotel_id}", summary='Удаление данных отеля')
async def delete_hotel(hotel_id: int):
    async with async_session_maker() as session:
        hotels_repository = HotelsRepository(session)
        deleted_hotel = await hotels_repository.delete(id = hotel_id)
        if deleted_hotel is None:
            raise HTTPException(status_code=404, detail=f"Отель с id {hotel_id} не найден")
        await session.commit()
    return {"status" : "Ok", "data": deleted_hotel}

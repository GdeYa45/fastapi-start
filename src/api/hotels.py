from fastapi import Query, Body, APIRouter, HTTPException

from fastapi.openapi.models import Example

from sqlalchemy import select, insert

from src.repositories.hotels import HotelsRepository
from src.database import async_session_maker, engine
from src.models.hotels import HotelsORM
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
            offset=per_page * (pagination.page - 1)
        )

@router.post("")
async def create_hotel(hotel_data: Hotel = Body(openapi_examples={
    "1" : Example(
        summary="Сочи",
        value={"title": "Сочи", "location": "Ул. Невского, 19А"}
    ),
    "2" : Example(
        summary="Дубай",
        value={"title": "Дубай", "location": "Ул. Мамадышская, 14"}
    )
})):
    async with async_session_maker() as session:
        add_hotel_stmt = insert(HotelsORM).values(**hotel_data.model_dump())
        print(add_hotel_stmt.compile(engine, compile_kwargs={"literal_binds" : True}))
        await session.execute(add_hotel_stmt)
        await session.commit()
    return {"message" : "OK"}

@router.put("/{hotel_id}", summary="Полное обновление данных")
def full_update_hotel(
        hotel_id: int,
        hotel_title: str = Body(),
        hotel_name: str = Body(),
):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            hotel["title"] = hotel_title
            hotel["name"] = hotel_name
            return {"message" : f"Данные отеля id - {hotel_id} изменены"}
    raise HTTPException(
        status_code=404,
        detail=f"Отель с id {hotel_id} не найден"
    )


@router.patch("/{hotel_id}", summary="Частичное обновление данных")
def one_update_hotel(
        hotel_id: int,
        hotel_data: HotelPATCH
):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            if hotel_data.title is None and hotel_data.location is None:
                raise HTTPException(
                    status_code=400,
                    detail="Нельзя обновить отель, если не передано ни одного нового значения"
                )
            if hotel_data.title is not None:
                hotel["title"] = hotel_data.title
            if hotel_data.location is not None:
                hotel["name"] = hotel_data.location
            return {"message": f"Данные отеля id - {hotel_id} изменены"}
    raise HTTPException(
        status_code=404,
        detail=f"Отель с id {hotel_id} не найден"
    )

@router.delete("/{hotel_id}")
def delete_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"status" : "OK"}
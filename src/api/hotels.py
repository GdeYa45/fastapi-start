from fastapi import Query, Body, APIRouter, HTTPException
from src.schemas.hotels import Hotel, HotelPATCH
from src.api.dependencies import PaginationDep

router = APIRouter(prefix='/hotels', tags=['Отели'])

hotels = [
    {"id": 1, "title": "Sochi", "name": "sochi"},
    {"id": 2, "title": "Дубай", "name": "dubai"},
    {"id": 3, "title": "Мальдивы", "name": "maldivi"},
    {"id": 4, "title": "Геленджик", "name": "gelendzhik"},
    {"id": 5, "title": "Москва", "name": "moscow"},
    {"id": 6, "title": "Казань", "name": "kazan"},
    {"id": 7, "title": "Санкт-Петербург", "name": "spb"},
]

@router.get('')
def get_hotels(
        pagination: PaginationDep,
        id: int | None = Query(None, description='Номер отеля в базе'),
        title: str | None = Query(None, description='Название отеля в базе')
):
    new_hotels = []
    for hotel in hotels:
        if id and hotel['id'] != id:
            continue
        if title and hotel['title'] != title:
            continue
        new_hotels.append(hotel)
    if pagination.page and pagination.per_page:
        return new_hotels[(pagination.page - 1) * pagination.per_page : (pagination.page - 1) * pagination.per_page + pagination.per_page]
    return new_hotels

@router.post('')
def create_hotel(hotel_data: Hotel):
    global hotels
    hotels.append({
        'id' : hotels[-1]['id'] + 1,
        'title' : hotel_data.title,
        'name' : hotel_data.name
    })
    return {'message' : 'OK'}

@router.put('/{hotel_id}', summary='Полное обновление данных')
def full_update_hotel(
        hotel_id: int,
        hotel_title: str = Body(),
        hotel_name: str = Body(),
):
    global hotels
    for hotel in hotels:
        if hotel['id'] == hotel_id:
            hotel['title'] = hotel_title
            hotel['name'] = hotel_name
            return {'message' : f'Данные отеля id - {hotel_id} изменены'}
    raise HTTPException(
        status_code=404,
        detail=f'Отель с id {hotel_id} не найден'
    )


@router.patch('/{hotel_id}', summary='Частичное обновление данных')
def one_update_hotel(
        hotel_id: int,
        hotel_data: HotelPATCH
):
    global hotels
    for hotel in hotels:
        if hotel['id'] == hotel_id:
            if hotel_data.title is None and hotel_data.name is None:
                raise HTTPException(
                    status_code=400,
                    detail='Нельзя обновить отель, если не передано ни одного нового значения'
                )
            if hotel_data.title is not None:
                hotel['title'] = hotel_data.title
            if hotel_data.name is not None:
                hotel['name'] = hotel_data.name
            return {'message': f'Данные отеля id - {hotel_id} изменены'}
    raise HTTPException(
        status_code=404,
        detail=f'Отель с id {hotel_id} не найден'
    )

@router.delete('/{hotel_id}')
def delete_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel['id'] != hotel_id]
    return {'status' : 'OK'}
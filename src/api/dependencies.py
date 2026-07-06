from fastapi import Depends, Query
from pydantic import BaseModel
from typing import Annotated

class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(None, ge=1, description='Номер страницы')]
    per_page: Annotated[int | None, Query(None, ge=1, lt=30, description='Сколько элементов на странице')]

PaginationDep = Annotated[PaginationParams, Depends()]
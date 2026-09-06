from fastapi.exceptions import HTTPException

from fastapi import APIRouter

from src.repositories.users import UsersRepository
from src.database import async_session_maker
from src.schemas.users import UserRequestAdd, UserAdd

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

router = APIRouter(prefix='/auth', tags=["Авторизация и аутентификация"])

@router.post("/register")
async def register_user(data: UserRequestAdd):
    async with async_session_maker() as session:
        users_repository = UsersRepository(session)
        existing_user = await users_repository.get_one_or_none(email=data.email)
        if existing_user is not None:
            raise HTTPException(status_code=409, detail="Пользователь с такой почтой уже существует")
        hashed_password = password_hash.hash(data.password)
        new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
        await users_repository.add(new_user_data)
        await session.commit()
    return {"status":"OK"}
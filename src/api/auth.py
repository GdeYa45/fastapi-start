from fastapi import APIRouter, HTTPException, Response

from src.services.auth import AuthService
from src.repositories.users import UsersRepository
from src.database import async_session_maker
from src.schemas.users import UserRequestAdd, UserAdd

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register")
async def register_user(data: UserRequestAdd):
    async with async_session_maker() as session:
        users_repository = UsersRepository(session)
        existing_user = await users_repository.get_one_or_none(email=data.email)
        if existing_user is not None:
            raise HTTPException(
                status_code=409, detail="Пользователь с такой почтой уже существует"
            )
        hashed_password = AuthService().hash_password(data.password)
        new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
        await users_repository.add(new_user_data)
        await session.commit()
    return {"status": "OK"}


@router.post("/login")
async def login_user(data: UserRequestAdd, response: Response):
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_user_with_hashed_password(
            email=data.email
        )
        if not user:
            raise HTTPException(
                status_code=401, detail="Пользователь с таким email не существует"
            )
        if not AuthService().verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Пароль неверный")
        access_token = AuthService().create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)
        return {"access_token": access_token}

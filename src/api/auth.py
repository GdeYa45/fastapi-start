from datetime import datetime, timezone, timedelta
import jwt

from fastapi import APIRouter, HTTPException, Response

from src.repositories.users import UsersRepository
from src.database import async_session_maker
from src.schemas.users import UserRequestAdd, UserAdd, UserWithHashedPassword

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

router = APIRouter(prefix='/auth', tags=["Авторизация и аутентификация"])

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

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

@router.post("/login")
async def login_user(data: UserRequestAdd, response: Response):
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_user_with_hashed_password(email=data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Пользователь с таким email не существует")
        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Пароль неверный")
        access_token = create_access_token({"user_id" : user.id})
        response.set_cookie("access_token", access_token)
        return {"access_token" : access_token}
from src.repositories.base import BaseRepository
from src.models.users import UsersORM
from src.schemas.users import User

class UsersRepository(BaseRepository):
    model = UsersORM
    schema = User
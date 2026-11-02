from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.security import decode_access_token
from app.database import get_db
from app.models import User
# from app.services.ai_client import AIClient


# OAuth2 схема: извлекает токен из заголовка Authorization: Bearer ...
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# async def get_ai_client() -> AIClient:
#     """Возвращает клиент для работы с LLM."""
#     return AIClient()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Зависимость для получения текущего пользователя.
    
    Проверяет JWT-токен и возвращает пользователя из БД.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Декодируем токен
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # 2. Извлекаем user_id из sub
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # 3. Ищем пользователя в БД
    user = await crud.get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception
    
    return user
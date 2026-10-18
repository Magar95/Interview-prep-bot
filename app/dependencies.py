from fastapi import Header, HTTPException

from app.ai_client import evaluate_answer


async def get_current_user(authorization: str = Header(None)):
    """
    Зависимость для получения текущего пользователя.
    
    Пока это заглушка: проверяем наличие заголовка Authorization.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Заглушка: возвращаем фиктивного пользователя
    return {"id": 1, "username": "demo_user"}


async def get_ai_client():
    """
    Зависимость для AI-клиента.
    
    Пока возвращает функцию-заглушку.
    """
    return evaluate_answer

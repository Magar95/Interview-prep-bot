import logging
import time

from fastapi import Request

logger = logging.getLogger("app.requests")


async def log_requests(request: Request, call_next):
    """
    Логирует каждый запрос: метод, путь, статус, время выполнения.
    """
    start_time = time.perf_counter()

    # Логируем входящий запрос
    logger.info(f"→ {request.method} {request.url.path}")
    
    # Передаём запрос дальше
    response = await call_next(request)
    
    # Считаем время
    process_time = time.perf_counter() - start_time
    process_time_ms = round(process_time * 1000, 2)
    
    # Логируем ответ
    log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
    logger.log(
        log_level,
        f"← {request.method} {request.url.path} "
        f"{response.status_code} ({process_time_ms}ms)",
    )
    
    # Добавляем заголовок с временем обработки
    response.headers["X-Process-Time"] = str(process_time_ms)
    
    return response
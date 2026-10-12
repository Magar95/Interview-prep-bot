import asyncio


async def evaluate_answer(question: str, user_answer: str) -> dict:
    """
    Отправляет ответ пользователя в LLM для оценки.

    Args:
        question: Текст вопроса
        user_answer: Ответ пользователя

    Returns:
        dict: Оценка, фидбек, сильные и слабые стороны
    """
    # Имитация задержки ответа от LLM (500 мс)
    await asyncio.sleep(0.5)

    return {
        "score": 7,
        "feedback": f"Ответ на вопрос '{question[:30]}...' принят. Оценка: 7/10",
        "strengths": ["Чёткое определение", "Пример использования"],
        "improvements": ["Можно добавить больше деталей"],
    }

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Answer, Question, User
from app.schemas import AnswerCreate, QuestionCreate

# QUESTIONS
async def get_questions(
    db: AsyncSession,
    topic: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
) -> Sequence[Question]:
    """Получить список вопросов с фильтрацией."""
    stmt = select(Question)
    if topic:
        stmt = stmt.where(Question.topic == topic)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_question(
    db: AsyncSession,
    question_id: int,
) -> Optional[Question]:
    """Получить вопрос по ID."""
    stmt = select(Question).where(Question.id == question_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_question(
    db: AsyncSession,
    question: QuestionCreate,
) -> Question:
    """Создать вопрос."""
    db_question = Question(**question.model_dump())
    db.add(db_question)
    await db.commit()
    await db.refresh(db_question)
    return db_question


async def delete_question(db: AsyncSession, question_id: int) -> bool:
    """Удалить вопрос."""
    question = await get_question(db, question_id)
    if not question:
        return False
    await db.delete(question)
    await db.commit()
    return True


# ANSWERS
async def create_answer(
    db: AsyncSession,
    answer: AnswerCreate,
    question_id: int,
    user_id: int,
    evaluation: dict,
) -> Answer:
    """Создать ответ с оценкой AI."""
    db_answer = Answer(
        question_id=question_id,
        user_id=user_id,
        text=answer.text,
        score=evaluation.get("score"),
        feedback=evaluation.get("feedback"),
    )
    db.add(db_answer)
    await db.commit()
    await db.refresh(db_answer)
    return db_answer

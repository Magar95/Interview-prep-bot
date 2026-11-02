from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Answer, Question, User
from app.schemas import AnswerCreate, QuestionCreate, UserCreate
from app.core.security import hash_password, verify_password


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


async def get_user_by_id(
    db: AsyncSession,
    id: int,
) -> User | None:
    """Найти пользователя по username."""
    stmt = select(User).filter_by(id=id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username(
    db: AsyncSession,
    username: str,
) -> User | None:
    """Найти пользователя по username."""
    stmt = select(User).filter_by(username=username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> User | None:
    """Найти пользователя по email."""
    stmt = select(User).filter_by(email=email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    user: UserCreate,
) -> User:
    """Создать пользователя с хешированным паролем."""
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str,
) -> User | None:
    """Проверить логин и пароль."""
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

import asyncio
from datetime import datetime
from typing import Optional
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_db
from app.services.ai_client import evaluate_answer
from app.dependencies import get_ai_client, get_current_user
from app.schemas import (QuestionCreate, 
                         QuestionResponse,
                         AnswerCreate, 
                         QuestionCreate,
                         QuestionResponse,
                         UserInToken,
                         EvaluationResponse,
                         UserResponse)
from app.routers.auth import router as auth_router
from app.models import User

# from app.services.ai_client import AIClient


app = FastAPI(
    title="Interview Prep Bot",
    description="AI помощник для подготовки к техническим собеседованиям",
    version="0.1.0"
)

app.include_router(auth_router)


@app.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question_endpoint(
    question_id: int,
    db: AsyncSession = Depends(get_db),
):
    question = await crud.get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@app.get("/questions", response_model=list[QuestionResponse])
async def get_questions_endpoint(
    topic: Optional[str] = None, 
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
) -> list[QuestionResponse]:
    """Получить список вопросов."""
    return await crud.get_questions(db, topic=topic, skip=skip, limit=limit)


@app.get("/questions/{question_id}/answers")
async def get_answers(question_id: int, limit: int = 5):
    return {
        'question_id': question_id,
        'limit': limit,
        'answers': []
    }


@app.post("/questions", response_model=QuestionResponse, status_code=201)
async def create_question_endpoint(
    question: QuestionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> QuestionResponse:
    """Создать вопрос. Только для авторизованных."""
    return await crud.create_question(db, question)


@app.delete('/questions/{question_id}', status_code=204)
async def delete_question(question_id: int):
    db = questions
    for q in db:
        if q['id'] == question_id:
            db.remove(q)
            return {}
    return {'error': 'Question not found'}


@app.delete("/questions/{question_id}", status_code=204)
async def delete_question_endpoint(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserInToken = Depends(get_current_user),
) -> None:
    """Удалить вопрос. Только для авторизованных."""
    deleted = await crud.delete_question(db, question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")


@app.get("/topics")
async def get_topics():
    return {'list_topics': list(set(q["topic"] for q in questions))}


@app.get("/me")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Защищённая ручка: возвращает текущего пользователя.
    """
    return current_user


@app.post(
    "/questions/{question_id}/evaluate",
    response_model=EvaluationResponse,
)
async def evaluate_user_answer_endpoint(
    question_id: int,
    answer: AnswerCreate,
    db: AsyncSession = Depends(get_db),
    # ai_client: AIClient = Depends(get_ai_client),
    current_user: UserInToken = Depends(get_current_user),
) -> EvaluationResponse:
    """Принимает ответ и отправляет на оценку AI."""
    question = await crud.get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    evaluation = await evaluate_answer(question.text, answer.text)
    
    db_answer = await crud.create_answer(
        db, answer, question_id, current_user.id, evaluation,
    )
    
    return EvaluationResponse(answer_id=db_answer.id, evaluation=evaluation)

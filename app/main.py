import asyncio
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_db
from app.ai_client import evaluate_answer
from app.dependencies import get_ai_client, get_current_user
from app.schemas import (QuestionCreate, 
                         QuestionResponse,
                         AnswerCreate, 
                         QuestionCreate,
                         QuestionResponse,
                         UserInToken,
                         EvaluationResponse)
from app.services.ai_client import AIClient


app = FastAPI(
    title="Interview Prep Bot",
    description="AI помощник для подготовки к техническим собеседованиям",
    version="0.1.0"
)


@app.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
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


@app.post("/questions", status_code=201, response_model=QuestionResponse)
async def create_question(
    question: QuestionCreate,
    current_user: dict = Depends(get_current_user),  # ← защита
):
    """Создать вопрос. Только для авторизованных пользователей."""

    db = questions
    new_id = max(i['id'] for i in db) + 1
    new_question = {
        'id': new_id,
        'topic': question.topic,
        'text': question.text,
        'difficulty': question.difficulty,
    }
    db.append(new_question)
    return new_question


@app.delete('/questions/{question_id}', status_code=204)
async def delete_question(question_id: int):
    db = questions
    for q in db:
        if q['id'] == question_id:
            db.remove(q)
            return {}
    return {'error': 'Question not found'}


@app.get("/topics")
async def get_topics():
    return {'list_topics': list(set(q["topic"] for q in questions))}


@app.post("/questions/{question_id}/evaluate", response_model=EvaluationResponse)
async def evaluate_user_answer(question_id: int, 
                               answer: AnswerCreate,
                               ai_client=Depends(get_ai_client),):
    """
    Принимает ответ пользователя и отправляет его на оценку AI.
    """
    # 1. Находим вопрос
    question = next((q for q in questions if q["id"] == question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # 2. Отправляем ответ на оценку AI (асинхронно)
    evaluation = await ai_client(question["text"], answer.text)
    
    # 3. Сохраняем ответ
    new_id = len(answers) + 1
    new_answer = {
        "id": new_id,
        "question_id": question_id,
        "text": answer.text,
        "created_at": datetime.now(),
        "evaluation": evaluation
    }
    answers.append(new_answer)
    
    return {
        "answer_id": new_id,
        "evaluation": evaluation
    }


@app.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Защищённая ручка: возвращает текущего пользователя.
    """
    return current_user

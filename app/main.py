import asyncio
from datetime import datetime

from fastapi import FastAPI, HTTPException

from app.ai_client import evaluate_answer
from app.schemas import (QuestionCreate, 
                         QuestionResponse,
                         AnswerCreate, 
                         AnswerResponse,
                         QuestionShort, 
                         QuestionFull,
                         EvaluationResponse)


app = FastAPI(
    title="Interview Prep Bot",
    description="AI помощник для подготовки к техническим собеседованиям",
    version="0.1.0"
)

# Имитация базы данных (пока без БД)
questions = [
    {"id": 1, "topic": "python", "text": "Что такое GIL?", "difficulty": 3},
    {"id": 2, "topic": "python", "text": "Чем list отличается от tuple?", "difficulty": 2},
    {"id": 3, "topic": "sql", "text": "Что такое индекс?", "difficulty": 2},
    {"id": 4, "topic": "fastapi", "text": "Что такое Dependency Injection?", "difficulty": 4},
]

answers = []


@app.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int):  # path-параметр
    db = questions
    for q in db:
        if q["id"] == question_id:
            return q
    return {"error": "Question not found"}


@app.get("/questions", response_model=list[QuestionResponse])
async def get_questions(topic: str = None, limit: int = 10):  # query-параметры
    db = questions

    if topic:
        db = [q for q in db if q["topic"] == topic]

    return db[:limit]


@app.get("/questions/{question_id}/answers")
async def get_answers(question_id: int, limit: int = 5):
    return {
        'question_id': question_id,
        'limit': limit,
        'answers': []
    }


@app.post("/questions", status_code=201, response_model=QuestionResponse)
async def create_question(question: QuestionCreate):
    db = questions
    new_id = max(i['id'] for i in db) + 1
    new_question = {
        'id': new_id,
        'topic': question.topic,
        'text': question.text,
        'difficulty': question.difficulty,
    }
    db.append(new_question)
    print(db)
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
async def evaluate_user_answer(question_id: int, answer: AnswerCreate):
    """
    Принимает ответ пользователя и отправляет его на оценку AI.
    """
    # 1. Находим вопрос
    question = next((q for q in questions if q["id"] == question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # 2. Отправляем ответ на оценку AI (асинхронно)
    evaluation = await evaluate_answer(question["text"], answer.text)
    
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

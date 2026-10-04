from fastapi import FastAPI

from app.schemas import QuestionCreate, QuestionResponse


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


@app.get("/questions/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int):  # path-параметр
    db = questions
    for q in db:
        if q["id"] == question_id:
            return q
    return {"error": "Question not found"}


@app.get("/questions", response_model=list[QuestionResponse])
def get_questions(topic: str = None, limit: int = 10):  # query-параметры
    db = questions

    if topic:
        db = [q for q in db if q["topic"] == topic]

    return db[:limit]


@app.get("/questions/{question_id}/answers")
def get_answers(question_id: int, limit: int = 5):
    return {
        'question_id': question_id,
        'limit': limit,
        'answers': []
    }


@app.post("/questions", status_code=201, response_model=QuestionResponse)
def create_question(question: QuestionCreate):
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
def delete_question(question_id: int):
    db = questions
    for q in db:
        if q['id'] == question_id:
            db.remove(q)
            return {}
    return {'error': 'Question not found'}


@app.get("/topics")
def get_topics():
    return {'list_topics': list(set(q["topic"] for q in questions))}


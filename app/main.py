from fastapi import FastAPI

app = FastAPI(
    title="Interview Prep Bot",
    description="AI помощник для подготовки к техническим собеседованиям",
    version="0.1.0"
)

# Имитация базы данных (пока без БД)
questions = [
    {"id": 1, "topic": "python", "text": "Что такое GIL?"},
    {"id": 2, "topic": "python", "text": "Чем list отличается от tuple?"},
    {"id": 3, "topic": "sql", "text": "Что такое индекс?"},
    {"id": 4, "topic": "fastapi", "text": "Что такое Dependency Injection?"},
]


@app.get("/questions/{question_id}")
def get_question(question_id: int):  # path-параметр
    db = questions
    for q in db:
        if q["id"] == question_id:
            return q
    return {"error": "Question not found"}


@app.get("/questions")
def get_questions(topic: str = None, limit: int = 10):  # query-параметры
    db = questions

    if topic:
        db = [q for q in db if q["topic"] == topic]

    return db[:limit]

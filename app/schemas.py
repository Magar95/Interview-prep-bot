from datetime import datetime

from pydantic import BaseModel, ValidationError, Field, ConfigDict, EmailStr


class QuestionBase(BaseModel):
    """Базовая схема вопроса"""

    topic: str = Field(..., min_length=2, max_length=50, description='Тема вопроса')
    text: str = Field(..., min_length=10, max_length=1000, description='Текст вопроса')
    difficulty: int = Field(1, ge=1, le=5, description='Сложность вопроса от 1 до 5')


class QuestionCreate(QuestionBase):
    """Схема для создания вопроса."""

    pass


class QuestionResponse(QuestionBase):
    """В каком виде пользователь получит вопрос от сайта."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class AnswerBase(BaseModel):
    """Базовая схема ответа"""

    question_id: int
    text: str = Field(..., min_length=1, max_length=500)


class AnswerCreate(AnswerBase):
    """Схема для создания ответа."""

    pass


class AnswerResponse(AnswerBase):
    """В каком виде пользователь получит ответ от сайта."""

    pass


class QuestionShort(BaseModel):
    """Короткая схема вопроса (для списка вопросов)"""

    id: int
    topic: str
    text: str


class QuestionFull(QuestionBase):
    """Полная схема вопроса (для детального просмотра)"""

    id: int
    answers: list[AnswerResponse] = []
    created_at: datetime = Field(datetime.now())

    model_config = ConfigDict(from_attributes=True)


class QuestionWithAnswers(QuestionCreate):
    id: int
    topic: str
    text: str
    answers: list[AnswerBase] = []


class EvaluationResponse(BaseModel):
    '''Схема оценки AI на ответ'''

    answer_id: int
    evaluation: dict


class UserInToken(BaseModel):
    """Пользователь, извлечённый из токена."""
    id: int
    username: str


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    id: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
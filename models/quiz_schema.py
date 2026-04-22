from pydantic import BaseModel

class Question(BaseModel):
    question: str
    options: list[str]
    answer: str
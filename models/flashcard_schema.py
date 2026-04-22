from pydantic import BaseModel

class Flashcard(BaseModel):
    concept: str
    definition: str
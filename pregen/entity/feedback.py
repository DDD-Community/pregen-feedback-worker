from langchain.pydantic_v1 import BaseModel


class Feedback(BaseModel):
    id: int
    practice_id: int
    memorization_score: float
    speed_score: float
    time_score: float
    total_score: float

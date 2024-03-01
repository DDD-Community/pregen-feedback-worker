from langchain.pydantic_v1 import BaseModel


class WordError(BaseModel):
    slide_id: int
    start_index: int
    end_index: int

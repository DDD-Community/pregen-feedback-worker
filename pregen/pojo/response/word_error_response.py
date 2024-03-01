from langchain.pydantic_v1 import BaseModel


class WordErrorResponseDetail(BaseModel):
    original_word: str
    spoken_word: str
    word_start_index: int


class WordErrorResponse(BaseModel):
    results: list[WordErrorResponseDetail]

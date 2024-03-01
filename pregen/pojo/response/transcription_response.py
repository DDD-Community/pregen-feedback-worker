from langchain.pydantic_v1 import BaseModel


class TranscriptionResponse(BaseModel):
    spoke_script: str
    word_count: int
    audio_duration: int

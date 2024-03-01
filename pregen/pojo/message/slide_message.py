from langchain.pydantic_v1 import BaseModel


class SlideMessage(BaseModel):
    slideId: int
    originalScript: str
    audioFilePath: str

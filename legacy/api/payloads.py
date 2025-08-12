from pydantic import BaseModel


class GeneratePL(BaseModel):
    prompt: str

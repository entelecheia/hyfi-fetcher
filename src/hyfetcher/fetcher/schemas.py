# schemas.py
from pydantic import BaseModel


class PressRelease(BaseModel):
    title: str
    content: str
    date: str  # Adding a date field to store the publication date

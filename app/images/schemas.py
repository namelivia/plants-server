from pydantic import BaseModel


class Image(BaseModel):
    location: str

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
import datetime


class PlantBase(BaseModel):
    name: str = Field(title="Name for the plant")
    description: Optional[str] = Field(title="Description for the plant")
    image: Optional[str] = Field(title="Image url for the plant")


class PlantCreate(PlantBase):
    pass


class Plant(PlantBase):
    id: int
    days_until_watering: int = Field(title="Days until the next plant watering")
    journaling_key: UUID = Field(title="Parent key for the journal entry")
    last_watering: datetime.datetime = Field(title="Time of the last watering")

    class Config:
        orm_mode = True


class JournalEntryBase(BaseModel):
    message: str = Field(title="Message contents")


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntry(JournalEntryBase):
    id: int
    key: UUID = Field(title="Parent key for the journal entry")
    timestamp: datetime.datetime = Field(title="Entry timestamp")

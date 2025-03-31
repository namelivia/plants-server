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


class PlantUpdate(PlantBase):
    pass


class WaterEvery(BaseModel):
    days: int


class Plant(PlantBase):
    id: int
    water_every: int = Field(title="Number of days between each watering")
    until_next_watering: int = Field(title="Days until the next plant watering")
    journaling_key: UUID = Field(title="Parent key for the journal entry")
    last_watering: datetime.datetime = Field(title="Time of the last watering")
    alive: bool = Field(title="If the plant is alive")
    indoor: bool = Field(title="If the plant is placed indoor")

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

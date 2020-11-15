from typing import Optional

from pydantic import BaseModel, Field


class PlantBase(BaseModel):
    name: str = Field(title="Name for the plant")
    description: Optional[str] = Field(title="Description for the plant")


class PlantCreate(PlantBase):
    pass


class Plant(PlantBase):
    id: int
    days_until_watering: int = Field(
        title="Days until the next plant watering"
    )

    class Config:
        orm_mode = True

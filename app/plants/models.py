from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from fastapi_utils.guid_type import GUID

PlantsBase = declarative_base()


class Plant(PlantsBase):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    journaling_key = Column(GUID, nullable=False)
    description = Column(String)
    days_until_watering = Column(Integer, nullable=False)
    last_watering = Column(DateTime, nullable=False)
    image = Column(String)

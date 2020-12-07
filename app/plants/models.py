from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

PlantsBase = declarative_base()


class Plant(PlantsBase):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    days_until_watering = Column(Integer, nullable=False)

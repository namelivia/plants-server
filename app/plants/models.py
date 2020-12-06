from sqlalchemy import Column, Integer, String

from app.database import Base


class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    days_until_watering = Column(Integer, nullable=False)

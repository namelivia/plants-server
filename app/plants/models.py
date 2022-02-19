from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from fastapi_utils.guid_type import GUID
from app.database import Base


class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    journaling_key = Column(GUID, nullable=False)
    description = Column(String)
    water_every = Column(Integer, nullable=False)
    last_watering = Column(DateTime, nullable=False, server_default=func.now())
    alive = Column(Boolean, nullable=False)
    image = Column(String)

from sqlalchemy.orm import Session

from . import models, schemas
from app.notifications.notifications import Notifications


def get_plant(db: Session, plant_id: int):
    return db.query(models.Plant).filter(models.Plant.id == plant_id).first()


# TODO: skip and limit
def get_plants(db: Session):
    return db.query(models.Plant).all()


def create_plant(db: Session, plant: schemas.PlantCreate):
    db_plant = models.Plant(**plant.dict(), days_until_watering=7)
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    Notifications.send("A new plant has been created")
    return db_plant


def delete_plant(db: Session, plant: models.Plant):
    db.delete(plant)
    db.commit()

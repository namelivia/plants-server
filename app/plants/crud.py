# TODO: Maybe the filename crud is not that good since this is not CRUD anymore
from sqlalchemy.orm import Session
import logging
import uuid
from . import models, schemas
from app.notifications.notifications import Notifications
from app.journaling.journaling import Journaling

logger = logging.getLogger(__name__)


def get_plant(db: Session, plant_id: int):
    return db.query(models.Plant).filter(models.Plant.id == plant_id).first()


# TODO: skip and limit
def get_plants(db: Session):
    return db.query(models.Plant).all()


def create_plant(db: Session, plant: schemas.PlantCreate):
    db_plant = models.Plant(
        **plant.dict(),
        days_until_watering=7,
        journaling_key=uuid.uuid4()
    )
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    logger.info("New plant created")
    try:
        Notifications.send(
            f"A new plant called {db_plant.name} has been created"
        )
    except Exception as err:
        logger.error(f"Notification could not be sent: {str(err)}")
    try:
        Journaling.create(
            db_plant.journaling_key,
            f"A new plant called {db_plant.name} has been created"
        )
    except Exception as err:
        logger.error(f"Could not add journal entry: {str(err)}")
    return db_plant


def delete_plant(db: Session, plant: models.Plant):
    db.delete(plant)
    db.commit()
    logger.info("Plant deleted")


def water_plant(db: Session, plant: models.Plant):
    plant.days_until_watering = 0
    db.commit()
    db.refresh(plant)
    try:
        Notifications.send(f"The plant {plant.name} has been watered")
    except Exception as err:
        logger.error(f"Notification could not be sent: {str(err)}")
    logger.info("Plant watered")
    return plant


def get_plants_to_be_watered(db: Session):
    return db.query(models.Plant).filter(
        models.Plant.days_until_watering > 5
    ).all()

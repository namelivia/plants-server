# TODO: Maybe the filename crud is not that good since this is not CRUD anymore
from sqlalchemy.orm import Session
import logging
import uuid
import datetime
from . import models, schemas
from app.notifications.notifications import Notifications
from app.journaling.journaling import Journaling

logger = logging.getLogger(__name__)


def _calculate_days_until_next_watering(
    last_watering: datetime, water_every: int
) -> int:
    next_watering_day = last_watering + datetime.timedelta(days=water_every)
    today = datetime.datetime.now()
    until_next_watering = next_watering_day - today
    return until_next_watering.days


def get_plant(db: Session, plant_id: int):
    plant = db.query(models.Plant).filter(models.Plant.id == plant_id).first()
    if plant is not None:
        plant.until_next_watering = _calculate_days_until_next_watering(
            plant.last_watering,
            plant.water_every,
        )
    return plant


# TODO: skip and limit
def get_plants(db: Session):
    plants = db.query(models.Plant).filter(models.Plant.alive == True).all()
    for plant in plants:
        plant.until_next_watering = _calculate_days_until_next_watering(
            plant.last_watering,
            plant.water_every,
        )
    return plants


def get_dead_plants(db: Session):
    plants = db.query(models.Plant).filter(models.Plant.alive == False).all()
    for plant in plants:
        plant.until_next_watering = _calculate_days_until_next_watering(
            plant.last_watering,
            plant.water_every,
        )
    return plants


def create_plant(db: Session, plant: schemas.PlantCreate):
    db_plant = models.Plant(
        **plant.dict(),
        water_every=7,  # TODO: This will come from an API
        last_watering=datetime.datetime.now(),
        journaling_key=uuid.uuid4(),
        alive=True,
    )
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    db_plant.until_next_watering = _calculate_days_until_next_watering(
        db_plant.last_watering,
        db_plant.water_every,
    )
    logger.info("New plant created")
    try:
        Notifications.send("en", f"A new plant called {db_plant.name} has been created")
        Notifications.send(
            "es", f"Una planta nueva llamada {db_plant.name} se ha creado"
        )
    except Exception as err:
        logger.error(f"Notification could not be sent: {str(err)}")
    try:
        Journaling.create(
            db_plant.journaling_key,
            f"A new plant called {db_plant.name} has been created",
        )
    except Exception as err:
        logger.error(f"Could not add journal entry: {str(err)}")
    return db_plant


def update_plant(db: Session, plant_id: int, new_plant_data: schemas.PlantUpdate):
    plants = db.query(models.Plant).filter(models.Plant.id == plant_id)
    plants.update(new_plant_data.dict(), synchronize_session=False)
    db.commit()
    plant = plants.first()
    plant.until_next_watering = _calculate_days_until_next_watering(
        plant.last_watering,
        plant.water_every,
    )
    logger.info("Plant updated")
    try:
        Notifications.send("en", f"The plant {plant.name} has been updated")
        Notifications.send("es", f"La planta {plant.name} se ha actualizado")
    except Exception as err:
        logger.error(f"Notification could not be sent: {str(err)}")
    try:
        Journaling.create(
            plant.journaling_key,
            f"The plant {plant.name} has been updated",
        )
    except Exception as err:
        logger.error(f"Could not add journal entry: {str(err)}")
    return plant


def update_watering_schedule(db: Session, plant_id: int, days: int):
    plants = db.query(models.Plant).filter(models.Plant.id == plant_id)
    plants.update({"water_every": days}, synchronize_session=False)
    db.commit()
    plant = plants.first()
    plant.until_next_watering = _calculate_days_until_next_watering(
        plant.last_watering,
        plant.water_every,
    )
    logger.info("Plant watering schedule updated")
    try:
        Notifications.send(
            "en", f"The plant {plant.name} will be watered every {days} days"
        )
        Notifications.send("es", f"La planta {plant.name} se regará cada {days} días")
    except Exception as err:
        logger.error(f"Notification could not be sent: {str(err)}")
    try:
        Journaling.create(
            plant.journaling_key,
            f"The plant {plant.name} will be watered every {days} days",
        )
    except Exception as err:
        logger.error(f"Could not add journal entry: {str(err)}")
    return plant


def delete_plant(db: Session, plant: models.Plant):
    db.delete(plant)
    db.commit()
    logger.info("Plant deleted")


def water_plant(db: Session, plant: models.Plant):
    plant.last_watering = datetime.datetime.now()
    db.commit()
    db.refresh(plant)
    try:
        Notifications.send("en", f"The plant {plant.name} has been watered")
        Notifications.send("es", f"La planta {plant.name} se ha regado")
    except Exception as err:
        logger.error(f"Notification could not be sent: {str(err)}")
    try:
        Journaling.create(
            plant.journaling_key, f"A The plant {plant.name} has been watered"
        )
    except Exception as err:
        logger.error(f"Could not add journal entry: {str(err)}")
    logger.info("Plant watered")
    plant.until_next_watering = _calculate_days_until_next_watering(
        plant.last_watering,
        plant.water_every,
    )
    return plant


def kill_plant(db: Session, plant: models.Plant):
    plant.alive = False
    db.commit()
    db.refresh(plant)
    try:
        Notifications.send("en", f"The plant {plant.name} is now dead")
        Notifications.send("es", f"La planta {plant.name} está muerta")
    except Exception as err:
        logger.error(f"Notification could not be sent: {str(err)}")
    try:
        Journaling.create(plant.journaling_key, f"A The plant {plant.name} has died")
    except Exception as err:
        logger.error(f"Could not add journal entry: {str(err)}")
    logger.info("Plant killed")
    return plant


def get_plants_to_be_watered(db: Session):
    plants = db.query(models.Plant).filter(models.Plant.alive == True).all()
    for plant in plants:
        plant.until_next_watering = _calculate_days_until_next_watering(
            plant.last_watering,
            plant.water_every,
        )
    return [plant for plant in plants if plant.until_next_watering <= 0]

from fastapi import APIRouter, Path, HTTPException, Depends, Response
from http import HTTPStatus
from app.dependencies import get_db
from . import crud, schemas
from typing import List
from sqlalchemy.orm import Session
from app.journaling.journaling import Journaling

router = APIRouter(prefix="/plants", dependencies=[Depends(get_db)])


@router.get("", response_model=List[schemas.Plant])
def plants(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    plants = crud.get_plants(db)
    return plants


@router.get("/dead", response_model=List[schemas.Plant])
def dead_plants(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    plants = crud.get_dead_plants(db)
    return plants


def _get_plant(db: Session, plant_id: int):
    db_plant = crud.get_plant(db, plant_id=plant_id)
    if db_plant is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Plant not found")
    return db_plant


@router.get("/{plant_id}", response_model=schemas.Plant)
def get_plant(
    plant_id: int = Path(None, title="The ID of the plant to get", ge=1),
    db: Session = Depends(get_db),
):
    return _get_plant(db, plant_id)


@router.get("/{plant_id}/journal")
def get_journal(
    db: Session = Depends(get_db),
    plant_id: int = Path(
        None, title="The ID of the plant to get the journal from", ge=1
    ),
):
    plant = _get_plant(db, plant_id)
    return Journaling.get(plant.journaling_key)


@router.post(
    "/{plant_id}/journal",
    response_model=schemas.JournalEntry,
    status_code=HTTPStatus.CREATED,
)
def post_journal_entry(
    new_entry: schemas.JournalEntryCreate,
    db: Session = Depends(get_db),
    plant_id: int = Path(None, title="The ID for the plant", ge=1),
):
    plant = _get_plant(db, plant_id)
    return Journaling.create(plant.journaling_key, new_entry.message)


@router.post("/{plant_id}/water", response_model=schemas.Plant)
def water_plant(
    plant_id: int = Path(None, title="The ID of the plant to get", ge=1),
    db: Session = Depends(get_db),
):
    plant = _get_plant(db, plant_id)
    return crud.water_plant(db, plant)


@router.post("/{plant_id}/kill", response_model=schemas.Plant)
def kill_plant(
    plant_id: int = Path(None, title="The ID of the plant to kill", ge=1),
    db: Session = Depends(get_db),
):
    plant = _get_plant(db, plant_id)
    return crud.kill_plant(db, plant)


@router.post("", response_model=schemas.Plant, status_code=HTTPStatus.CREATED)
def create_plant(plant: schemas.PlantCreate, db: Session = Depends(get_db)):
    return crud.create_plant(db, plant)


@router.put("/{plant_id}", response_model=schemas.Plant, status_code=HTTPStatus.OK)
def update_plant(
    new_plant_data: schemas.PlantUpdate,
    db: Session = Depends(get_db),
    plant_id: int = Path(None, title="The ID for the plant to update", ge=1),
):
    return crud.update_plant(db, plant_id, new_plant_data)


@router.delete("/{plant_id}")
async def delete_plant(
    plant_id: int = Path(None, title="The ID of the plant to remove", ge=1),
    db: Session = Depends(get_db),
):
    crud.delete_plant(db, _get_plant(db, plant_id))
    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.post(
    "/{plant_id}/water_every", response_model=schemas.Plant, status_code=HTTPStatus.OK
)
def water_every(
    new_plant_schedule: schemas.WaterEvery,
    db: Session = Depends(get_db),
    plant_id: int = Path(None, title="The ID for the plant to update", ge=1),
):
    return crud.update_watering_schedule(db, plant_id, new_plant_schedule.days)

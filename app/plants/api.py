from fastapi import (
    APIRouter,
    Path,
    HTTPException,
    Depends,
    Response
)
from http import HTTPStatus
from app.dependencies import get_db
from . import crud, schemas
from typing import Optional, List
from sqlalchemy.orm import Session
from shamrock import Shamrock
import os

router = APIRouter(
    prefix="/plants",
    dependencies=[Depends(get_db)]
)


@router.get("", response_model=List[schemas.Plant])
def plants(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    plants = crud.get_plants(db)
    return plants


def _get_plant(db: Session, plant_id: int):
    db_plant = crud.get_plant(db, plant_id=plant_id)
    if db_plant is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Plant not found"
        )
    return db_plant


@router.get("/{plant_id}", response_model=schemas.Plant)
def get_plant(
    plant_id: int = Path(None, title="The ID of the plant to get", ge=1),
    db: Session = Depends(get_db)
):
    return _get_plant(db, plant_id)


@router.post("/{plant_id}/water", response_model=schemas.Plant)
def water_plant(
    plant_id: int = Path(None, title="The ID of the plant to get", ge=1),
    db: Session = Depends(get_db)
):
    plant = _get_plant(db, plant_id)
    return crud.water_plant(db, plant)


@router.post(
    "",
    response_model=schemas.Plant,
    status_code=HTTPStatus.CREATED
)
def create_plant(
    plant: schemas.PlantCreate,
    db: Session = Depends(get_db)
):
    return crud.create_plant(db, plant)


@router.put(
    "/{plant_id}",
    response_model=schemas.Plant
)
async def update_plant(
    plant_id: int = Path(None, title="The ID of the plant to update", ge=1),
    plant: Optional[schemas.Plant] = None
):
    result = {"plant": plant}
    if plant:
        result.update({"updated_plant": plant})
    return schemas.Plant(name="test")


@router.delete("/{plant_id}")
async def delete_plant(
    plant_id: int = Path(None, title="The ID of the plant to remove", ge=1),
    db: Session = Depends(get_db)
):
    crud.delete_plant(db, _get_plant(db, plant_id))
    return Response(status_code=HTTPStatus.NO_CONTENT)

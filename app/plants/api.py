from fastapi import (
    APIRouter,
    Path,
    File,
    UploadFile,
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


@router.get("/species")
def test_api(query: str = ''):
    api = Shamrock('YOUR_TREFLE_API_KEY')
    return api.search(query)


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


# Good for small files
@router.post("/files/")
async def create_file(file: bytes = File(None, title="File to review")):
    return {"file_size": len(file)}


# More routerropriate for big files
@router.post("/uploadfile/")
async def create_upload_file(
    file: UploadFile = File(None, title="File to upload")
):
    return {"filename": file.filename}

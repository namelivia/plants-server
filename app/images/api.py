from fastapi import (
    APIRouter,
    File,
    UploadFile
)
import httpx
import os
from . import schemas
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/images"
)


@router.post("", response_model=schemas.Image)
async def image(media: UploadFile = File(...)):
    logger.info("Uploading image")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=os.getenv("IMAGES_SERVICE_ENDPOINT"),
            files={"media": media.file}
        )
    return schemas.Image(location=response.headers['location'])

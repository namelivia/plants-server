from fastapi import (
    APIRouter,
    File,
    UploadFile,
    Response,
)
import httpx
import requests
import os
from . import schemas
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/image"
)


@router.post("", response_model=schemas.Image)
async def post_image(media: UploadFile = File(...)):
    logger.info("Uploading image")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=os.getenv("IMAGES_SERVICE_ENDPOINT"),
            files={"media": media.file}
        )
    return schemas.Image(location=response.headers['location'])


@router.get("/{image_path}/{extra}")
async def get_image(
    image_path: str,
    extra: str,
):
    logger.info("Retrieving image")
    logger.info(image_path)
    image = requests.get(os.getenv("IMAGES_SERVICE_ENDPOINT") + '/' + image_path)
    return Response(content=image.content)

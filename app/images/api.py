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

router = APIRouter(prefix="/image")


@router.post("", response_model=schemas.Image)
async def post_image(media: UploadFile = File(...)):
    logger.info("Uploading image")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=os.getenv("IMAGES_SERVICE_ENDPOINT") + "/image/",
            files={"media": media.file},
        )
    return schemas.Image(location=response.headers["location"])


@router.get("/{image_path}/{extra}")
async def get_image(
    image_path: str,
    extra: str,
):
    logger.info("Retrieving image")
    logger.info(image_path)
    # TODO: service to return scaled images depending on the frontend needs
    originalUrl = os.getenv("IMAGES_SERVICE_ENDPOINT") + "/image/" + image_path
    image = requests.get(
        os.getenv("IMAGES_SERVICE_ENDPOINT") + "/unsafe/fit-in/1024x768/" + originalUrl
    )
    return Response(content=image.content)

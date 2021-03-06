from fastapi import (
    APIRouter,
    File,
    UploadFile,
    Response,
)
from typing import Optional
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
            url=os.getenv("IMAGES_SERVICE_ENDPOINT") + "/image",
            files={"media": media.file},
        )
    return schemas.Image(location=response.headers["location"])


@router.get("/{image_path}/{extra}")
async def get_image(
    image_path: str,
    extra: str,
    width: Optional[int] = None,
):
    # TODO: service to return scaled images depending on the frontend needs
    original_url = os.getenv("IMAGES_SERVICE_ENDPOINT") + "/image/" + image_path
    image_width = width if width is not None else 1024
    logger.info(original_url)
    scaled_url = (
        os.getenv("IMAGES_SERVICE_ENDPOINT")
        + f"/unsafe/fit-in/{image_width}x0/"
        + original_url
    )
    logger.info(scaled_url)
    image = requests.get(scaled_url)
    logger.info(image.status_code)
    return Response(content=image.content)

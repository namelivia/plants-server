import os
import requests
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class Journaling:

    @staticmethod
    def create(key: UUID, message: str):
        logger.info("Creating journal entry")
        data = {
            'message': message,
            'key': str(key)
        }
        response = requests.post(
            url=os.getenv("JOURNALING_SERVICE_ENDPOINT") + '/new',
            json=data
        )
        logger.info(response.text)

    @staticmethod
    def get(key: UUID):
        logger.info("Reading journal")
        response = requests.get(
            url=os.getenv("JOURNALING_SERVICE_ENDPOINT") + f"{str(key)}/all",
        )
        logger.info(response.text)
        return response.text

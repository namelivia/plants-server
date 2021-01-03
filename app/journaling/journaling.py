import os
import requests
import logging

logger = logging.getLogger(__name__)


class Journaling:

    @staticmethod
    def create(message: str):
        logger.info("Creating journal entry")
        data = {
            'message': message
        }
        response = requests.post(
            url=os.getenv("JOURNALING_SERVICE_ENDPOINT") + '/new',
            json=data
        )
        logger.info(response.text)

    @staticmethod
    def get():
        logger.info("Reading journal")
        response = requests.get(
            url=os.getenv("JOURNALING_SERVICE_ENDPOINT") + '/all',
        )
        logger.info(response.text)
        return response

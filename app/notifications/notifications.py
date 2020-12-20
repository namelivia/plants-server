import os
import requests


class Notifications:

    @staticmethod
    def send(message: str):
        data = {
            'message': message
        }
        requests.post(
            url=os.getenv("NOTIFICATIONS_SERVICE_ENDPOINT"),
            data=data
        )

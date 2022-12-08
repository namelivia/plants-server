from app.plants import crud
from sqlalchemy.orm import Session
import logging
import sys
from app.notifications.notifications import Notifications

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logger = logging.getLogger(__name__)


class Tasks:
    @staticmethod
    def send_watering_reminders(db: Session):
        logger.info("Checking for watering reminders")
        plants = crud.get_plants_to_be_watered(db)
        if len(plants) > 0:
            messages = {
                "es": f"Hay {len(plants)} plantas que necesitan regarse",
                "en": f"There are {len(plants)} plants that need to be watered",
            }
            for language, message in messages.items():
                logger.info(f"Sending watering reminders for language {language}")
                try:
                    Notifications.send(language, message)
                except Exception as err:
                    logger.error(
                        f"Notification for language {language} could not be sent: {str(err)}"
                    )
        return plants

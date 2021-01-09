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
        logger.info(f"Checking for watering reminders")
        plants = crud.get_plants_to_be_watered(db)
        if len(plants) > 0:
            logger.info(f"Sending watering reminders")
            try:
                Notifications.send(
                    f"There are {len(plants)} plants that need to be watered"
                )
            except Exception as err:
                logger.error(f"Notification could not be sent: {str(err)}")
        return plants

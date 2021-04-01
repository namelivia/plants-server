from mock import patch, Mock
import uuid
from .test_base import (
    client,
    create_test_database,
    database_test_session,
)
from app.plants.models import Plant
from app.tasks.tasks import Tasks
import datetime
from freezegun import freeze_time


@freeze_time("2013-04-09")
class TestApp:
    def _insert_test_plant(self, session, plant: dict = {}):
        key = uuid.uuid4()
        data = {
            "name": "Test plant",
            "description": "Test Description",
            "days_until_watering": 3,
            "journaling_key": key,
            "alive": True,
            "last_watering": datetime.datetime.now(),
        }
        data.update(plant)
        db_plant = Plant(**data)
        session.add(db_plant)
        session.commit()
        return db_plant

    @patch("app.notifications.notifications.Notifications.send")
    def test_sending_watering_reminders(
        self, m_send_notification, database_test_session
    ):
        self._insert_test_plant(database_test_session)
        dry_plant = self._insert_test_plant(
            database_test_session, {"days_until_watering": 10}
        )
        another_dry_plant = self._insert_test_plant(
            database_test_session, {"days_until_watering": 12}
        )
        # Dead plant
        self._insert_test_plant(
            database_test_session, {"days_until_watering": 12, "alive": False}
        )
        self._insert_test_plant(database_test_session, {"days_until_watering": 5})
        result = Tasks.send_watering_reminders(database_test_session)
        m_send_notification.assert_called_with(
            "There are 2 plants that need to be watered"
        )
        assert len(result) == 2
        assert set(result) == set([dry_plant, another_dry_plant])

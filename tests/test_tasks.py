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
            "water_every": 3,
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
        dry_plant = self._insert_test_plant(
            database_test_session, {"name": "Plant1", "water_every": 4}
        )
        another_dry_plant = self._insert_test_plant(
            database_test_session, {"name": "Plant2", "water_every": 3}
        )
        # Dead plant
        self._insert_test_plant(
            database_test_session, {"water_every": 12, "alive": False}
        )
        # Not a dry plant
        self._insert_test_plant(database_test_session, {"water_every": 5})
        with freeze_time("2013-04-13"):
            result = Tasks.send_watering_reminders(database_test_session)
        m_send_notification.assert_any_call(
            "en", "There are 2 plants that need to be watered\n- Plant1\n- Plant2"
        )
        m_send_notification.assert_any_call(
            "es", "Hay 2 plantas que necesitan regarse\n- Plant1\n- Plant2"
        )
        assert len(result) == 2
        assert set(result) == set([dry_plant, another_dry_plant])

from mock import patch, Mock
import uuid
from .test_base import (
    client,
    create_test_database,
    database_test_session,
)
from app.plants.models import Plant
from app.plants.schemas import Plant as PlantSchema
from app.tasks.tasks import Tasks
import datetime
from freezegun import freeze_time


@freeze_time('2013-04-09')
class TestApp:

    def _insert_test_plant(self, session, plant: dict = {}):
        key = uuid.uuid4()
        data = {
            "name": 'Test plant',
            "description": 'Test Description',
            "days_until_watering": 3,
            "journaling_key": key,
            "last_watering": datetime.datetime.now(),
        }
        data.update(plant)
        db_plant = Plant(**data)
        session.add(db_plant)
        session.commit()
        return db_plant

    @patch("uuid.uuid4")
    @patch("app.notifications.notifications.Notifications.send")
    def test_create_plant_description(self, m_send_notification, m_uuid, client):
        key = '271c973a-638f-4e01-9a79-308c880e3d11'
        m_uuid.return_value = key
        response = client.post("/plants", json={
            'name': 'Test plant 2',
            'description': 'Test description',
        })
        assert response.status_code == 201
        assert response.json() == {
            "id": 1,
            "name": "Test plant 2",
            "description": "Test description",
            "days_until_watering": 7,
            "image": None,
            "journaling_key": key,
            "last_watering": "2013-04-09T00:00:00",
        }
        m_send_notification.assert_called_with(
            "A new plant called Test plant 2 has been created"
        )

    @patch("uuid.uuid4")
    @patch("app.notifications.notifications.Notifications.send")
    def test_create_plant_no_description(self, m_send_notification, m_uuid, client):
        key = '271c973a-638f-4e01-9a79-308c880e3d11'
        m_uuid.return_value = key
        response = client.post("/plants", json={
            'name': 'Test plant'
        })
        assert response.status_code == 201
        assert response.json() == {
            "id": 1,
            "name": "Test plant",
            "description": None,
            "days_until_watering": 7,
            "image": None,
            "journaling_key": key,
            "last_watering": "2013-04-09T00:00:00",
        }
        m_send_notification.assert_called_with(
            "A new plant called Test plant has been created"
        )

    def test_get_non_existing_plant(self, client):
        response = client.get("/plants/99")
        assert response.status_code == 404

    def test_get_existing_plant(self, client, database_test_session):
        key = uuid.uuid4()
        self._insert_test_plant(database_test_session, {"journaling_key": key})
        response = client.get("/plants/1")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "Test plant",
            "description": 'Test Description',
            "days_until_watering": 3,
            "image": None,
            "journaling_key": str(key),
            "last_watering": "2013-04-09T00:00:00",
        }

    def test_create_plant_invalid(self, client):
        response = client.post("/plants", json={
            'payload': 'Invalid'
        })
        assert response.status_code == 422

    @patch("app.notifications.notifications.Notifications.send")
    def test_water_plant(self, m_send_notification, client, database_test_session):
        key = uuid.uuid4()
        self._insert_test_plant(database_test_session, {
            "journaling_key": key,
            "last_watering": datetime.datetime(2012, 5, 5)
        })
        response = client.post("/plants/1/water")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "Test plant",
            "description": 'Test Description',
            "days_until_watering": 3,
            "image": None,
            "journaling_key": str(key),
            "last_watering": "2013-04-09T00:00:00",
        }
        m_send_notification.assert_called_with("The plant Test plant has been watered")

    def test_get_all_plants(self, client, database_test_session):
        key = uuid.uuid4()
        self._insert_test_plant(database_test_session, {"journaling_key": key})
        self._insert_test_plant(database_test_session, {"journaling_key": key})
        response = client.get("/plants")
        assert response.status_code == 200
        assert response.json() == [{
            "id": 1,
            "name": "Test plant",
            "description": 'Test Description',
            "days_until_watering": 3,
            "image": None,
            "journaling_key": str(key),
            "last_watering": "2013-04-09T00:00:00",
        }, {
            "id": 2,
            "name": "Test plant",
            "description": 'Test Description',
            "days_until_watering": 3,
            "image": None,
            "journaling_key": str(key),
            "last_watering": "2013-04-09T00:00:00",
        }]

    def test_delete_non_existing_plant(self, client):
        response = client.get("/plants/99")
        assert response.status_code == 404

    def test_delete_plant(self, client, database_test_session):
        self._insert_test_plant(database_test_session)
        response = client.get("/plants/1")
        assert response.status_code == 200

    def test_post_image(self, client):
        response = client.post("/image")
        assert response.status_code == 422

    @patch("requests.get")
    def test_get_image(self, m_get, client):
        m_get.return_value = Mock()
        m_get.return_value.content = 'image_binary_data'
        response = client.get("/image/image_path/extra")
        m_get.assert_called_with('http://images-service:80/image/image_path')
        assert response.status_code == 200
        assert response.content == b'image_binary_data'

    @patch("app.notifications.notifications.Notifications.send")
    def test_sending_watering_reminders(self, m_send_notification, database_test_session):
        self._insert_test_plant(database_test_session)
        dry_plant = self._insert_test_plant(database_test_session, {
            "days_until_watering": 10
        })
        another_dry_plant = self._insert_test_plant(database_test_session, {
            "days_until_watering": 12
        })
        self._insert_test_plant(database_test_session, {
            "days_until_watering": 5
        })
        result = Tasks.send_watering_reminders(database_test_session)
        m_send_notification.assert_called_with(
            "There are 2 plants that need to be watered"
        )
        assert len(result) == 2
        assert set(result) == set([dry_plant, another_dry_plant])

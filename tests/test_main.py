import pytest
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

    @patch("uuid.uuid4")
    @patch("app.notifications.notifications.Notifications.send")
    def test_create_plant_description(self, m_send_notification, m_uuid, client):
        key = "271c973a-638f-4e01-9a79-308c880e3d11"
        m_uuid.return_value = key
        response = client.post(
            "/plants",
            json={
                "name": "Test plant 2",
                "description": "Test description",
            },
        )
        assert response.status_code == 201
        assert response.json() == {
            "id": 1,
            "name": "Test plant 2",
            "description": "Test description",
            "water_every": 7,
            "until_next_watering": 7,
            "image": None,
            "journaling_key": key,
            "alive": True,
            "last_watering": "2013-04-09T00:00:00",
        }
        m_send_notification.assert_any_call(
            "en", "A new plant called Test plant 2 has been created"
        )

    @patch("uuid.uuid4")
    @patch("app.notifications.notifications.Notifications.send")
    def test_create_plant_no_description(self, m_send_notification, m_uuid, client):
        key = "271c973a-638f-4e01-9a79-308c880e3d11"
        m_uuid.return_value = key
        response = client.post("/plants", json={"name": "Test plant"})
        assert response.status_code == 201
        assert response.json() == {
            "id": 1,
            "name": "Test plant",
            "description": None,
            "water_every": 7,
            "until_next_watering": 7,
            "image": None,
            "journaling_key": key,
            "alive": True,
            "last_watering": "2013-04-09T00:00:00",
        }
        m_send_notification.assert_any_call(
            "en", "A new plant called Test plant has been created"
        )

    def test_get_non_existing_plant(self, client):
        response = client.get("/plants/99")
        assert response.status_code == 404

    @patch("app.users.api.UserInfo.get_current")
    def test_get_current_user(self, m_get_user_info, client):
        m_get_user_info.return_value = {
            "aud": ["example"],
            "email": "user@example.com",
            "exp": 1237658,
            "iat": 1237658,
            "iss": "test.example.com",
            "nbf": 1237658,
            "sub": "user",
            "name": "User Name",
        }
        response = client.get(
            "/users/me", headers={"X-Pomerium-Jwt-Assertion": "jwt_assertion"}
        )
        assert response.status_code == 200
        assert response.json() == {
            "aud": ["example"],
            "email": "user@example.com",
            "exp": 1237658,
            "iat": 1237658,
            "iss": "test.example.com",
            "nbf": 1237658,
            "sub": "user",
            "name": "User Name",
        }
        m_get_user_info.assert_called_with("jwt_assertion")

    def test_get_existing_plant(self, client, database_test_session):
        key = uuid.uuid4()
        self._insert_test_plant(database_test_session, {"journaling_key": key})
        response = client.get("/plants/1")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "Test plant",
            "description": "Test Description",
            "water_every": 3,
            "until_next_watering": 3,
            "image": None,
            "journaling_key": str(key),
            "alive": True,
            "last_watering": "2013-04-09T00:00:00",
        }

    def test_create_plant_invalid(self, client):
        response = client.post("/plants", json={"payload": "Invalid"})
        assert response.status_code == 422

    @patch("app.notifications.notifications.Notifications.send")
    def test_water_plant(self, m_send_notification, client, database_test_session):
        key = uuid.uuid4()
        self._insert_test_plant(
            database_test_session,
            {"journaling_key": key, "last_watering": datetime.datetime(2012, 5, 5)},
        )
        response = client.post("/plants/1/water")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "Test plant",
            "description": "Test Description",
            "water_every": 3,
            "until_next_watering": 3,
            "image": None,
            "journaling_key": str(key),
            "alive": True,
            "last_watering": "2013-04-09T00:00:00",
        }
        m_send_notification.assert_any_call(
            "en", "The plant Test plant has been watered"
        )

    @patch("app.notifications.notifications.Notifications.send")
    def test_water_all_plants(self, m_send_notification, client, database_test_session):
        key = uuid.uuid4()
        self._insert_test_plant(
            database_test_session,
            {"journaling_key": key, "last_watering": datetime.datetime(2012, 5, 5)},
        )
        self._insert_test_plant(
            database_test_session,
            {"journaling_key": key, "last_watering": datetime.datetime(2012, 5, 5)},
        )
        response = client.post("/plants/water_all")
        assert response.status_code == 204
        m_send_notification.assert_any_call(
            "en", "The plant Test plant has been watered"
        )

    @patch("app.notifications.notifications.Notifications.send")
    def test_kill_plant(self, m_send_notification, client, database_test_session):
        key = uuid.uuid4()
        self._insert_test_plant(
            database_test_session,
            {"journaling_key": key},
        )
        response = client.post("/plants/1/kill")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "Test plant",
            "description": "Test Description",
            "water_every": 3,
            "until_next_watering": 3,
            "image": None,
            "journaling_key": str(key),
            "alive": False,
            "last_watering": "2013-04-09T00:00:00",
        }
        m_send_notification.assert_any_call("en", "The plant Test plant is now dead")

    def test_get_all_plants(self, client, database_test_session):
        key = uuid.uuid4()
        self._insert_test_plant(database_test_session, {"journaling_key": key})
        self._insert_test_plant(database_test_session, {"journaling_key": key})
        # This one will be excluded
        self._insert_test_plant(
            database_test_session, {"alive": False, "journaling_key": key}
        )
        response = client.get("/plants")
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": 1,
                "name": "Test plant",
                "description": "Test Description",
                "water_every": 3,
                "until_next_watering": 3,
                "image": None,
                "journaling_key": str(key),
                "alive": True,
                "last_watering": "2013-04-09T00:00:00",
            },
            {
                "id": 2,
                "name": "Test plant",
                "description": "Test Description",
                "water_every": 3,
                "until_next_watering": 3,
                "image": None,
                "journaling_key": str(key),
                "alive": True,
                "last_watering": "2013-04-09T00:00:00",
            },
        ]

    def test_get_plants_to_be_watered(self, client, database_test_session):
        key = uuid.uuid4()
        # Two dry plants
        self._insert_test_plant(
            database_test_session, {"water_every": 4, "journaling_key": key}
        )
        self._insert_test_plant(
            database_test_session, {"water_every": 3, "journaling_key": key}
        )
        # Dead plant
        self._insert_test_plant(
            database_test_session, {"water_every": 12, "alive": False}
        )
        # Not a dry plant
        self._insert_test_plant(database_test_session, {"water_every": 5})
        with freeze_time("2013-04-13"):
            response = client.get("/plants/to_be_watered")
        assert response.status_code == 200
        assert response.json() == [
            {
                "name": "Test plant",
                "description": "Test Description",
                "image": None,
                "id": 1,
                "water_every": 4,
                "until_next_watering": 0,
                "journaling_key": str(key),
                "last_watering": "2013-04-09T00:00:00",
                "alive": True,
            },
            {
                "name": "Test plant",
                "description": "Test Description",
                "image": None,
                "id": 2,
                "water_every": 3,
                "until_next_watering": -1,
                "journaling_key": str(key),
                "last_watering": "2013-04-09T00:00:00",
                "alive": True,
            },
        ]

    def test_get_dead_plants(self, client, database_test_session):
        key = uuid.uuid4()
        self._insert_test_plant(database_test_session, {"journaling_key": key})
        self._insert_test_plant(database_test_session, {"journaling_key": key})
        # Only this one will be included
        self._insert_test_plant(
            database_test_session, {"alive": False, "journaling_key": key}
        )
        response = client.get("/plants/dead")
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": 3,
                "name": "Test plant",
                "description": "Test Description",
                "water_every": 3,
                "until_next_watering": 3,
                "image": None,
                "journaling_key": str(key),
                "alive": False,
                "last_watering": "2013-04-09T00:00:00",
            },
        ]

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

    def test_updating_plant(self, client, database_test_session):
        key = uuid.uuid4()
        original_plant = self._insert_test_plant(
            database_test_session, {"name": "Some name", "journaling_key": key}
        )
        response = client.put(
            "/plants/1",
            json={
                "name": "Updated name",
                "description": original_plant.description,
                "journaling_key": str(key),
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "Updated name",
            "description": "Test Description",
            "last_watering": "2013-04-09T00:00:00",
            "water_every": 3,
            "until_next_watering": 3,
            "alive": True,
            "image": None,
            "journaling_key": str(key),
        }

    @patch("requests.get")
    def test_get_image(self, m_get, client):
        m_get.return_value = Mock()
        m_get.return_value.content = "image_binary_data"
        response = client.get("/image/image_path/extra")
        # TODO: Change this assertion once the image service is done
        # m_get.assert_called_with("http://images-service:80/image/image_path")
        assert response.status_code == 200
        assert response.content == b"image_binary_data"

    def test_updating_watering_schedule(self, client, database_test_session):
        key = uuid.uuid4()
        self._insert_test_plant(database_test_session, {"journaling_key": key})
        response = client.post(
            "/plants/1/water_every",
            json={"days": 5},
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "Test plant",
            "description": "Test Description",
            "last_watering": "2013-04-09T00:00:00",
            "water_every": 5,
            "until_next_watering": 5,
            "alive": True,
            "image": None,
            "journaling_key": str(key),
        }

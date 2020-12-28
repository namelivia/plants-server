from mock import patch, Mock
from .test_base import (
    client,
    create_test_database,
    database_test_session,
)
from app.plants.models import Plant


class TestApp:

    def _insert_test_plant(self, session):
        db_plant = Plant(
            name='Test plant',
            description='Test Description',
            days_until_watering=3,
        )
        session.add(db_plant)
        session.commit()

    def test_create_plant_description(self, client):
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
        }

    def test_create_plant_no_description(self, client):
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
        }

    def test_get_non_existing_plant(self, client):
        response = client.get("/plants/99")
        assert response.status_code == 404

    def test_get_existing_plant(self, client, database_test_session):
        self._insert_test_plant(database_test_session)
        response = client.get("/plants/1")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "Test plant",
            "description": 'Test Description',
            "days_until_watering": 3,
            "image": None,
        }

    def test_create_plant_invalid(self, client):
        response = client.post("/plants", json={
            'payload': 'Invalid'
        })
        assert response.status_code == 422

    def test_get_all_plants(self, client, database_test_session):
        self._insert_test_plant(database_test_session)
        self._insert_test_plant(database_test_session)
        response = client.get("/plants")
        assert response.status_code == 200
        assert response.json() == [{
            "id": 1,
            "name": "Test plant",
            "description": 'Test Description',
            "days_until_watering": 3,
            "image": None,
        }, {
            "id": 2,
            "name": "Test plant",
            "description": 'Test Description',
            "days_until_watering": 3,
            "image": None,
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

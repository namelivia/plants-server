from mock import patch, Mock
import uuid
from app.notifications.notifications import Notifications
from app.journaling.journaling import Journaling


class TestServices:

    @patch("requests.post")
    def test_sending_a_notification(self, m_post):
        Notifications.send("Test message")
        m_post.assert_called_with(
            url='http://notifications-service:80',
            json={
                'message': 'Test message'
            },
        )

    @patch("requests.post")
    def test_creating_a_journal_entry(self, m_post):
        key = uuid.uuid4()
        message = "Test message"
        Journaling.create(key, message)
        m_post.assert_called_with(
            url='http://journaling-service:80/new',
            json={
                'key': str(key),
                'message': message,
            },
        )

    @patch("requests.get")
    def test_retrieving_a_journal_entryset(self, m_get):
        key = uuid.uuid4()
        response_mock = Mock()
        response_mock.text = '{"data": "journaling_data"}'
        response_mock.json = lambda: {"data": "journaling_data"}
        m_get.return_value = response_mock
        response = Journaling.get(key)
        m_get.assert_called_with(
            url=f"http://journaling-service:80/{str(key)}/all",
        )
        assert response['data'] == 'journaling_data'

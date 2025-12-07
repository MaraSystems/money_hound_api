from fastapi import status
from httpx import AsyncClient
from pymongo.database import Database
from bson import ObjectId
import pytest

from src.domains.notifications.notify_user import notify_user
from src.domains.notifications.model import CreateNotification
from src.domains.roles.model import CreateRole
from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestGetNotificationEndpoint(TestFixture):
    async def test_get_notification_success(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        notification = await self._create_notification(test_db)

        get_resp = await async_client.get(f"/notifications/{notification['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert get_resp.status_code == 200

        data = get_resp.json()
        assert data['data']['_id'] == str(notification['_id'])
        assert data['data']['subject'] == notification['subject']

    
    async def test_get_notification_not_found(self, async_client: AsyncClient, test_db):
        await self._set_up(test_db)
        missing_id = str(ObjectId())
        response = await async_client.get(f'/notifications/{missing_id}', headers={'Authorization': f'Bearer {self.token}'})
        assert response.status_code == 404
        assert response.json()['message'] == f'Notification not found: {missing_id}'

    
    async def test_get_notification_private_unathorized(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        notification = await self._create_notification(test_db, CreateNotification(**{**self.notification_data.model_dump(), 'public': False, 'subject': 'Private'}))

        response = await async_client.get(f"/notifications/{notification['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()['message'] == f"You are unauthorized to read this notification: {notification['_id']}"
        

    async def test_get_notification_private_authroized(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        notification = await self._create_notification(test_db, CreateNotification(**{**self.notification_data.model_dump(), 'public': False, 'subject': 'Private'}))

        await notify_user(notification['_id'], str(self.user['_id']), test_db, test_cache)
        
        get_resp = await async_client.get(f"/notifications/{notification['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert get_resp.status_code == 200

        data = get_resp.json()
        assert data['data']['_id'] == str(notification['_id'])
        assert data['data']['subject'] == notification['subject']
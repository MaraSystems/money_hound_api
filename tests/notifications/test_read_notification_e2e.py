from httpx import AsyncClient
import pytest
from fastapi import HTTPException, status
from pymongo.database import Database
from bson import ObjectId

from src.domains.notifications.create_notification import create_notification
from src.domains.notifications.model import CreateNotification
from src.domains.notifications.notify_user import notify_user
from src.lib.utils.response import DataResponse
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestNotifiyUserService(TestFixture):
    async def test_notify_user_success(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)
        notification = await self._create_notification(test_db)
        
        response = await async_client.put(f"/notifications/{notification['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        response_data: DataResponse[None] = response.json()
        assert response_data['message'] == 'User read notification successfully'

        updated_notification = await test_db.notifications.find_one({'_id': notification['_id']})
        assert str(self.user['_id']) in updated_notification['readers']


    async def test_read_notification_not_found(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)
        missing_notification = ObjectId()

        response = await async_client.put(f"/notifications/{missing_notification}", headers={'Authorization': f'Bearer {self.token}'})
        assert response.status_code == 404

        response_data = response.json()
        assert response_data['message'] == f"Notification not found: {missing_notification}"

    
    async def test_read_notification_private_success(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        notification = await self._create_notification(test_db, CreateNotification(**{**self.notification_data.model_dump(), 'public': False, 'subject': 'Private'}))

        notify_user(notification['_id'], str(self.user['_id']), test_db, test_cache)

        response = await async_client.put(f"/notifications/{notification['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        response_data: DataResponse[None] = response.json()
        assert response_data['message'] == 'User read notification successfully'

        updated_notification = await test_db.notifications.find_one({'_id': notification['_id']})
        assert str(self.user['_id']) in updated_notification['readers']


    async def test_read_notification_private_success(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)
        notification = await self._create_notification(test_db, CreateNotification(**{**self.notification_data.model_dump(), 'public': False, 'subject': 'Private'}))

        response = await async_client.put(f"/notifications/{notification['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert response.status_code == 401

        response_data = response.json()
        assert response_data['message'] == f"You are unauthorized to read this notification: {notification['_id']}"

from datetime import datetime, timedelta
from httpx import AsyncClient
import pytest
from fastapi import HTTPException, status
from pymongo.database import Database
from bson import ObjectId

from src.domains.notifications.create_notification import create_notification
from src.domains.notifications.model import CreateNotification, Notification
from src.lib.utils.response import DataResponse
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestCreateNotificationEndpoint(TestFixture):
    async def test_create_notification_success(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)

        notification_data = {
            'subject': 'Sample',
            'message': 'Welcome message',
            'category': 'message'
        }
        
        create_response = await async_client.post(
            '/notifications',
            json=notification_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 201
        response_data: DataResponse[None] = create_response.json()
        assert response_data['message'] == 'Notification created successfully'

        notifications = await test_db.notifications.find({}).to_list()
        titles = [i['subject'] for i in notifications]
        assert self.notification_data.subject in titles
        assert notifications[0]['users'] == None


    async def test_create_notification_private(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)
        notification_data = {
            'subject': 'Sample',
            'message': 'Welcome message',
            'category': 'message',
            'public': False
        }
        
        create_response = await async_client.post(
            '/notifications',
            json=notification_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 201
        response_data: DataResponse[None] = create_response.json()
        assert response_data['message'] == 'Notification created successfully'

        notifications = await test_db.notifications.find({}).to_list()
        assert notifications[0]['public'] == False
        assert notifications[0]['users'] == []


    async def test_create_notification_expiry(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)
        expiry = (datetime.now() + timedelta(days=1)).isoformat()
        notification_data = {
            'subject': 'Sample',
            'message': 'Welcome message',
            'category': 'message',
            'expires_at': expiry
        }
        
        create_response = await async_client.post(
            '/notifications',
            json=notification_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 201
        response_data: DataResponse[None] = create_response.json()
        assert response_data['message'] == 'Notification created successfully'

        notifications = await test_db.notifications.find({}).to_list()
        assert notifications[0]['expires_at'] - datetime.fromisoformat(expiry) < timedelta(seconds=1)


    async def test_create_notification_past_expiry(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)
        expiry = (datetime.now() - timedelta(days=1)).isoformat()
        notification_data = {
            'subject': 'Sample',
            'message': 'Welcome message',
            'category': 'message',
            'expires_at': expiry
        }
        
        create_response = await async_client.post(
            '/notifications',
            json=notification_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 400
        response_data = create_response.json()
        assert response_data['message'] == f'Notification must expire in the future: {datetime.fromisoformat(expiry)}'

 
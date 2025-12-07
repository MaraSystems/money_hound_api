from datetime import datetime, timedelta
from httpx import AsyncClient
import pytest
from pymongo.database import Database
from freezegun import freeze_time

from src.domains.notifications.create_notification import create_notification
from src.domains.notifications.list_notifications import list_notification
from src.domains.notifications.model import CreateNotification, ListNotifications
from src.domains.notifications.notify_user import notify_user
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestListNotificationEndpoint(TestFixture):
    
    async def test_list_notification_empty(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)

        response = await async_client.get(f"/notifications", headers={'Authorization': f'Bearer {self.token}'})
        assert response.status_code == 200
        data = response.json()
        assert len(data['data']) == 0


    async def test_list_notification_populated(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)
        await self._create_notification(test_db)
        await self._create_notification(test_db, CreateNotification(**{**self.notification_data.model_dump(), 'public': False, 'subject': 'Private'}))

        response = await async_client.get(f"/notifications", headers={'Authorization': f'Bearer {self.token}'})
        assert response.status_code == 200
        data = response.json()
        assert len(data['data']) == 1

        titles = [i['subject'] for i in data['data']]
        assert self.notification_data.subject in titles


    async def test_list_notification_private(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        await self._create_notification(test_db)
        private = await self._create_notification(test_db, CreateNotification(**{**self.notification_data.model_dump(), 'public': False, 'subject': 'Private'}))

        await notify_user(private['_id'], str(self.user['_id']), test_db, test_cache)

        response = await async_client.get(f"/notifications", headers={'Authorization': f'Bearer {self.token}'})
        notifications = response.json()['data']
        assert len(notifications) == 2

        titles = [i['subject'] for i in notifications]
        assert self.notification_data.subject in titles
        assert 'Private' in titles


    async def test_list_notification_filtered(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)
        await self._create_notification(test_db)
        await self._create_notification(test_db, CreateNotification(**{**self.notification_data.model_dump(), 'subject': 'Another'}))

        response = await async_client.get(f"/notifications?query=ano", headers={'Authorization': f'Bearer {self.token}'})
        notifications = response.json()['data']
        assert len(notifications) == 1

        titles = [i['subject'] for i in notifications]
        assert self.notification_data.subject not in titles
        assert 'Another' in titles


    async def test_list_notification_paginated(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)
        for i in range(5):
            await self._create_notification(test_db, CreateNotification(**{**self.notification_data.model_dump(), 'subject': f'Notification_{i}'}))

        response = await async_client.get(f"/notifications?limit=2", headers={'Authorization': f'Bearer {self.token}'})
        notifications = response.json()['data']
        assert len(notifications) == 2

        response = await async_client.get(f"/notifications?limit=2&skip=4", headers={'Authorization': f'Bearer {self.token}'})
        notifications = response.json()['data']
        assert len(notifications) == 1


    async def test_list_notification_not_expired(self, async_client: AsyncClient, test_db: Database):
        expiry = (datetime.now() + timedelta(days=1)).isoformat()

        await self._set_up(test_db)
        await self._create_notification(test_db)
        await self._create_notification(test_db, CreateNotification(**{**self.notification_data.model_dump(), 'expires_at': expiry}))

        response = await async_client.get(f"/notifications", headers={'Authorization': f'Bearer {self.token}'})
        notifications = response.json()['data']
        assert len(notifications) == 2


    async def test_list_notification_expired(self, async_client: AsyncClient, test_db: Database):
        now = datetime.now()
        
        with freeze_time(now):
            expiry = (now + timedelta(days=1)).isoformat()
            await self._create_notification(test_db)
            await self._create_notification(test_db, CreateNotification(**{**self.notification_data.model_dump(), 'expires_at': expiry}))
        
        with freeze_time(now + timedelta(days=2)):
            await self._set_up(test_db)
            response = await async_client.get(f"/notifications", headers={'Authorization': f'Bearer {self.token}'})
            notifications = response.json()['data']
            assert len(notifications) == 1

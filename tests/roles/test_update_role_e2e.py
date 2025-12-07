from httpx import AsyncClient
from pymongo.database import Database
import pytest

from src.domains.roles.model import CreateRole
from src.domains.users.model import User
from tests.fixture_spec import TestFixture

@pytest.mark.asyncio
class TestUpdateRoleEndpoint(TestFixture):
    async def test_update_role_success(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        update_payload = {
            'title': 'Updated Admin',
            'description': 'Updated administrator role'
        }
        resp = await async_client.patch(f"/roles/{self.role['_id']}", json=update_payload, headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        assert data['data']['title'] == 'Updated Admin'
        assert data['data']['description'] == 'Updated administrator role'
        assert data['message'] == 'Role updated successfully'


    async def test_update_role_partial(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)

        update_payload = {'title': 'Admin v2'}
        resp = await async_client.patch(f"/roles/{self.role['_id']}", json=update_payload, headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        assert data['data']['title'] == 'Admin v2'

        assert data['data']['description'] == 'Administrator role'
        assert data['data']['permissions'] == ['*:*:*']


    async def test_update_role_duplicate_title_conflict(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        r2 = await self._create_role(test_db, self.user['_id'], CreateRole(**{**self.role_data.model_dump(), 'title': 'User'}))

        resp = await async_client.patch(f"/roles/{r2['_id']}", json={'title': 'Admin'}, headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 409
        assert resp.json()['message'] == 'Role title not available: Admin'


    async def test_update_role_same_title_allowed(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        resp = await async_client.patch(f"/roles/{self.role['_id']}", json={'title': 'Admin', 'description': 'Updated'}, headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        assert data['data']['title'] == 'Admin'
        assert data['data']['description'] == 'Updated'
        assert data['message'] == 'Role updated successfully'


    async def test_update_role_clear_permissions(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        resp = await async_client.patch(f"/roles/{self.role['_id']}", json={'permissions': []}, headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        assert data['data']['permissions'] == []
        assert data['message'] == 'Role updated successfully'

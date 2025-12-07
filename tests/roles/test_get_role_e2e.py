from httpx import AsyncClient
from pymongo.database import Database
from bson import ObjectId
import pytest

from src.domains.roles.model import CreateRole
from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestGetRoleEndpoint(TestFixture):
    async def test_get_role_success(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)

        get_resp = await async_client.get(f"/roles/{self.role['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data['data']['_id'] == str(self.role['_id'])
        assert data['data']['title'] == 'Admin'
        assert data['message'] is None or data['message'] == ''


    async def test_get_role_not_found(self, async_client: AsyncClient, test_db):
        await self._set_up(test_db)
        missing_id = str(ObjectId())
        get_resp = await async_client.get(f'/roles/{missing_id}', headers={'Authorization': f'Bearer {self.token}'})
        assert get_resp.status_code == 404
        assert get_resp.json()['message'] == f'Role not found: {missing_id}'


    async def test_get_role_hidden_returns_404(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)

        # Soft-delete (hide) the role
        del_resp = await async_client.delete(f"/roles/{self.role['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert del_resp.status_code == 200

        # Now fetching should return 404 because hidden roles are excluded
        get_resp = await async_client.get(f"/roles/{self.role['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert get_resp.status_code == 404
        assert get_resp.json()['message'] == f"Role not found: {self.role['_id']}"

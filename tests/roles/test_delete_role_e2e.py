from bson import ObjectId
from httpx import AsyncClient
from pymongo.database import Database
import pytest

from src.domains.roles.model import CreateRole
from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestDeleteRoleEndpoint(TestFixture):
    async def test_delete_role_success(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)

        del_resp = await async_client.delete(f"/roles/{self.role['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert del_resp.status_code == 200
        assert del_resp.json()['message'] == 'Role deleted successfully'

        get_resp2 = await async_client.get(f"/roles/{self.role['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert get_resp2.status_code == 404


    async def test_delete_role_not_found(self, async_client: AsyncClient, test_db):
        await self._set_up(test_db)
        missing_id = '66f2f2f2f2f2f2f2f2f2f2f2'  # any ObjectId-like string
        del_resp = await async_client.delete(f"/roles/{missing_id}", headers={'Authorization': f'Bearer {self.token}'})
        assert del_resp.status_code == 404
        assert del_resp.json()['message'].startswith('Role not found:')


    async def test_delete_role_preserves_other_fields(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)

        del_resp = await async_client.delete(f"/roles/{self.role['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert del_resp.status_code == 200

        stored = await test_db.roles.find_one({'_id': self.role['_id']})
        assert stored['title'] == self.role['title']
        assert stored['description'] == self.role['description']
        assert stored['permissions'] == ['*:*:*']
        assert stored['hidden'] is True

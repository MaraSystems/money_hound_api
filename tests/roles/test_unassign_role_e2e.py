from httpx import AsyncClient
from pymongo.database import Database
from bson import ObjectId
import pytest

from src.domains.roles.model import CreateRole
from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestUnassignRoleEndpoint(TestFixture):
    async def test_unassign_role_success(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        new_role = await self._create_role(test_db, self.user['_id'], CreateRole(**{**self.role_data.model_dump(), 'title': 'User'}))
        await self._assign_role(test_db, new_role['_id'], self.user['_id'])

        unassign_resp = await async_client.delete(f"/roles/{new_role['_id']}/unassign/{self.user['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert unassign_resp.status_code == 200
        assert unassign_resp.json()['message'] == 'Role unassigned from user successfully'

        resp = await async_client.get(f"/roles/{new_role['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        role = resp.json()
        assert self.user['_id'] not in new_role['users']


    async def test_unassign_role_unauthorized(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)

        # Attempt unassign without auth header
        resp = await async_client.delete(f"/roles/{self.role['_id']}/unassign/{self.user['_id']}")
        assert resp.status_code == 401
        assert 'message' in resp.json()


    async def test_unassign_role_not_found(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)
        missing_role_id = str(ObjectId())

        resp = await async_client.delete(f"/roles/{missing_role_id}/unassign/{self.user['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 404
        assert resp.json()['message'] == f"Role not found: {missing_role_id}"


    async def test_unassign_role_not_assigned_idempotent(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        new_role = await self._create_role(test_db, self.user['_id'], CreateRole(**{**self.role_data.model_dump(), 'title': 'User'}))

        # Unassign even though not assigned should still succeed (idempotent $pull)
        resp = await async_client.delete(f"/roles/{new_role['_id']}/unassign/{self.user['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        assert resp.json()['message'] == 'Role unassigned from user successfully'

from httpx import AsyncClient
from pymongo.database import Database
from bson import ObjectId
from pytest import mark
import pytest

from src.domains.auth.model import CreateUser
from src.domains.roles.model import CreateRole
from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestAssignRoleEndpoint(TestFixture):
    async def test_assign_role_success(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        
        response = await async_client.post(f"/roles/{self.role['_id']}/assign/{self.user['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert response.status_code == 200
        assert response.json()['message'] == 'Role assigned to user successfully'
        
        response = await async_client.get(f"/roles/{self.role['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        
        role = response.json()['data']
        assert role['author_id'] in role['users']


    async def test_assign_role_unauthorized(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)

        response = await async_client.post(f"/roles/{self.role['_id']}/assign/{self.user['_id']}")
        assert response.status_code == 401
        assert 'message' in response.json()


    async def test_assign_role_not_found(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)
        missing_role_id = str(ObjectId())

        response = await async_client.post(f"/roles/{missing_role_id}/assign/{self.user['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert response.status_code == 404
        assert response.json()['message'] == f"Role not found: {missing_role_id}"


    async def test_assign_role_duplicate_push(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)

        # Assign twice; implementation uses $push so duplicates will appear
        response1 = await async_client.post(f"/roles/{self.role['_id']}/assign/{self.user['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert response1.status_code == 200
        response2 = await async_client.post(f"/roles/{self.role['_id']}/assign/{self.user['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert response2.status_code == 200

        response = await async_client.get(f"/roles/{self.role['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        role = response.json()['data']
        assert role['users'].count(str(self.user['_id'])) == 1

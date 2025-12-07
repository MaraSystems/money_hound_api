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
class TestGetUserEndpoint(TestFixture):
    async def test_get_user_success(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)

        resp = await async_client.get(f"/users/{self.user['_id']}", headers={"Authorization": f"Bearer {self.token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["_id"] == str(self.user['_id'])
        assert data["data"]["email"] == self.user['email']


    async def test_get_user_unauthorized(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)

        resp = await async_client.get(f"/users/{self.user['_id']}")
        assert resp.status_code == 401
        assert "message" in resp.json()


    async def test_get_user_forbidden_without_permission(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db, role=CreateRole(**{**self.role_data.model_dump(), 'permissions': []}))

        resp = await async_client.get(f"/users/{self.user['_id']}", headers={"Authorization": f"Bearer {self.token}"})
        assert resp.status_code == 403
        assert resp.json()["message"] == "Not Authorized"
        

    async def test_get_user_not_found(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        missing_id = str(ObjectId())
        
        resp = await async_client.get(f"/users/{missing_id}", headers={"Authorization": f"Bearer {self.token}"})
        assert resp.status_code == 404
        assert resp.json()["message"] == f"User not found: {missing_id}"

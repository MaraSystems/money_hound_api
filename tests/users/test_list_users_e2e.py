from bson import ObjectId
from httpx import AsyncClient
from pymongo.database import Database
import pytest

from src.domains.auth.delete_profile import delete_profile
from src.domains.auth.model import CreateUser
from src.domains.roles.model import CreateRole
from src.domains.users.list_users import list_users
from src.domains.users.model import ListUsers
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestListUsersEndpoint(TestFixture):
    async def test_list_users_populated(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)
        await self._create_user(test_db, CreateUser(**{**self.user_data.model_dump(), 'email': 'r@r.r'}))

        resp = await async_client.get(f"/users", headers={"Authorization": f"Bearer {self.token}"})
        data = resp.json()['data']
        emails = [u["email"] for u in data]
        assert "m@m.m" in emails
        assert "r@r.r" in emails


    async def test_list_users_query_filter(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)
        await self._create_user(test_db, CreateUser(**{**self.user_data.model_dump(), 'email': 'r@r.r'}))
        
        resp = await async_client.get(f"/users?query=m", headers={"Authorization": f"Bearer {self.token}"})
        data = resp.json()['data']
        assert len(data) == 1
        assert data[0]["email"] == "m@m.m"


    async def test_list_users_excludes_hidden(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        user = await self._create_user(test_db, CreateUser(**{**self.user_data.model_dump(), 'email': 'r@r.r'}))

        await delete_profile(user['_id'], test_db, test_cache)

        resp = await async_client.get(f"/users?query=m", headers={"Authorization": f"Bearer {self.token}"})
        data = resp.json()['data']
        emails = [u["email"] for u in data]
        assert "r@r.r" not in emails
        assert "m@m.m" in emails


    async def test_list_users_pagination(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)
        for i in range(4):
            await self._create_user(test_db, CreateUser(**{**self.user_data.model_dump(), 'email': f'r_{i}@r.r'}))

        resp1 = await async_client.get(f"/users?limit=2", headers={"Authorization": f"Bearer {self.token}"})
        data1 = resp1.json()['data']
        assert len(data1) == 2

        resp2 = await async_client.get(f"/users?limit=2&skip-2", headers={"Authorization": f"Bearer {self.token}"})
        data2 = resp2.json()['data']
        assert len(data2) == 2

    
    async def test_list_users_unauthorized(self, async_client: AsyncClient):
        resp = await async_client.get(f"/users")
        assert resp.status_code == 401
        assert "message" in resp.json()


    async def test_list_users_forbidden_without_permission(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db, role=CreateRole(**{**self.role_data.model_dump(), 'permissions': []}))

        resp = await async_client.get(f"/users", headers={"Authorization": f"Bearer {self.token}"})
        assert resp.status_code == 403
        assert resp.json()["message"] == "Not Authorized"

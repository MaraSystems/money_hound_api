from httpx import AsyncClient
from pymongo.database import Database
from bson import ObjectId
from pytest import mark
import pytest

from src.domains.roles.model import CreateRole
from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestListRolesEndpoint(TestFixture):
    async def test_list_roles_success(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        await self._create_role(test_db, self.user['_id'], CreateRole(**{**self.role_data.model_dump(), 'title': 'User'}))

        resp = await async_client.get('/roles', headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data['data'], list)
        titles = [r['title'] for r in data['data']]
        assert 'Admin' in titles
        assert 'User' in titles


    async def test_list_roles_query_filter(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        await self._create_role(test_db, self.user['_id'], CreateRole(**{**self.role_data.model_dump(), 'title': 'User'}))

        resp = await async_client.get('/roles?query=adm', headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['data']) >= 1
        assert data['data'][0]['title'] == 'Admin'


    async def test_list_roles_excludes_hidden(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        hidden = await self._create_role(test_db, self.user['_id'], CreateRole(**{**self.role_data.model_dump(), 'title': 'User'}))
        
        # Soft delete the hidden one
        del_resp = await async_client.delete(f"/roles/{hidden['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert del_resp.status_code == 200

        resp = await async_client.get('/roles', headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        titles = [r['title'] for r in data['data']]
        assert 'Admin' in titles
        assert 'User' not in titles


    async def test_list_roles_pagination(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)

        # Create 5 roles
        for i in range(5):
            await self._create_role(test_db, self.user['_id'], CreateRole(**{**self.role_data.model_dump(), 'title': f'Role_{i}'}))

        # Limit
        resp = await async_client.get('/roles?limit=2', headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['data']) == 2

        # Skip + limit
        resp2 = await async_client.get('/roles?skip=2&limit=2', headers={'Authorization': f'Bearer {self.token}'})
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert len(data2['data']) == 2

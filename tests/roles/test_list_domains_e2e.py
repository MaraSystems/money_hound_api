from httpx import AsyncClient
from pymongo.database import Database
import pytest

from src.domains.auth.model import CreateUser
from src.domains.roles.model import CreateRole
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestListDomainsEndpoint(TestFixture):
    async def test_list_domains_success(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)

        response = await async_client.get('/roles/domains', headers={'Authorization': f'Bearer {self.token}'})
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'data' in data
        assert 'message' in data
        assert isinstance(data['data'], list)
        assert len(data['data']) == 7
        

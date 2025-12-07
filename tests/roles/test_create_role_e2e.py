from httpx import AsyncClient
from pymongo.database import Database
import pytest

from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestCreateRoleEndpoint(TestFixture):
    async def test_create_role_success(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)

        role_data = {
            'title': 'Random',
            'description': 'Administrator role',
            'permissions': ['*:*:*']
        }
        
        create_response = await async_client.post(
            '/roles',
            json=role_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 201
        response_data = create_response.json()
        
        assert 'data' in response_data
        assert 'message' in response_data
        assert response_data['data']['title'] == 'Random'
        assert response_data['data']['description'] == 'Administrator role'
        assert response_data['data']['permissions'] == ['*:*:*']
        assert response_data['data']['author_id'] is not None
        assert response_data['message'] == 'Role created successfully: Random'


    async def test_create_role_duplicate_title(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)

        role_data = {
            'title': 'Admin',
            'description': 'Administrator role',
            'permissions': ['*:*:*']
        }
        
        response = await async_client.post(
            '/roles',
            json=role_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert response.status_code == 409
        response_data = response.json()
        assert response_data['message'] == 'Role title not available: Admin'


    async def test_create_role_minimal_data(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)

        role_data = {
            'title': 'User',
            'permissions': ['*:*:*']
        }
        
        create_response = await async_client.post(
            '/roles',
            json=role_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 201
        response_data = create_response.json()
        
        assert response_data['data']['title'] == 'User'
        assert response_data['data']['description'] is None
        assert response_data['data']['permissions'] == ['*:*:*']
        assert response_data['message'] == 'Role created successfully: User'


    async def test_create_role_unauthorized(self, async_client: AsyncClient):
        role_data = {
            'title': 'Admin',
            'description': 'Administrator role',
            'permissions': ['*:*:*']
        }
        
        create_response = await async_client.post('/roles', json=role_data)
        
        assert create_response.status_code == 401
        response_data = create_response.json()
        assert 'message' in response_data


    async def test_create_role_invalid_token(self, async_client: AsyncClient):
        role_data = {
            'title': 'Admin',
            'description': 'Administrator role',
            'permissions': ['*:*:*']
        }
        
        create_response = await async_client.post(
            '/roles',
            json=role_data,
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        assert create_response.status_code == 401
        response_data = create_response.json()
        assert response_data['message'] == 'Token is invalid'


    async def test_create_role_validation_errors(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)

        # Test: Create role with missing required fields
        invalid_role_data = {
            'description': 'Role without title'
        }
        
        create_response = await async_client.post(
            '/roles',
            json=invalid_role_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 422
        assert create_response.json()['message'] == '\'title\': Field required'

from httpx import AsyncClient
from pymongo.database import Database
import pytest

from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestSimulateTransactionsEndpoint(TestFixture):
    async def test_create_simulation_success(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)

        simulation_data = {
            'num_banks':2,
            'min_num_user':5,
            'fraudulence':.05,
            'latitude':9,
            'longitude':3,
            'radius':5000,
            'min_amount':100,
            'max_amount':10000,
            'days':1
        }

        create_response = await async_client.post(
            '/simulations',
            json=simulation_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 201
        response_data = create_response.json()
        
        assert 'data' in response_data
        assert 'message' in response_data
        assert response_data['data']['status'] == 'PENDING'
        assert response_data['data']['author_id'] is not None
        assert response_data['message'] == 'Simulation initiated successfully'


    async def test_create_role_unauthorized(self, async_client: AsyncClient):
        simulation_data = {
            'num_banks':2,
            'min_num_user':5,
            'fraudulence':.05,
            'latitude':9,
            'longitude':3,
            'radius':5000,
            'min_amount':100,
            'max_amount':10000,
            'days':1
        }
        
        create_response = await async_client.post(
            '/simulations',
            json=simulation_data
        )
        
        assert create_response.status_code == 401
        response_data = create_response.json()
        assert 'message' in response_data


    async def test_create_simulation_invalid_token(self, async_client: AsyncClient):
        simulation_data = {
            'num_banks':2,
            'min_num_user':5,
            'fraudulence':.05,
            'latitude':9,
            'longitude':3,
            'radius':5000,
            'min_amount':100,
            'max_amount':10000,
            'days':1
        }
        
        create_response = await async_client.post(
            '/simulations',
            json=simulation_data,
            headers={'Authorization': f'Bearer invalid_token'}
        )
        
        assert create_response.status_code == 401
        response_data = create_response.json()
        assert response_data['message'] == 'Token is invalid'
        

    async def test_create_simulation_validation_errors(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)

        # Test: Create role with missing required fields
        invalid_simulation_data = {
            'min_num_user':10,
            'fraudulence':.05,
            'latitude':9,
            'longitude':3,
            'radius':5000,
            'min_amount':100,
            'max_amount':1000000,
            'days':7
        }
        
        create_response = await async_client.post(
            '/simulations',
            json=invalid_simulation_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 422
        assert create_response.json()['message'] == '\'num_banks\': Field required'

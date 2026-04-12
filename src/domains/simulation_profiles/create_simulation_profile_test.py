from httpx import AsyncClient
from pymongo import DESCENDING
from pymongo.database import Database
import pytest
from redis import Redis

from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestCreateSimulationProfileEndpoint(TestFixture):
    async def test_create_simulation_prfofile_success(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)

        simulation_profile_data = {
            'name': 'Random',
            'gender': 'Male',
            'email': 'r@r.r',
            'birthdate': '1990-01-01T00:00:00',
            'devices': ['iPhone', 'Android'],
            'latitude': 37.7749,
            'longitude': -122.4194,
            'simulation_id': simulation['_id']
        }

        create_response = await async_client.post(
            '/simulation_profiles',
            json=simulation_profile_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 201
        response_data = create_response.json()
        
        assert 'data' in response_data
        assert 'message' in response_data
        assert 'user_id' in response_data['data']
        assert response_data['message'] == 'Simulation Profile created successfully'


    async def test_create_simulation_prfofile_unavailable_email(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)
        user = await test_db.simulation_profiles.find_one({'simulation_id': simulation['_id']})

        simulation_profile_data = {
            'name': 'Random',
            'gender': 'Male',
            'email': user['email'],
            'birthdate': '1990-01-01T00:00:00',
            'devices': ['iPhone', 'Android'],
            'latitude': 37.7749,
            'longitude': -122.4194,
            'simulation_id': simulation['_id']
        }

        create_response = await async_client.post(
            '/simulation_profiles',
            json=simulation_profile_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 409
        response_data = create_response.json()
        assert response_data['message'] == f"Simulation Email not available: {user['email']}"


    async def test_create_simulation_prfofile_validation_errors(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)

        simulation_profile_data = {
            'gender': 'Male',
            'email': 'r@r.r',
            'birthdate': '1990-01-01T00:00:00',
            'devices': ['iPhone', 'Android'],
            'latitude': 37.7749,
            'longitude': -122.4194,
            'simulation_id': simulation['_id']
        }

        create_response = await async_client.post(
            '/simulation_profiles',
            json=simulation_profile_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 422
        assert create_response.json()['message'] == '\'name\': Field required'

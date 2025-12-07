from httpx import AsyncClient
from pymongo.database import Database
import pytest

from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestGetProfileEndpoint(TestFixture): 
	async def test_get_profile(self, async_client: AsyncClient, test_db: Database, test_cache):
		await test_db.users.insert_one(self.user_data.model_dump())
		request_response = await async_client.get(f'/auth/request?email={self.user_data.email}')
		assert request_response.status_code == 200

		code = await test_cache.get(f'OTP:{self.user_data.email}')
		verify_response = await async_client.post('/auth/verify', json={'email': self.user_data.email, 'code': code})
		assert verify_response.status_code == 201
		token = verify_response.json()['data']['token']

		get_response = await async_client.get('/auth/profile', headers={'Authorization': f'Bearer {token}'})
		assert get_response.status_code == 200
		profile_data = get_response.json()
		assert profile_data['data']['email'] == self.user_data.email


	async def test_get_profile_invalid_token(self, async_client: AsyncClient, test_db: Database, test_cache):
		get_response = await async_client.get('/auth/profile', headers={'Authorization': f'Bearer token'})
		assert get_response.status_code == 401
		assert get_response.json()['message'] == 'Token is invalid'

from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase
import pytest

from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestDeleteProfileEndpoint(TestFixture): 
	async def test_delete_profile(self, async_client: AsyncClient, test_db: AsyncIOMotorDatabase, test_cache):
		await test_db.users.insert_one(self.user_data.model_dump())
		request_response = await async_client.get(f'/auth/request?email={self.user_data.email}')
		assert request_response.status_code == 200

		code = await test_cache.get(f'OTP:{self.user_data.email}')
		verify_response = await async_client.post('/auth/verify', json={'email': self.user_data.email, 'code': code})
		assert verify_response.status_code == 201
		token = verify_response.json()['data']['token']

		update_response = await async_client.delete('/auth/profile', headers={'Authorization': f'Bearer {token}'})
		assert update_response.status_code == 200
		update_data = update_response.json()
		assert update_data['message'] == 'Profile deleted successfully'
	
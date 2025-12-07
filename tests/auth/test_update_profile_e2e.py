from httpx import AsyncClient
from pymongo.database import Database
import pytest

from src.domains.users.model import User
from tests.fixture_spec import TestFixture


class TestUpdateProfileEndpoint(TestFixture): 
	@pytest.mark.asyncio
	async def test_update_profile(self, async_client: AsyncClient, test_db: Database, test_cache):
		await self._create_user(test_db)
		request_response = await async_client.get(f'/auth/request?email={self.user_data.email}')
		assert request_response.status_code == 200

		code = await test_cache.get(f'OTP:{self.user_data.email}')
		verify_response = await async_client.post('/auth/verify', json={'email': self.user_data.email, 'code': code})
		assert verify_response.status_code == 201
		token = verify_response.json()['data']['token']

		updated_firstname = 'UpdatedName'
		update_response = await async_client.patch('/auth/profile', json={'firstname': updated_firstname}, headers={'Authorization': f'Bearer {token}'})

		assert update_response.status_code == 200
		update_data = update_response.json()
		assert update_data['data']['firstname'] == updated_firstname
		assert update_data['message'] == 'Profile updated successfully'


	@pytest.mark.asyncio
	async def test_update_profile_existing_email(self, async_client: AsyncClient, test_db: Database, test_cache):
		await self._create_user(test_db)
		updated_email = 'r@r.r'
		test_db.users.insert_one({**self.user_data.model_dump(), 'email': updated_email})
		request_response = await async_client.get(f'/auth/request?email={self.user_data.email}')
		assert request_response.status_code == 200

		code = await test_cache.get(f'OTP:{self.user_data.email}')
		verify_response = await async_client.post('/auth/verify', json={'email': self.user_data.email, 'code': code})
		assert verify_response.status_code == 201
		token = verify_response.json()['data']['token']

		update_response = await async_client.patch('/auth/profile', json={'email': updated_email}, headers={'Authorization': f'Bearer {token}'})

		assert update_response.status_code == 409
		assert update_response.json()['message'] == f'Email not available: {updated_email}'

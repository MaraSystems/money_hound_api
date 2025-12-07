from httpx import AsyncClient
from pymongo.database import Database
import pytest

from src.domains.users.model import User
from tests.fixture_spec import TestFixture


class TestVerifyOTPEndpoint(TestFixture): 
	@pytest.mark.asyncio
	async def test_verify_otp(self, async_client: AsyncClient, test_db: Database, test_cache):
		await test_db.users.insert_one(self.user_data.model_dump())
		request_response = await async_client.get(f'/auth/request?email={self.user_data.email}')
		assert request_response.status_code == 200

		code = await test_cache.get(f'OTP:{self.user_data.email}')
		verify_response = await async_client.post('/auth/verify', json={'email': self.user_data.email, 'code': code})
		assert verify_response.status_code == 201


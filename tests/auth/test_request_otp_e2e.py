from httpx import AsyncClient
from pymongo.database import Database
import pytest

from src.domains.users.model import User
from tests.fixture_spec import TestFixture


class TestRequestOTPEndpoint(TestFixture): 
	@pytest.mark.asyncio
	async def test_request_otp(self, async_client: AsyncClient, test_db: Database, test_cache):
		await self._create_user(test_db)
		request_response = await async_client.get(f'/auth/request?email={self.user_data.email}')
		assert request_response.status_code == 200
		

	@pytest.mark.asyncio
	async def test_request_otp_user_not_found(self, async_client: AsyncClient, test_db: Database, test_cache):
		await self._create_user(test_db)
		request_response = await async_client.get('/auth/request?email=r@r.r')
		assert request_response.status_code == 404
		assert request_response.json()['message'] == f'User not found: r@r.r'
		
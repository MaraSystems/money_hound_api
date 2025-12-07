from httpx import AsyncClient
from pymongo.database import Database
import pytest

from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestRegisterUserEndpoint(TestFixture): 
    async def test_register_user(self, async_client: AsyncClient, test_db: Database):
        register_response = await async_client.post('/auth/register', json={
            'firstname': self.user_data.firstname,
            'lastname': self.user_data.lastname,
            'email': self.user_data.email
        })
        assert register_response.status_code == 201
        data = register_response.json()
        assert data['data']['email'] == self.user_data.email
        assert data['message'] == f'Registration successful: {self.user_data.email}'


    async def test_register_user_existing_email(self, async_client: AsyncClient, test_db: Database, test_cache):
        await test_db.users.insert_one(self.user_data.model_dump())
        register_response = await async_client.post('/auth/register', json={
            'firstname': self.user_data.firstname,
            'lastname': self.user_data.lastname,
            'email': self.user_data.email
        })
        assert register_response.status_code == 409
        assert register_response.json()['message'] == f'Email not available: {self.user_data.email}'


    async def test_register_user_invalid_email(self, async_client: AsyncClient, test_db: Database):
        register_response = await async_client.post('/auth/register', json={
            'firstname': self.user_data.firstname,
            'lastname': self.user_data.lastname,
            'email': 'invalid_email'
        })
        assert register_response.status_code == 422
        assert register_response.json()['message'] == '\'email\': value is not a valid email address: An email address must have an @-sign.'

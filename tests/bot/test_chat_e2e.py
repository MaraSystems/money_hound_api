from uuid import uuid4
from httpx import AsyncClient
import pytest
from pymongo.database import Database
from langgraph.graph.state import CompiledStateGraph

from src.domains.bot.chat import chat
from src.domains.bot.model import Chat
from src.lib.utils.response import DataResponse
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestChatEndpoint(TestFixture):
    async def test_chat_success(self, async_client: AsyncClient, test_db: Database):
        chat = {'message': 'Hello, world', 'session_id': 'session_id'}
        chat_response = await async_client.post(
            '/bot/chat',
            json=chat
        )
        assert chat_response.status_code == 200
        chat: DataResponse[Chat] = chat_response.json()
        assert 'session_id' in chat['data']

        chats = await test_db.bot_chat.find({}).to_list()
        assert len(chats) == 2
        assert chats[0]['role'] == 'human'
        assert chats[1]['role'] == 'bot'


    async def test_chat_success_without_session_id(self, async_client: AsyncClient, test_db: Database):
        chat = {'message': 'Hello, world'}
        chat_response = await async_client.post(
            '/bot/chat',
            json=chat
        )
        assert chat_response.status_code == 200
        chat: DataResponse[Chat] = chat_response.json()
        assert 'session_id' in chat['data']

        chats = await test_db.bot_chat.find({}).to_list()
        assert len(chats) == 2
        assert chats[0]['role'] == 'human'
        assert chats[1]['role'] == 'bot'

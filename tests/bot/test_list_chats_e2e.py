from uuid import uuid4
from httpx import AsyncClient
from langgraph.graph.state import CompiledStateGraph
import pytest
from pymongo.database import Database

from src.domains.bot.chat import chat
from src.domains.bot.list_chats import list_chats
from src.domains.bot.model import CreateChat
from src.lib.utils.pagination import Page
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestListChatsService(TestFixture):
    async def test_list_chat_empty(self, async_client: AsyncClient):
        session_id = str(uuid4())
        chat_response = await async_client.get(
            f'/bot/chat/{session_id}'
        )
        assert chat_response.status_code == 200
        response_data = chat_response.json()
        assert response_data['data'] == []


    async def test_list_chat_populated(self, async_client: AsyncClient, test_db: Database, test_agent: CompiledStateGraph, test_cache):
        session_id = str(uuid4())
        await chat(CreateChat(message='Hello, I am stan', session_id=session_id), test_agent, test_db, test_cache)
        await chat(CreateChat(message='Hey, how are you today?'), test_agent, test_db, test_cache)

        chat_response = await async_client.get(
            f'/bot/chat/{session_id}'
        )
        assert chat_response.status_code == 200
        response_data = chat_response.json()

        assert len(response_data['data']) == 2

    
    async def test_list_chat_paginated(self, async_client: AsyncClient, test_db: Database, test_agent: CompiledStateGraph, test_cache):
        session_id = str(uuid4())
        for i in range(5):
            await chat(CreateChat(message=f'Hello, I am {i}', session_id=session_id), test_agent, test_db, test_cache)

        chat_response = await async_client.get(
            f'/bot/chat/{session_id}?limit=2'
        )
        response_data = chat_response.json()
        assert len(response_data['data']) == 2

        chat_response = await async_client.get(
            f'/bot/chat/{session_id}?limit=2&skip=9'
        )
        response_data = chat_response.json()
        assert len(response_data['data']) == 1
        



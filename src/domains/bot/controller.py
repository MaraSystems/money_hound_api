import os
from typing import Annotated, List
from fastapi import Depends, Query
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse

from src.graphs.taxq import get_taxq_graph
from src.config.cache import get_cache
from src.config.database import get_db
from src.domains.bot.list_chats import list_chats
from src.domains.bot.chat import chat
from src.domains.bot.model import Chat, CreateChat
from src.lib.utils.pagination import Page
from src.lib.utils.response import DataResponse

from src.tasks.sync_knowledge import sync_compliance


bot_router = APIRouter(prefix='/bot')

@bot_router.post(
    '/chat', 
    name="Chat bot")
async def send(
    payload: CreateChat, 
    agent=Depends(get_taxq_graph),
    db=Depends(get_db),
    cache=Depends(get_cache)
):
    return await chat(payload, agent, db, cache)


@bot_router.get(
    '/chat/{session_id}',
    response_model=DataResponse[List[Chat]],
    name="List Chats"
)
async def fetch(
    session_id: str,
    payload: Annotated[Query, Depends(Page)],
    db=Depends(get_db)
) -> DataResponse[List[Chat]]:
    return await list_chats(session_id, payload, db)


@bot_router.post(
    '/sync', 
    response_model=DataResponse[None],
)
async def sync(
    db=Depends(get_db)
):
    await sync_compliance(db)
    return DataResponse(message='Sync complete')
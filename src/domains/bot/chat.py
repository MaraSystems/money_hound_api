from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph
import json
from pymongo.database import Database
from redis.asyncio import Redis

from src.domains.bot.chat_session import get_chat_session, update_chat_session
from src.domains.bot.model import Chat, CreateChat
from src.lib.utils.response import DataResponse
from src.lib.utils.function import FunctionEnum, TAXQ_FUNCTIONS


async def chat(payload: CreateChat, graph: CompiledStateGraph,  db: Database, cache: Redis):
    bot_chat_collection = db.bot_chat
    config = {"configurable": {"thread_id": payload.session_id}}

    history = await get_chat_session(cache, payload.session_id)
    parsed_history = [HumanMessage(chat['message']) if chat['role'] == 'human' else AIMessage(chat['role']) for chat in history]
    messages = parsed_history + [HumanMessage(payload.message)]

    functions = [TAXQ_FUNCTIONS[FunctionEnum.RESEARCHER]]

    response = await graph.ainvoke({
        'messages': messages,
        'functions': functions
    }, config=config)

    reply = response['messages'][-1].content
    conversation = [
        {'message':payload.message, 'role': 'human'},
        {'message':reply, 'role': 'bot'}
    ]

    history = history + conversation
    await update_chat_session(cache, payload.session_id, history)

    chats = [CreateChat(**{**chat, 'session_id': payload.session_id}).model_dump() for chat in conversation]
    await bot_chat_collection.insert_one(chats[0])
    insert = await bot_chat_collection.insert_one(chats[1])
    data = await bot_chat_collection.find_one({'_id': insert.inserted_id})

    return DataResponse(data=Chat(**data))

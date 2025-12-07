from pymongo.database import Database
from src.lib.utils.pagination import Page, sort_mapping
from src.lib.utils.response import DataResponse


async def list_chats(session_id: str, payload: Page, db: Database):
    bot_chat_collection = db.bot_chat

    data = (await bot_chat_collection.find({'session_id': session_id})
                 .sort('created_at', sort_mapping[payload.sort])
                 .limit(payload.limit)
                 .skip(payload.skip)
                 .to_list())
    
    return DataResponse(data=data)

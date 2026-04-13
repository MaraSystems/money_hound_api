from pymongo.database import Database
from src.models.pagination import Page, sort_mapping
from src.models.response import PageResponse


async def list_chats(session_id: str, payload: Page, db: Database):
    """List chat messages for a specific session with pagination

    Args:
        session_id: ID of the chat session to retrieve messages for
        payload: Page object containing pagination parameters (skip, limit, sort)
        db: Database connection

    Returns:
        PageResponse containing paginated chat messages and metadata
    """
    conversation_collection = db.conversations

    data = (await conversation_collection.find({'session_id': session_id})
                 .sort('created_at', sort_mapping[payload.sort])
                 .limit(payload.limit + 1)
                 .skip(payload.skip * payload.limit)
                 .to_list())

    has_more = len(data) > payload.limit
    return PageResponse(skip=payload.skip, limit=payload.limit, data=data[0:payload.limit], has_more=has_more)

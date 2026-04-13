from typing_extensions import Annotated
from fastapi import Depends, Query, Request
from fastapi.routing import APIRouter

from src.db.cache import get_cache
from src.db.database import get_db
from src.domains.bots.list_chats import list_chats
from src.middlewares.auth_guard import require_user
from src.models.auth import CurrentUser
from src.models.workflow import Chat, CreateChat
from src.domains.bots.support import support
from src.models.pagination import Page
from src.models.response import PageResponse


bots_router = APIRouter(prefix='/bots')

@bots_router.post(
    '/support',
    name="Support bot")
async def send(
    request: Request,
    payload: CreateChat,
    db=Depends(get_db),
    cache=Depends(get_cache)
):
    """Send a message to the support bot and get a streamed response

    Args:
        request: FastAPI Request object
        payload: CreateChat object containing user message and session info
        db: Database dependency
        cache: Redis cache dependency

    Returns:
        StreamingResponse with bot's response
    """
    user: CurrentUser = await require_user(request, db, cache, False)
    user_id = None if user is None else user.id
    return await support(payload, db, cache, user_id)


@bots_router.get(
    '/chats/{session_id}',
    response_model=PageResponse[Chat],
    name="List Chats"
)
async def fetch(
    session_id: str,
    payload: Annotated[Query, Depends(Page)],
    db=Depends(get_db)
) -> PageResponse[Chat]:
    """Fetch chat history for a specific session

    Args:
        session_id: ID of the chat session
        payload: Page object containing pagination parameters
        db: Database dependency

    Returns:
        DataResponse containing paginated chat history
    """
    return await list_chats(session_id, payload, db)

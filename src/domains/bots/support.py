import base64
from fastapi.responses import StreamingResponse
from pymongo.database import Database
from redis.asyncio import Redis
from langchain.messages import HumanMessage

from src.domains.bots.start_conversation import start_conversation
from src.models.workflow import CreateChat
from src.lib.store.storage import Storage
from src.models.workflow import WorkflowSettings
from src.agents.support_agent import SupportState, SupportAgent


async def support(payload: CreateChat, db: Database, cache: Redis, user_id = None):
    """Process user support request and return streamed AI response

    Args:
        payload: CreateChat object containing user message and session info
        db: Database connection
        cache: Redis cache connection
        user_id: Optional user ID for authenticated users

    Returns:
        StreamingResponse with AI-generated support response
    """
    messages = []
    if payload.document:
        payload.document.content = base64.b64decode(payload.document.url)
        storage = Storage()
        file_path, content_type = await storage.upload_document(payload.document)
        messages.append(HumanMessage(f'Extract the contents of this document file_path={file_path}; content_type={content_type}'))

    await start_conversation(payload.session_id, user_id, cache)

    workflow = SupportAgent(db=db, cache=cache, settings=WorkflowSettings(session_id=payload.session_id))
    messages.append(HumanMessage(payload.content))
    return StreamingResponse(
        workflow.stream(SupportState(messages=messages), save=True),
        media_type='text/event-stream'
    )

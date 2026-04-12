import asyncio, os
import shutil
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from httpx import AsyncClient, ASGITransport
from redis import asyncio as aioredis

from src.db.cache import get_cache
from src.db.database import get_db
from src.lib.utils.config import APP_NAME, MONGO_URL, REDIS_URL, UPLOAD_PATH
from src.middlewares.limits import rate_limit
from src.main import app



db_name = f'{APP_NAME}_test'

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    client = AsyncIOMotorClient(MONGO_URL)
    db: Database = client[db_name]
    yield db
    await client.drop_database(db_name)
    client.close()


@pytest.fixture
async def test_cache():
    client = aioredis.from_url(f'{REDIS_URL}/0', decode_responses=True)
    yield client
    await client.flushall()
    await client.aclose()


@pytest_asyncio.fixture(autouse=True)
async def clean_up():
    yield
    shutil.rmtree(UPLOAD_PATH, ignore_errors=True)


@pytest_asyncio.fixture(autouse=True)
async def override_dependency(test_db, test_cache):
    app.dependency_overrides[get_db] = lambda: test_db
    app.dependency_overrides[get_cache] = lambda: test_cache

    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(test_db, test_cache):
    rate_limit.reset()
    transport = ASGITransport(app=app, root_path='')

    async with AsyncClient(transport=transport, base_url='http://test') as test_client:
        yield test_client

    app.dependency_overrides.clear()


def pytest_collection_modifyitems(config, items):
    only_items = [item for item in items if "only" in item.keywords]
    if only_items:
        items[:] = only_items
import asyncio
import shutil
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from httpx import AsyncClient, ASGITransport
from redis import asyncio as aioredis

from src.graphs.taxq import get_taxq_graph
from src.config.config import ENV, UPLOAD_PATH
from src.middlewares.limits import rate_limit
from src.main import app
from src.config.database import MONGO_URL, MONGO_DB, get_db
from src.config.cache import REDIS_URL, get_cache
from tests.fakes import FakeAgent


db_name = f'{MONGO_DB}_test'

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
async def override_dependency(test_db, test_agent, test_cache):
    app.dependency_overrides[get_db] = lambda: test_db
    app.dependency_overrides[get_taxq_graph] = lambda: test_agent
    app.dependency_overrides[get_cache] = lambda: test_cache

    yield
    app.dependency_overrides.clear()


@pytest.fixture
def test_agent():
    agent = FakeAgent()
    yield agent


@pytest.fixture
async def async_client(test_db, test_agent, test_cache):
    rate_limit.reset()

    transport = ASGITransport(app=app, root_path='')

    async with AsyncClient(transport=transport, base_url='http://test') as test_client:
        yield test_client

    app.dependency_overrides.clear()


def pytest_collection_modifyitems(config, items):
    only_items = [item for item in items if "only" in item.keywords]
    if only_items:
        items[:] = only_items
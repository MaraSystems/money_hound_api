from typing import Optional
from bson import ObjectId
from pymongo.database import Database
import pytest
from redis import Redis

from src.domains.auth.model import CreateUser, TokenData
from src.domains.notifications.model import CreateNotification
from src.domains.roles.model import CreateRole
from src.domains.auth.create_token import create_token
from src.domains.bot.model import CreateChat
from src.domains.simulations.model import CreateSimulation
from src.tasks.simulations import run_simulation


class TestFixture:
    user_data = CreateUser(
        email='m@m.m', 
        firstname='some', 
        lastname='one'
    )

    role_data = CreateRole(
        title="Admin",
        description="Administrator role",
        permissions=["*:*:*"]
    )

    notification_data = CreateNotification(
        subject='Sample',
        message='Welcome message',
        category='message'
    )

    chat_data = CreateChat(
        message='Hello'
    )

    simulation_data = CreateSimulation(
        num_banks=5,
        min_num_user=10,
        latitude=9,
        longitude=3,
        days=0.001
    )


    async def _create_user(self, test_db: Database, user: Optional[CreateUser]=None):
        user = user or self.user_data
        inserted = await test_db.users.insert_one(user.model_dump())
        return await test_db.users.find_one({'_id': inserted.inserted_id})


    def _assign_token(self, user: Optional[CreateUser]=None):
        user = user or self.user_data
        return create_token(TokenData(sub=user.email))


    async def _create_role(self, test_db: Database, author_id: ObjectId, role: Optional[CreateRole]=None):
        role = role or self.role_data
        inserted = await test_db.roles.insert_one({**role.model_dump(), 'author_id': str(author_id)})
        return await test_db.roles.find_one({'_id': inserted.inserted_id})

    
    async def _assign_role(self, test_db: Database, role_id: ObjectId, user_id: ObjectId):
        await test_db.roles.update_one(
            {"_id": role_id},
            {"$addToSet": {"users": str(user_id)}},
        )
        
    
    async def _set_up(self, test_db: Database, user: Optional[CreateUser]=None, role: Optional[CreateRole]=None):
        user = user or self.user_data
        role = role or self.role_data

        self.user = await self._create_user(test_db, user)
        self.token = self._assign_token(user)
        self.role = await self._create_role(test_db, self.user['_id'], role)
        await self._assign_role(test_db, self.role['_id'], self.user['_id'])


    async def _create_notification(self, test_db: Database, notification: Optional[CreateNotification]=None):
        notification = notification or self.notification_data
        inserted = await test_db.notifications.insert_one(notification.model_dump())
        return await test_db.notifications.find_one({'_id': inserted.inserted_id})
    

    async def _create_simulation(self, test_db: Database, test_cache: Redis, simulation: Optional[CreateSimulation]=None):
        simulation = simulation or self.simulation_data
        inserted = await test_db.simulations.insert_one({**simulation.model_dump(), 'author_id': str(self.user['_id'])})

        simulation = await test_db.simulations.find_one({'_id': inserted.inserted_id})
        simulation['_id'] = str(simulation['_id'])

        await run_simulation(simulation, str(self.user['_id']), test_db, test_cache)
        return simulation

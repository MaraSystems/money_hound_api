from typing import Any


from pymongo.database import Database

from src.models.simulation import CreateSimulation, Simulation
from src.lib.task.run_task import run_task
from src.models.response import DataResponse
from src.tasks.run_simulation import run_simulation_task


async def create_simulation(payload: CreateSimulation, user_id: str, db: Database):
    simulation_collection = db.simulations
    insert = await simulation_collection.insert_one({**payload.model_dump(), 'author_id': user_id})
    simulation = await simulation_collection.find_one({'_id': insert.inserted_id})

    simulation['_id'] = str(simulation['_id'])
    run_task(
        run_simulation_task,
        kwargs={
            'payload': simulation,
            'user_id': user_id
        }
    )
    return DataResponse[Simulation](data=Simulation(**simulation), message=f'Simulation initiated successfully')

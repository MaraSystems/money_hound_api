from typing import Any


from pymongo.database import Database

from src.domains.simulations.model import CreateSimulation, Simulation
from src.lib.utils.response import DataResponse
from src.tasks.simulations import run_simulation, simulator


async def create_simulation(payload: CreateSimulation, user_id: str, db: Database):
    simulation_collection = db.simulations
    insert = await simulation_collection.insert_one({**payload.model_dump(), 'author_id': user_id})
    simulation = await simulation_collection.find_one({'_id': insert.inserted_id})

    simulation['_id'] = str(simulation['_id'])
    simulator.delay(simulation, user_id)
    return DataResponse[Simulation](data=Simulation(**simulation), message=f'Simulation initiated successfully')

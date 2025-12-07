from src.lib.utils.pagination import sort_mapping
from .model import ListUsers
from pymongo.database import Database

from ...lib.utils.response import DataResponse


async def list_users(params: ListUsers, db: Database):
    user_collection = db.users
    query = {'hidden': False}
    if params.query != '':
        query = {
            '$or': [
                {'email': {'$regex': f'^{params.query}', "$options": "i"}},
                {'firstname': {'$regex': f'^{params.query}', "$options": "i"}},
                {'lastname': {'$regex': f'^{params.query}', "$options": "i"}}
            ]
        }

    data = (await user_collection.find(query)
                 .sort('created_at', sort_mapping[params.sort])
                 .limit(params.limit)
                 .skip(params.skip)
                 .to_list())
    
    return DataResponse(data=data)

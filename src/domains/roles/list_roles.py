from pymongo.database import Database

from src.lib.utils.pagination import sort_mapping
from .model import ListRoles, Role
from src.lib.utils.response import DataResponse


async def list_roles(payload: ListRoles, db: Database) -> DataResponse[list[Role]]:
    role_collection = db.roles
    query = {'hidden': False}
    if payload.query is not None:
        query = {
            **query,
            **{
                '$or': [
                    {'title': {'$regex': f'^{payload.query}', "$options": "i"}}
                ]
            }
        }

    if payload.user_id is not None:
        query = {
            **query,
            **{'users': payload.user_id}
        }

    data = (await role_collection.find(query)
                 .sort('created_at', sort_mapping[payload.sort])
                 .limit(payload.limit)
                 .skip(payload.skip)
                 .to_list())
    
    return DataResponse(data=data)

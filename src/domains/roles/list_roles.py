from pymongo.database import Database

from src.models.pagination import sort_mapping
from src.models.role import ListRoles, Role
from src.models.response import PageResponse


async def list_roles(payload: ListRoles, db: Database) -> PageResponse[Role]:
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
        .limit(payload.limit+1)
        .skip(payload.skip * payload.limit)
        .to_list())
    
    has_more = len(data) > payload.limit
    return PageResponse(skip=payload.skip, limit=payload.limit, data=data[0:payload.limit], has_more=has_more)

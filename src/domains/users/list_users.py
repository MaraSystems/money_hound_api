from src.models.pagination import sort_mapping
from src.models.user import ListUsers, User
from pymongo.database import Database
from src.models.response import PageResponse


async def list_users(payload: ListUsers, db: Database) -> PageResponse[User]:
    user_collection = db.users
    query = {'hidden': False}
    if payload.query != '':
        query = {
            '$or': [
                {'email': {'$regex': f'^{payload.query}', "$options": "i"}},
                {'firstname': {'$regex': f'^{payload.query}', "$options": "i"}},
                {'lastname': {'$regex': f'^{payload.query}', "$options": "i"}}
            ]
        }

    data = (await user_collection.find(query)
        .sort('created_at', sort_mapping[payload.sort])
        .limit(payload.limit+1)
        .skip(payload.skip * payload.limit)
        .to_list())
    
    has_more = len(data) > payload.limit
    return PageResponse(skip=payload.skip, limit=payload.limit, data=data[0:payload.limit], has_more=has_more)


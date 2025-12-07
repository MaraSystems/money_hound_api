from typing import Callable, List
from fastapi import Depends, HTTPException, status

from src.config.database import get_db
from src.domains.auth.model import CurrentUser
from src.middlewares.auth_guard import get_current_user


def check_permission(permission: str, user_permissions: List[str]) -> bool:
    [domain, section, action] = permission.split(':')

    for user_permit in user_permissions:
        [user_domain, user_section, user_action] = user_permit.split(':')
        valid_domain = ['*', domain].count(user_domain) > 0
        valid_section = ['*', section].count(user_section) > 0
        valid_action = ['*', action].count(user_action) > 0

        if valid_domain and valid_section and valid_action:
            return True

    return False


def require_permission(permission: str) -> Callable:
    async def dependency(user: CurrentUser=Depends(get_current_user), db=Depends(get_db)) -> None:
        user_permissions = await user.get_permissions(db)
        allow = check_permission(permission, user_permissions)

        if not allow:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Not Authorized',
            )

    return dependency

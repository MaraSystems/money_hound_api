from typing import List

from src.domains.roles.model import Domain
from src.lib.utils.response import DataResponse


async def list_domains():
    return DataResponse(
        data=[
            Domain(name='users', subdomains=['base']),
            Domain(name='roles', subdomains=['base', 'domains', 'users']),
            Domain(name='notifications', subdomains=['base']),
            Domain(name='designs', subdomains=['base']),
            Domain(name='carts', subdomains=['base', 'categories']),
            Domain(name='orders', subdomains=['base']),
            Domain(name='transactions', subdomains=['base']),
        ]
    )

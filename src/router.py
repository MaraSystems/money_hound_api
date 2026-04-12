from fastapi import FastAPI

from src.domains.simulation_accounts.controller import simulation_accounts_router
from src.domains.simulation_devices.controller import simulation_devices_router
from src.domains.simulation_profiles.controller import simulation_profiles_router
from src.domains.simulation_transactions.controller import simulation_transactions_router

from .domains.users.controller import user_router
from .domains.auth.controller import auth_router
from .domains.roles.controller import role_router
from .domains.notifications.controller import notification_router
from .domains.simulations.controller import simulations_router


def register_routes(app: FastAPI):
    app.include_router(auth_router, tags=["Authentication"])
    app.include_router(user_router, tags=["Users"])
    app.include_router(role_router, tags=["Roles"])
    app.include_router(notification_router, tags=["Notifications"])
    app.include_router(simulations_router, tags=["Simulations"])
    app.include_router(simulation_transactions_router, tags=["Simulation Transactions"])
    app.include_router(simulation_profiles_router, tags=["Simulation Profiles"])
    app.include_router(simulation_accounts_router, tags=["Simulation Accounts"])
    app.include_router(simulation_devices_router, tags=["Simulation Devices"])

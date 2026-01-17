from aiogram import Router

from . import client
# from . import admin
# from . import testing

def setup_callback_routers():

    router = Router()
    router.include_router(client.router)
    # router.include_router(admin.router)
    # router.include_router(testing.router)
    return router
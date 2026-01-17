from aiogram import Router

from . import client

def setup_message_routers():

    router = Router()
    router.include_router(client.router)
    return router
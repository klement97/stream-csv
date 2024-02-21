from es_config import client
from services.stream_csv import StreamUsersCSVService


async def get_stream_users_service():
    return StreamUsersCSVService(client)

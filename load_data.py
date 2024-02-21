import json
import uuid

from elasticsearch import helpers

from es_config import client
import asyncio


def load_data(file_name):
    with open(file_name) as f:
        return json.load(f)


async def save_data(data):
    actions = [
        {
            "doc_as_upsert": "true",
            "doc": item,
            "_op_type": "update",
            "_index": "users",
            "_id": uuid.uuid4(),
        }
        for item in data
    ]
    await helpers.async_bulk(client, actions)
    print("Data saved")


if __name__ == '__main__':
    mock_data = load_data('./mock_data.json')
    # Multiply the data to have 1M docs
    mock_data *= 1000
    asyncio.run(save_data(mock_data))

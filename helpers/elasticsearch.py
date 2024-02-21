from contextlib import AbstractAsyncContextManager


class PointInTime(AbstractAsyncContextManager):
    def __init__(self, client, index, keep_alive):
        self.client = client
        self.index = index
        self.keep_alive = keep_alive
        self._pit_id = None

    async def __aenter__(self):
        response = await self.client.open_point_in_time(
            index=self.index, keep_alive=self.keep_alive
        )
        self.pit_id = response.get("id")

        if self.pit_id is None:
            raise Exception("Unable to open point in time")

        return self.pit_id

    async def __aexit__(self, exc_type, exc_val, traceback) -> None:
        if self._pit_id is None:
            return

        await self.client.close_point_in_time(id=self._pit_id)
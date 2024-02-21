import csv
from io import StringIO

from starlette.responses import StreamingResponse

from helpers.elasticsearch import PointInTime


class StreamUsersCSVService:
    fields = [
        "id",
        "first_name",
        "last_name",
        "email",
        "gender",
        "ip_address",
    ]

    def __init__(self, client):
        self.client = client
        self._index = "users"
        self._pit_keep_alive = "10s"
        self._es_search_max_size = 100

    @classmethod
    def get_csv_header(cls):
        return ",".join(cls.fields) + "\n"

    @classmethod
    def get_csv_row(cls, row):
        user = row["_source"]
        row_output = StringIO(newline="\n")
        r = [
            user["id"],
            user["first_name"],
            user["last_name"],
            user["email"],
            user["gender"],
            user["ip_address"],
        ]
        csv.writer(row_output).writerow(r)

        return row_output.getvalue()

    async def _get_data_for_export(self):
        """
        Perform a search using the search_after + PIT method to get all the data for export.
        https://www.elastic.co/guide/en/elasticsearch/reference/current/point-in-time-api.html#point-in-time-api

        Yields:
        - AsyncGenerator: An asynchronous generator that yields a list of search results that comes
                          from ES.
        """
        async with PointInTime(self.client, self._index,
                               self._pit_keep_alive) as pit_id:
            search_kwargs = {
                "size": self._es_search_max_size,
                "sort": {"id": "asc"},
                "pit": {"id": pit_id, "keep_alive": self._pit_keep_alive},
                "track_total_hits": False,
            }
            response = await self.client.search(**search_kwargs)
            hits = response["hits"]["hits"]
            yield hits

            while hits:
                last_sort_value = hits[-1]["sort"]
                response = await self.client.search(
                    **search_kwargs,
                    search_after=last_sort_value,
                )
                hits = response["hits"]["hits"]
                yield hits

    async def _start_stream(self):
        """
        Asynchronously generates a CSV file of users and yields each row as a string.

        Yields:
        - AsyncGenerator: An asynchronous generator that yields a string representation of each row
                          in the CSV file.
        """
        yield self.get_csv_header()  # Yield the header first so the stream can start immediately.
        async for data_chunk in self._get_data_for_export():
            for row in data_chunk:
                yield self.get_csv_row(row)

    async def execute(self):
        return StreamingResponse(
            self._start_stream(),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=user_exports.csv",
            },
        )

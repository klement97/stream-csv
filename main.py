from fastapi import Depends, FastAPI

from helpers.deps import get_stream_users_service

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/export")
async def export(service=Depends(get_stream_users_service)):
    return await service.execute()

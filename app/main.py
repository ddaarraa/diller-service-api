from app.db import db
from app.routes import raw_logs
from fastapi import FastAPI

app = FastAPI()

app.include_router(raw_logs.router)

    



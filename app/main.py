from app.routes import raw_logs, correlation
from fastapi import FastAPI

app = FastAPI()

app.include_router(raw_logs.router)
app.include_router(correlation.router)

    



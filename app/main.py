from app.middleware.middleware import SecretKeyMiddleware
from app.routes import raw_logs, correlation
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecretKeyMiddleware)
app.include_router(raw_logs.router)
app.include_router(correlation.router)

    



from app.middleware.middleware import SecretKeyMiddleware, verify_secret_key
from app.routes import raw_logs, correlation
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(dependencies=[Depends(verify_secret_key)])
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

    



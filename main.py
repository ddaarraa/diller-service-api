from fastapi import FastAPI
from app.routes import router
import raw_logs.getRawLogs

app = FastAPI(title="My FastAPI Project")

# Include routes
app.include_router(router)

@app.get("/rawlogs/:collection/:page")
async def home():
    return {"message" : raw_logs.getRawLogs() }


# @app.get("/processedlogs/:collection/:page")
# async def home():
#     return {"message": "🚀 FastAPI is running!"}
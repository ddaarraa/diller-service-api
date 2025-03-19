from fastapi import FastAPI

app = FastAPI(title="My FastAPI Project")

@app.get("/")
async def home():
    return {"message" : "fast is running" }


# @app.get("/processedlogs/:collection/:page")
# async def home():
#     return {"message": "🚀 FastAPI is running!"}
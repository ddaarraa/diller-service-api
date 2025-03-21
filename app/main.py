from app.db import db
from app.routes import raw_logs
from fastapi import FastAPI

app = FastAPI()

app.include_router(raw_logs.router)

@app.get("/create-index")
async def create_text_index(collection_name: str = "vpc_logs_collection"):
    collection = db[collection_name]
    
    # Fetch a sample document with await to avoid '_asyncio.Future' issue
    sample_doc = await collection.find_one()

    if sample_doc:
        # Create text index on all fields except '_id'
        index_fields = [(field, "text") for field in sample_doc.keys() if field != "_id"]
        await collection.create_index(index_fields)
        return {"message": f"Text index created on fields: {index_fields}"}
    else:
        return {"message": "Collection is empty. No index created."}
    




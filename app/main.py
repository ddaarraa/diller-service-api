import datetime
import string
from fastapi import FastAPI, Query
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
from pymongo import MongoClient
from pydantic import BaseModel,Field, ConfigDict

app = FastAPI()

# MongoDB connection URI (replace with your actual URI)
MONGO_URI = "mongodb://admin:adminpassword@3.107.211.33:27017/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=admin&appName=mongosh+2.4.0"
DATABASE_NAME = "logs_db"

client = None
db = None

try:
    client = AsyncIOMotorClient(MONGO_URI)
    # client = MongoClient(MONGO_URI)
    db = client["logs_db"]
    print("MongoDB connection established!")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")
    raise HTTPException(status_code=500, detail="Database connection error")

class TimeModel(BaseModel):
    date: datetime = Field(..., serialization_alias="$date")

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Fix for datetime

class vpc_logs(BaseModel):
    id: str = Field(..., alias="_id")
    version: str
    account_id: str
    interface_id: str
    srcaddr: str
    dstaddr: str
    srcport: int
    dstport: int
    protocol: int
    packets: int
    bytes: int
    end: int
    action: str
    log_status: str
    time: TimeModel

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


@app.get("/raw-logs/", response_model=List[vpc_logs])
async def get_raw_logs(page: int = Query(1, alias="page", ge=1), page_size: int = 10, collection_name : str = "vpc_logs_collection"):
    """
    Fetch paginated items from MongoDB.
    Default page size = 10.
    """

    collection = db[collection_name]
    skip = (page - 1) * page_size

    items = []
    items_cursor = await collection.find().skip(skip).limit(page_size).to_list(None)

    # Iterate over the items directly
    for item in items_cursor:
        items.append(
            vpc_logs(
                id=str(item["_id"]),
                version=item["version"],
                account_id=item["account_id"],
                interface_id=item["interface_id"],
                srcaddr=item["srcaddr"],
                dstaddr=item["dstaddr"],
                srcport=item["srcport"],
                dstport=item["dstport"],
                protocol=item["protocol"],
                packets=item["packets"],
                bytes=item["bytes"],
                end=item["end"],
                action=item["action"],
                log_status=item["log_status"],
                time={"date": item["time"]}  # No need to use ["$date"]
            )
        )

    return items


# @app.get("/processedlogs/:collection/:page")
# async def home():
#     return {"message": "🚀 FastAPI is running!"}



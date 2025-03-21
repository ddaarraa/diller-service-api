from app.models.app_logs import app_logs
from fastapi import APIRouter, Query
from typing import List, Optional
from app.models.vpc_logs import vpc_logs
from app.db import db 

router = APIRouter()

@router.get("/raw-logs/application_logs_collection", response_model=List[app_logs])
async def get_application_logs_collection(page: int = Query(1, alias="page", ge=1),
    page_size: int = Query(10, alias="page_size"),
    collection_name: str = Query("application_logs_collection", alias="collection_name"),
    query: Optional[str] = Query(None, alias="search")):
    """
    Fetch paginated items from MongoDB.
    Default page size = 10.
    """

    collection = db['application_logs_collection']

    skip = (page - 1) * page_size

    items = []
    
    filters = {"$text": {"$search": query}} if query else {}

    items_cursor = await collection.find(filters).sort("_id").skip(skip).limit(page_size).to_list(None)

    for item in items_cursor:
        items.append(
            app_logs(
                id=str(item["_id"]),
                source=item["source"],
                log=item["log"],
                container_id=item["container_id"],
                container_name=item["container_name"],
                srcaddr=item["srcaddr"],
                method=item["method"],
                message=item["message"],
                status=item["status"],
                action=item["action"],
                time={"date": item["time"]}
            )
        )

    return items


@router.get("/raw-logs/vpc_logs_collection", response_model=List[vpc_logs])
async def get_vpc_logs_collection(page: int = Query(1, alias="page", ge=1),
    page_size: int = Query(10, alias="page_size"),
    collection_name: str = Query("vpc_logs_collection", alias="collection_name"),
    query: Optional[str] = Query(None, alias="search")):
    """
    Fetch paginated items from MongoDB.
    Default page size = 10.
    """

    collection = db[collection_name]

    skip = (page - 1) * page_size

    items = []
    
    filters = {"$text": {"$search": query}} if query else {}

    items_cursor = await collection.find(filters).sort("_id").skip(skip).limit(page_size).to_list(None)

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
                time={"date": item["time"]}
            )
        )

    return items
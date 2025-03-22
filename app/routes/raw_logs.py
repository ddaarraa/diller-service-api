import datetime
from tkinter.tix import INTEGER
from tokenize import String
from app.models.app_logs import app_logs, app_logs_response
from fastapi import APIRouter, Query
from typing import List, Optional
from app.models.vpc_logs import vpc_logs, vpc_logs_response
from app.db import db 
from math import ceil

router = APIRouter()

@router.get("/raw-logs/application_logs_collection", response_model=app_logs_response)
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
    
    filters = {}
    if query:
        filters["$or"] = []

        sample_doc = await collection.find_one()
        
        CustomSearch(sample_doc=sample_doc, model=app_logs, filters=filters, query=query)

    total_logs = await collection.count_documents(filters)
    total_pages = ceil(total_logs / page_size) if total_logs > 0 else 1

    items_cursor = await collection.find(filters).sort("_id").skip(skip).limit(page_size).to_list(None)

    logs = [
        app_log.dict()  # Serialize each app_log instance to a dictionary
        for item in items_cursor
        for app_log in [app_logs(
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
            time={"date": item["time"]},  # Extract the date from MongoDB's $date field
        )]
    ]

    resposenData : app_logs_response = {
        "page" : page,
        "page_size" : page_size,
        "total_logs" : total_logs,
        "total_pages" : total_pages,
        "logs" : logs
    }

    return resposenData



@router.get("/raw-logs/vpc_logs_collection", response_model=vpc_logs_response)
async def get_vpc_logs_collection(
        page: int = Query(1, alias="page", ge=1),
        page_size: int = Query(10, alias="page_size"),
        collection_name: str = Query("vpc_logs_collection", alias="collection_name"),
        query: Optional[str] = Query(None, alias="search"
    )):

    collection = db[collection_name]

    skip = (page - 1) * page_size
    
    items = []
    
    filters = {}
    if query:
        filters["$or"] = []

        sample_doc = await collection.find_one()
        
        CustomSearch(sample_doc=sample_doc, model=vpc_logs, filters=filters, query=query)
                    
    total_logs = await collection.count_documents(filters)

    total_pages = ceil(total_logs / page_size) if total_logs > 0 else 1

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

    return {
        "page" : page,
        "page_size" : page_size,
        "total_logs" : total_logs,
        "total_pages" : total_pages,
        "logs" : items
    }


def CustomSearch(sample_doc, model, filters, query) :
    for field in sample_doc.keys() :
            if field in model.__annotations__.keys() :
                field_type = model.__annotations__[field] 
                if field_type == int :
                    try:
                        query_number = float(query)
                        filters["$or"].append({field: query_number})
                    except ValueError:
                        pass  
                elif field_type == str : 
                    filters["$or"].append({field: {"$regex": query, "$options": "i"}})
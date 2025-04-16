import datetime
from http.client import HTTPException

from bson import ObjectId

from app.log_models.sys_logs import sys_logs, system_logs_response
from fastapi import APIRouter, Query
from typing import Dict, List, Optional, Union
from math import ceil
from dateutil import parser
from app.log_models.app_logs import app_logs, app_logs_response
from app.log_models.vpc_logs import vpc_logs, vpc_logs_response
from app.db import log_db
from log_models.time import TimeModel

router = APIRouter()

@router.get("/raw-logs-id")
async def get_log_by_id(
    _id: str = Query(..., alias="_id"),
    collection_name: str = Query("application_logs_collection", alias="collection_name")
):
    if collection_name not in ["application_logs_collection", "vpc_logs_collection", "sys_logs_collection"]:
        raise HTTPException(status_code=400, detail="Invalid collection_name")

    collection = log_db[collection_name]
    model = model_selection(collection_name)

    try:
        doc = await collection.find_one({"_id": ObjectId(_id)})
    except Exception:
        doc = await collection.find_one({"_id": _id})

    if not doc:
        raise HTTPException(status_code=404, detail="Log not found")

    time = TimeModel(date=doc["time"]).dict()["date"]

    parsed_log = model(
        id=str(doc["_id"]),
        **{key: doc[key] for key in doc if key in model.__annotations__ and key != "time"},
        time={"date": time}
    )

    response_data = {
        "log": parsed_log
    }

    return response_data


@router.get("/raw-logs", response_model=Union[app_logs_response, vpc_logs_response ,system_logs_response])
async def get_logs(
    page: int = Query(1, alias="page", ge=1),
    page_size: int = Query(10, alias="page_size"),
    collection_name: str = Query("vpc_logs_collection", alias="collection_name"),
    query: Optional[str] = Query(None, alias="search"),
    start_date: Optional[str] = Query(None, alias="start_date"),
    end_date: Optional[str] = Query(None, alias="end_date")
):
    
    if collection_name not in ["application_logs_collection", "vpc_logs_collection", "sys_logs_collection"]:
        return {"error": "Invalid collection_name"}

    collection = log_db[collection_name]
    filters = {}

    model = model_selection(collection_name=collection_name)
    
    if query:
        filters["$or"] = []
        sample_doc = await collection.find_one()
        CustomSearch(sample_doc=sample_doc, model=model, filters=filters, query=query)

    if start_date or end_date :
        time_filter(filters=filters, start_date=start_date, end_date=end_date)
    
    skip = (page - 1) * page_size
      
    total_logs = await collection.count_documents(filters)

    items_cursor = await collection.find(filters).sort("time", -1).skip(skip).limit(page_size).to_list(None)

    logs = []

    for item in items_cursor:
        time = TimeModel(date=item["time"]).dict()["date"]
        logs.append(
            model(
                id=str(item["_id"]),
                **{key: item[key] for key in item if key in model.__annotations__ and key != "time"},
                time={"date": time}
            )
        )

    total_pages = ceil(total_logs / page_size) if total_logs > 0 else 1

    response_data = {
        "page": page,
        "page_size": page_size,
        "total_logs": total_logs,
        "total_pages": total_pages,
        "logs": logs
    }

    return response_data

@router.get("/all-raw-logs", response_model=Dict[str, List[Union[app_logs, vpc_logs, sys_logs]]])
async def get_logs(
   
    collection_name: str = Query("vpc_logs_collection", alias="collection_name"),
):
    
    if collection_name not in ["application_logs_collection", "vpc_logs_collection", "sys_logs_collection"]:
        return {"error": "Invalid collection_name"}

    collection = log_db[collection_name]

    model = model_selection(collection_name=collection_name)
    

    items = await collection.find({}).to_list(None)

    logs = []
    for item in items:
        formatted_time = TimeModel(date=item["time"]).dict()["date"]
        logs.append(
            model(
                id=str(item["_id"]),
                **{k: item[k] for k in item if k in model.__annotations__ and k != "time"},
                time={"date": formatted_time}
            )
        )

    return {"logs": logs}


def CustomSearch(sample_doc, model, filters, query):
    for field in sample_doc.keys():
        if field in model.__annotations__.keys():
            field_type = model.__annotations__[field]
            if field_type == int:
                try:
                    query_number = float(query)
                    filters["$or"].append({field: query_number})
                except ValueError:
                    pass  
            elif field_type == str:
                filters["$or"].append({field: {"$regex": query, "$options": "i"}})


def time_filter(filters, start_date: datetime = None, end_date: datetime = None):
    date_filter = {}
    if start_date:
        date_filter["$gte"] = parser.parse(start_date)
    if end_date:
        date_filter["$lte"] = parser.parse(end_date)
    filters["time"] = date_filter
    

def model_selection(collection_name: str): 
    if collection_name == "application_logs_collection":
        return app_logs
    elif collection_name == "vpc_logs_collection":
        return vpc_logs
    elif collection_name == "sys_logs_collection":  
        return sys_logs
    

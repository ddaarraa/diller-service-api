import datetime
from app.models.sys_logs import sys_logs
from fastapi import APIRouter, Query
from typing import List, Optional, Union
from math import ceil

from app.models.app_logs import app_logs, app_logs_response
from app.models.vpc_logs import vpc_logs, vpc_logs_response, TimeModel
from app.db import db

router = APIRouter()

@router.get("/raw-logs", response_model=Union[app_logs_response, vpc_logs_response ,sys_logs])
async def get_logs(
    page: int = Query(1, alias="page", ge=1),
    page_size: int = Query(10, alias="page_size"),
    collection_name: str = Query("vpc_logs_collection", alias="collection_name"),
    query: Optional[str] = Query(None, alias="search"),
    start_date: Optional[str] = Query(None, alias="start_date"),
    end_date: Optional[str] = Query(None, alias="end_date")
):
    
    if collection_name not in ["application_logs_collection", "vpc_logs_collection", "system_logs_collection"]:
        return {"error": "Invalid collection_name"}

    collection = db[collection_name]

    model = None
    if collection_name == "application_logs_collection":
        model = app_logs
    elif collection_name == "vpc_logs_collection":
        model = vpc_logs
    else:  
        model = sys_logs

    skip = (page - 1) * page_size

    filters = {}
    
    if query:
        filters["$or"] = []
        sample_doc = await collection.find_one()
        CustomSearch(sample_doc=sample_doc, model=model, filters=filters, query=query)

    total_logs = await collection.count_documents(filters)

    items_cursor = await collection.find(filters).sort("time", -1).skip(skip).limit(page_size).to_list(None)

    logs = []

    for item in items_cursor :
            time = TimeModel(date=item["time"]).dict()["date"]
            if is_datetime_in_period(check_time=time, start_time=start_date, end_time=end_date) :
                logs.append(
                    model(
                            id=str(item["_id"]),
                            **{key: item[key] for key in item if key in model.__annotations__ and key != "time"},
                            time={"date": time}
                        )
                )
            else :
                total_logs = total_logs - 1

    total_pages = ceil(total_logs / page_size) if total_logs > 0 else 1

    resposenData = {
        "page" : page,
        "page_size" : page_size,
        "total_logs" : total_logs,
        "total_pages" : total_pages,
        "logs" : logs
    }

    return resposenData


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


def is_datetime_in_period(check_time: datetime, start_time: datetime = None, end_time: datetime = None) -> bool:
    if start_time and end_time :
        return start_time <= check_time <= end_time
    elif start_time != None :
        return start_time <= check_time
    elif end_time != None :
        return check_time <= end_time
    return True

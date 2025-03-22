import datetime
from fastapi import APIRouter, Query
from typing import List, Optional, Union
from math import ceil

from app.models.app_logs import app_logs, app_logs_response
from app.models.vpc_logs import vpc_logs, vpc_logs_response, TimeModel
from app.db import db

router = APIRouter()

@router.get("/raw-logs", response_model=Union[app_logs_response, vpc_logs_response])
async def get_logs(
    page: int = Query(1, alias="page", ge=1),
    page_size: int = Query(10, alias="page_size"),
    collection_name: str = Query("vpc_logs_collection", alias="collection_name"),
    query: Optional[str] = Query(None, alias="search")
):
    """
    Fetch paginated items from MongoDB for both application_logs_collection and vpc_logs_collection.
    Default page size = 10.
    """

    if collection_name not in ["application_logs_collection", "vpc_logs_collection"]:
        return {"error": "Invalid collection_name"}

    # Select the correct collection and model
    collection = db[collection_name]
    model = app_logs if collection_name == "application_logs_collection" else vpc_logs

    skip = (page - 1) * page_size
    filters = {}

    if query:
        filters["$or"] = []
        sample_doc = await collection.find_one()
        CustomSearch(sample_doc=sample_doc, model=model, filters=filters, query=query)

    total_logs = await collection.count_documents(filters)
    total_pages = ceil(total_logs / page_size) if total_logs > 0 else 1

    items_cursor = await collection.find(filters).sort("time", -1).skip(skip).limit(page_size).to_list(None)

    logs = [
    model(
        id=str(item["_id"]),
        **{key: item[key] for key in item if key in model.__annotations__ and key != "time"},
        time={"date": TimeModel(date=item["time"]).dict()["date"]}
    )
    for item in items_cursor
]


    return {
        "page": page,
        "page_size": page_size,
        "total_logs": total_logs,
        "total_pages": total_pages,
        "logs": logs
    }

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

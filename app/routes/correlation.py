from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Query
from math import ceil
from app.db import correlation_db
from app.log_models.time import TimeModel

router = APIRouter()

class response(BaseModel) :
    page : int
    page_size : int
    total_data : int
    total_pages : int
    data: List[dict] 
    
@router.get("/correlation", response_model=response)
async def get_logs(
    page: int = Query(1, alias="page", ge=1),
    page_size: int = Query(10, alias="page_size"),
):

    collection = correlation_db["correlation"]
    filters = {}

    skip = (page - 1) * page_size
      
    total_data = await collection.count_documents(filters)

    items_cursor = await collection.find(filters).sort("date", -1).skip(skip).limit(page_size).to_list(None)

    correlation_data = []

    for item in items_cursor:
        correlation_data.append(
            {
                "id" :str(item["_id"]),
                "time" :item["date"],
                "correlation" : item.get("correlation", [])   
            }
        )
    total_pages = ceil(total_data / page_size) if total_data > 0 else 1

    response_data = {
        "page": page,
        "page_size": page_size,
        "total_data": total_data,
        "total_pages": total_pages,
        "data": correlation_data
    }

    return response_data





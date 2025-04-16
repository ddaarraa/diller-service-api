import datetime
from typing import List, Optional
from pydantic import BaseModel,Field, ConfigDict

class TimeModel(BaseModel):
    date: datetime.datetime = Field(..., serialization_alias="$date") # Fix for datetime

class app_logs(BaseModel):
    id: str = Field(..., alias="_id")
    source: str
    log: str
    container_id: str
    container_name: str
    srcaddr: Optional[str] = None
    method: Optional[str] = None
    message: Optional[str] = None
    status: Optional[str] = None
    action: str
    time: TimeModel

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

class app_logs_response(BaseModel):
    page: int
    page_size: int
    total_logs: int
    total_pages: int
    logs: List[app_logs]
    class Config:
        orm_mode = True
import datetime
from pydantic import BaseModel,Field, ConfigDict

class TimeModel(BaseModel):
    date: datetime = Field(..., serialization_alias="$date")

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Fix for datetime

class app_logs(BaseModel):
    id: str = Field(..., alias="_id")
    source: str
    log: str
    container_id: str
    container_name: str
    srcaddr: str
    method: str
    message: str
    status: str
    action: str
    time: TimeModel

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
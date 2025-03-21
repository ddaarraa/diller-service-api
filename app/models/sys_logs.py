import datetime
from pydantic import BaseModel,Field, ConfigDict

class TimeModel(BaseModel):
    date: datetime = Field(..., serialization_alias="$date")

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Fix for datetime

class sys_logs(BaseModel):
    id: str = Field(..., alias="_id")
    source: str
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
import datetime
from typing import List
import pytz
from pydantic import BaseModel,Field, ConfigDict

class TimeModel(BaseModel):
    date: datetime = Field(..., serialization_alias="$date")

    def convert_to_local_time(self):
        """Converts UTC datetime to local time (UTC+7)"""
        # Ensure the datetime is in UTC before conversion
        if self.date.tzinfo is None:
            utc_zone = pytz.utc
            self.date = utc_zone.localize(self.date)  # Localize to UTC if not already timezone-aware

        local_timezone = pytz.timezone("Asia/Bangkok")  # UTC+7 timezone
        return self.date.astimezone(local_timezone)

    def dict(self, *args, **kwargs):
        """Override dict method to return the local time instead of UTC"""
        data = super().dict(*args, **kwargs)
        # Convert the date field to local time before returning
        if "date" in data:
            data["date"] = self.convert_to_local_time().isoformat()
        return data

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

class vpc_logs_response(BaseModel):
    page: int
    page_size: int
    total_logs: int
    total_pages: int
    logs: List[vpc_logs]
    class Config:
        orm_mode = True
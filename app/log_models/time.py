import datetime
from pydantic import BaseModel,Field, ConfigDict
import pytz

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

    model_config = ConfigDict(arbitrary_types_allowed=True)
from typing import List
from app.log_models.time import TimeModel
from pydantic import BaseModel,Field, ConfigDict

class sys_logs(BaseModel):
    id: str = Field(..., alias="_id")
    host: str
    process: str
    message: str
    srcaddr: str
    action: str
    time: TimeModel
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
    
class system_logs_response(BaseModel):
    page: int
    page_size: int
    total_logs: int
    total_pages: int
    logs: List[sys_logs]
    class Config:
        orm_mode = True 
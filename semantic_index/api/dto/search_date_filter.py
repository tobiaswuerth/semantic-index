from pydantic import BaseModel
from datetime import datetime


class SearchDateFilter(BaseModel):
    createdate_start: datetime | None
    createdate_end: datetime | None
    modifieddate_start: datetime | None
    modifieddate_end: datetime | None

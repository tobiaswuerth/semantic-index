from pydantic import BaseModel


class HistogramResponse(BaseModel):
    bucket: str
    count: int

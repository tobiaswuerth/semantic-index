from pydantic import BaseModel


class ReadContentResult(BaseModel):
    section: str

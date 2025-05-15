from datetime import datetime
from typing import NamedTuple, Optional


class Source(NamedTuple):
    id: Optional[int]
    uri: str
    last_modified: datetime
    last_processed: Optional[datetime]

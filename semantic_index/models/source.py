from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class Source:
    id: Optional[int]
    uri: str
    last_modified: datetime
    last_processed: Optional[datetime]

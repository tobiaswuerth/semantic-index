from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class Source:
    id: Optional[int]
    uri: str
    last_modified: datetime
    last_processed: Optional[datetime]
    error: bool = False
    error_message: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "uri": self.uri,
            "last_modified": self.last_modified.isoformat(),
            "last_processed": (
                self.last_processed.isoformat() if self.last_processed else None
            ),
            "error": self.error,
            "error_message": self.error_message,
        }

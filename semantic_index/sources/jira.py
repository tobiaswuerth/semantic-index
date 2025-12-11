import logging
from typing import Iterator
import requests
from datetime import datetime
from tqdm import tqdm

from ..data import Source, SourceType
from .base_handler import BaseSourceHandler

logger = logging.getLogger(__name__)


class JiraSourceHandler(BaseSourceHandler):
    handler_name = "Jira"
    source_types = {
        "Issue": ["issue"],
        "Comment": ["comment"],
        "Attachment": ["attachment"],
    }

    def __init__(self):
        super().__init__()

    def _search(self, base_url: str, key: str, start_at: int):
        query = {
            "jql": "",
            "maxResults": 1000,
            "startAt": start_at,
            "fields": "id,key,summary,created,updated,attachment,filename,comment,author",
        }
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        search_url = f"{base_url}/rest/api/2/search"
        response = requests.get(search_url, headers=headers, params=query)
        response.raise_for_status()
        return response.json()

    def parse_date(self, date_str: str):
        # e.g. "created": "2018-11-14T10:23:58.137+0100",
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")

    def crawl(self, base: str, **kwargs) -> Iterator[Source]:
        api_key = kwargs.get("key")
        assert api_key, "API key is required to crawl Jira sources"

        handler = self.get_handler_model()
        assert handler

        type_issue: SourceType = self.get_type_model("Issue")
        type_comment: SourceType = self.get_type_model("Comment")
        type_attachment: SourceType = self.get_type_model("Attachment")

        # get all issues from Jira API
        idx = 0
        results = [1]
        while results:
            data = self._search(base, api_key, idx)
            results = data.get("issues", [])
            for issue in results:
                issue_key = issue["key"]
                ticket_url = f"{base}/browse/{issue_key}"
                fields = issue["fields"]

                # Create Source for the issue itself
                cdate = fields["created"]
                mdate = self.parse_date(fields.get("updated", cdate))
                cdate = self.parse_date(cdate)
                yield Source(
                    id=None,
                    source_handler_id=handler.id,
                    source_type_id=type_issue.id,
                    uri=issue["self"],
                    resolved_to=ticket_url,
                    title=f"Jira Issue {issue_key}: {fields['summary']}",
                    obj_created=cdate,
                    obj_modified=mdate,
                    last_checked=datetime.now(),
                    last_processed=None,
                    error=False,
                    error_message=None,
                )

                # Create Sources for comments
                comments = fields.get("comment", {}).get("comments", [])
                for comment in comments:
                    comment_id = comment["id"]

                    cdate = comment["created"]
                    mdate = self.parse_date(comment.get("updated", cdate))
                    cdate = self.parse_date(cdate)
                    yield Source(
                        id=None,
                        source_handler_id=handler.id,
                        source_type_id=type_comment.id,
                        uri=comment["self"],
                        resolved_to=f"{ticket_url}?focusedCommentId={comment_id}",
                        title=f"Comment {comment_id} on Jira Issue {issue_key}",
                        obj_created=cdate,
                        obj_modified=mdate,
                        last_checked=datetime.now(),
                        last_processed=None,
                        error=False,
                        error_message=None,
                    )

                # Create Sources for attachments
                attachments = fields.get("attachment", [])
                for attachment in attachments:
                    filename = attachment["filename"]
                    cdate = attachment["created"]
                    mdate = self.parse_date(attachment.get("updated", cdate))
                    cdate = self.parse_date(cdate)
                    yield Source(
                        id=None,
                        source_handler_id=handler.id,
                        source_type_id=type_attachment.id,
                        uri=attachment["self"],
                        resolved_to=attachment["content"],
                        title=f"Attachment {filename} on Jira Issue {issue_key}",
                        obj_created=cdate,
                        obj_modified=mdate,
                        last_checked=datetime.now(),
                        last_processed=None,
                        error=False,
                        error_message=None,
                    )

            idx += len(results)

    def _read_source(self, source: Source) -> str:
        raise NotImplementedError()

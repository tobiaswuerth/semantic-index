import logging
from typing import Iterator
import requests
from datetime import datetime
from tqdm import tqdm

from ..data import Source, SourceType
from ..config import config
from .base_handler import BaseSourceHandler
from .io import supported_extensions, extension_to_reader, TempDirectory

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

    def _jira_auth_req(self, url: str, params: dict = {}) -> requests.Response:
        headers = {
            "Authorization": f"Bearer {config.jira.api_key}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response

    def _jira_search(self, base_url: str, start_at: int) -> dict:
        query = {
            "jql": "",
            "maxResults": 1000,
            "startAt": start_at,
            "fields": "id,key,summary,created,updated,attachment,filename,comment,author",
        }
        search_url = f"{base_url}/rest/api/2/search"
        return self._jira_auth_req(search_url, params=query).json()

    def parse_date(self, date_str: str):
        # e.g. "created": "2018-11-14T10:23:58.137+0100",
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")

    def crawl(self, base: str) -> Iterator[Source]:
        handler = self.get_handler_model()
        assert handler

        type_issue: SourceType = self.source_type_by_name("Issue")
        type_comment: SourceType = self.source_type_by_name("Comment")
        type_attachment: SourceType = self.source_type_by_name("Attachment")

        # get all issues from Jira API
        idx = 0
        results = [1]
        while results:
            data = self._jira_search(base, idx)
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
                    title=f"Jira {issue_key}: {fields['summary']}",
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
                        title=f"Jira {issue_key} Comment: {comment_id}",
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
                    ext = "." + filename.split(".")[-1].lower()
                    if ext not in supported_extensions:
                        logger.info(
                            f"Skipping unsupported attachment type: {filename} ({ext})"
                        )
                        continue

                    cdate = attachment["created"]
                    mdate = self.parse_date(attachment.get("updated", cdate))
                    cdate = self.parse_date(cdate)
                    yield Source(
                        id=None,
                        source_handler_id=handler.id,
                        source_type_id=type_attachment.id,
                        uri=attachment["self"],
                        resolved_to=attachment["content"],
                        title=f"Jira {issue_key} Attachment: {filename}",
                        obj_created=cdate,
                        obj_modified=mdate,
                        last_checked=datetime.now(),
                        last_processed=None,
                        error=False,
                        error_message=None,
                    )

            idx += len(results)

    def _read_source(self, source: Source) -> str:
        if source.source_type_id == self.source_type_by_name("Issue").id:
            return self._read_issue(source)
        elif source.source_type_id == self.source_type_by_name("Comment").id:
            return self._read_comment(source)
        elif source.source_type_id == self.source_type_by_name("Attachment").id:
            return self._read_attachment(source)

        raise NotImplementedError(f"Unknown type: {source.source_type_id}")

    def _read_issue(self, source: Source) -> str:
        data = self._jira_auth_req(source.uri).json()

        key = data["key"]

        fields = data["fields"]

        issuetype = fields.get("issuetype", {}).get("name", "N/A")

        parent = None
        has_parent = "parent" in fields
        if has_parent:
            parent = fields["parent"]
            parent = f'{parent.get("key", "N/A")}: {parent.get("fields", {}).get("summary", "")}'

        project = fields.get("project", {}).get("name", "N/A")
        fix_versions = ", ".join(
            [v.get("name", "") for v in fields.get("fixVersions", [])]
        )

        resolution = fields.get("resolution", {})
        resolution = (
            "Unresolved" if not resolution else resolution.get("name", "Unresolved")
        )

        resolutiondate = fields.get("resolutiondate", "N/A")
        createdate = fields.get("created", "N/A")
        priority = fields.get("priority", {}).get("name", "N/A")
        labels = ", ".join(fields.get("labels", []))

        issuelinks = []
        for link in fields.get("issuelinks", []):
            type_ = "inward" if "inwardIssue" in link else "outward"
            link_type = link["type"][type_]
            linked_key = link[f"{type_}Issue"]["key"]
            linked_summary = link[f"{type_}Issue"]["fields"].get("summary", "")
            issuelinks.append(f"- {link_type} {linked_key}: {linked_summary}")
        issuelinks = "\n".join(issuelinks) if issuelinks else "N/A"

        assignee = fields.get("assignee", {}).get("displayName", "Unassigned")
        updatedate = fields.get("updated", "N/A")
        status = fields.get("status", {}).get("name", "N/A")
        components = ", ".join(
            [c.get("name", "") for c in fields.get("components", [])]
        )
        description = fields.get("description", "<no description>")

        attachments = "\n".join(
            [f"- {att.get('filename', 'N/A')}" for att in fields.get("attachment", [])]
        )
        summary = fields.get("summary", "<no summary>")
        creator = fields.get("creator", {}).get("displayName", "N/A")

        subtasks = "\n".join(
            [
                f"- {subtask.get('key', 'N/A')}: {subtask.get('fields', {}).get('summary', '')}"
                for subtask in fields.get("subtasks", [])
            ]
        )
        reporter = fields.get("reporter", {}).get("displayName", "N/A")

        comments = "\n".join(
            [
                f"- {comment.get('updateAuthor', {}).get('displayName', 'N/A')}: {comment.get('body', '')}"
                for comment in fields.get("comment", {}).get("comments", [])
            ]
        )

        # Format the issue data into a string
        result = (
            f"JIRA Issue {key}: {summary}\n"
            f"Project: {project} / Type: {issuetype} / Priority: {priority}\n"
            f"Status: {status} / Resolution: {resolution} / Fix Versions: {fix_versions}\n"
            f"Created: {createdate} / Updated: {updatedate} / Resolved: {resolutiondate}\n"
            f"Assignee: {assignee} / Reporter: {reporter} / Creator: {creator}\n"
            f"Labels: {labels} / Components: {components}\n"
            f"Description: {description}\n"
            f"Issue Links: {issuelinks}\n"
            f"Subtasks: {subtasks}\n"
            f"Attachments: {attachments}\n"
            f"Comments: {comments}\n"
        )
        if has_parent and parent:
            result += f"Parent Issue: {parent}"

        return result

    def _read_comment(self, source: Source) -> str:
        data = self._jira_auth_req(source.uri).json()
        author = data.get("updateAuthor", {}).get("displayName", "N/A")
        createdate = data.get("created", "N/A")
        updatedate = data.get("updated", createdate)
        body = data.get("body", "<no content>")
        return (
            f"JIRA Comment by {author}\n"
            f"Created: {createdate} / Updated: {updatedate}\n"
            f"Content:\n{body}"
        )

    def _read_attachment(self, source: Source) -> str:
        metadata = self._jira_auth_req(source.uri).json()

        filename = metadata.get("filename", "N/A")
        ext = "." + filename.split(".")[-1].lower()
        if ext not in supported_extensions:
            raise ValueError(f"Unsupported attachment extension: {ext}")

        assert source.resolved_to
        with TempDirectory() as temp_dir:
            binary = self._jira_auth_req(source.resolved_to).content
            temp_path = temp_dir / filename
            with open(temp_path, "wb") as f:
                f.write(binary)
            reader = extension_to_reader[ext]
            content = reader(str(temp_path))

        author = metadata.get("author", {}).get("displayName", "N/A")
        created = metadata.get("created", "N/A")
        updated = metadata.get("updated", created)
        update_author = metadata.get("updateAuthor", {}).get("displayName", "N/A")
        size = metadata.get("size", "N/A")
        mime_type = metadata.get("mimeType", "N/A")
        body = content if content else "<no content>"

        return (
            f"JIRA Attachment: {filename}\n"
            f"Mime Type: {mime_type} / Size: {size} bytes\n"
            f"Uploaded by: {author} / Created: {created}\n"
            f"Last updated by: {update_author} / Updated: {updated}\n"
            f"Content:\n{body}"
        )

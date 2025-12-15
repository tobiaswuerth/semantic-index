import logging
from typing import Iterator
import requests
from datetime import datetime
from enum import Enum

from ..data import Source
from ..config import config
from .base_handler import BaseSourceHandler
from .io import (
    get_file_extension,
    supported_extensions,
    extension_to_reader,
    TempDirectory,
)

logger = logging.getLogger(__name__)


class JiraType(Enum):
    ISSUE = 0
    COMMENT = 1
    ATTACHMENT = 2


class JiraSourceHandler(BaseSourceHandler):
    def get_name(self) -> str:
        return "Jira"

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
            "maxResults": 250,
            "startAt": start_at,
            "fields": "id,key,summary,created,updated,attachment,filename,comment,author",
        }
        search_url = f"{base_url}/rest/api/2/search"
        return self._jira_auth_req(search_url, params=query).json()

    def index_all(self, base: str) -> Iterator[Source]:
        idx = 0
        results = [1]
        while results:
            data = self._jira_search(base, idx)
            results = data.get("issues", [])
            for issue in results:
                issue_key = issue.get("key", None)
                fields = issue.get("fields") or {}
                yield self._index_issue(issue["self"], issue)

                for comment in (fields.get("comment") or {}).get("comments", []):
                    yield self._index_comment(comment["self"], comment, issue_key)

                for attachment in fields.get("attachment", []):
                    try:
                        yield self._index_attachment(attachment, issue_key=issue_key)
                    except ValueError as ve:
                        logger.warning(f"Skipping attachment due to error: {ve}")

            idx += len(results)

    def get_type_enum(self, uri: str) -> JiraType:
        if "/attachment/" in uri:
            return JiraType.ATTACHMENT
        elif "/comment/" in uri:
            return JiraType.COMMENT
        elif "/issue/" in uri:
            return JiraType.ISSUE

        raise ValueError(f"Cannot identify jira source type from uri: {uri}")

    def index_one(self, uri: str) -> Source:
        data = self._jira_auth_req(uri).json()
        type_ = self.get_type_enum(uri)
        if type_ == JiraType.ATTACHMENT:
            return self._index_attachment(data)
        elif type_ == JiraType.COMMENT:
            return self._index_comment(uri, data)
        elif type_ == JiraType.ISSUE:
            return self._index_issue(uri, data)

        raise ValueError(f"Cannot identify jira source type from uri: {uri}")

    def get_create_modify_dates(self, data: dict) -> tuple[datetime, datetime]:
        def _parse_date(date_str: str):
            # e.g. "created": "2018-11-14T10:23:58.137+0100",
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")

        cdate = data["created"]
        mdate = _parse_date(data.get("updated", cdate))
        cdate = _parse_date(cdate)
        assert cdate <= mdate
        return cdate, mdate

    def _index_attachment(self, data: dict, issue_key: str | None = None) -> Source:
        filename = data["filename"]
        ext = get_file_extension(filename)
        tags = [
            self.handler_tag,
            self.repo_tag.get_or_create("Attachment"),
            self.repo_tag.get_or_create(ext),
        ]
        cdate, mdate = self.get_create_modify_dates(data)
        key_insert = issue_key + " " if issue_key else ""
        return Source(
            id=None,
            source_handler_id=self.handler.id,
            uri=data["self"],
            resolved_to=data["content"],
            title=f"Jira {key_insert}Attachment: {filename}",
            obj_created=cdate,
            obj_modified=mdate,
            last_checked=datetime.now(),
            last_processed=None,
            error=False,
            error_message=None,
            tags=tags,
        )

    def _index_comment(
        self, uri: str, data: dict, issue_key: str | None = None
    ) -> Source:
        if issue_key is None:
            issue_url = uri.split("/comment/")[0]
            issue_data = self._jira_auth_req(issue_url).json()
            issue_key = issue_data.get("key", None)

        key_insert = issue_key + " " if issue_key else ""
        ticket_url = f"{uri.split('/rest/api/')[0]}/browse/{issue_key}"
        tags = [self.handler_tag, self.repo_tag.get_or_create("Comment")]
        cdate, mdate = self.get_create_modify_dates(data)
        return Source(
            id=None,
            source_handler_id=self.handler.id,
            uri=data["self"],
            resolved_to=ticket_url,
            title=f"Jira {key_insert}Comment: {data['id']}",
            obj_created=cdate,
            obj_modified=mdate,
            last_checked=datetime.now(),
            last_processed=None,
            error=False,
            error_message=None,
            tags=tags,
        )

    def _index_issue(self, uri: str, data: dict) -> Source:
        issue_key = data["key"]
        ticket_url = f"{uri.split('/rest/api/')[0]}/browse/{issue_key}"
        fields = data["fields"]
        tags = [self.handler_tag, self.repo_tag.get_or_create("Issue")]
        cdate, mdate = self.get_create_modify_dates(fields)
        return Source(
            id=None,
            source_handler_id=self.handler.id,
            uri=data["self"],
            resolved_to=ticket_url,
            title=f"Jira {issue_key}: {fields['summary']}",
            obj_created=cdate,
            obj_modified=mdate,
            last_checked=datetime.now(),
            last_processed=None,
            error=False,
            error_message=None,
            tags=tags,
        )

    def _read_source(self, source: Source) -> str:
        type_ = self.get_type_enum(source.uri)
        if type_ == JiraType.ISSUE:
            return self._read_issue(source)
        elif type_ == JiraType.COMMENT:
            return self._read_comment(source)
        elif type_ == JiraType.ATTACHMENT:
            return self._read_attachment(source)

        raise NotImplementedError(f"Unknown type: {source.uri}")

    def _read_issue(self, source: Source) -> str:
        data = self._jira_auth_req(source.uri).json()

        key = data["key"]

        fields = data["fields"]

        issuetype = (fields.get("issuetype") or {}).get("name", "N/A")

        parent = None
        has_parent = "parent" in fields
        if has_parent:
            parent = fields["parent"]
            parent = f'{parent.get("key", "N/A")}: {(parent.get("fields") or {}).get("summary", "")}'

        project = (fields.get("project") or {}).get("name", "N/A")
        fix_versions = ", ".join(
            [v.get("name", "") for v in fields.get("fixVersions", [])]
        )

        resolution = fields.get("resolution") or {}
        resolution = (
            "Unresolved" if not resolution else resolution.get("name", "Unresolved")
        )

        resolutiondate = fields.get("resolutiondate", "N/A")
        createdate = fields.get("created", "N/A")
        priority = (fields.get("priority") or {}).get("name", "N/A")
        labels = ", ".join(fields.get("labels", []))

        issuelinks = []
        for link in fields.get("issuelinks", []):
            type_ = "inward" if "inwardIssue" in link else "outward"
            link_type = link["type"][type_]
            linked_key = link[f"{type_}Issue"]["key"]
            linked_summary = link[f"{type_}Issue"]["fields"].get("summary", "")
            issuelinks.append(f"- {link_type} {linked_key}: {linked_summary}")
        issuelinks = "\n".join(issuelinks) if issuelinks else "N/A"

        assignee = (fields.get("assignee") or {}).get("displayName", "Unassigned")
        updatedate = fields.get("updated", "N/A")
        status = (fields.get("status") or {}).get("name", "N/A")
        components = ", ".join(
            [c.get("name", "") for c in fields.get("components", [])]
        )
        description = fields.get("description", "<no description>")

        attachments = "\n".join(
            [f"- {att.get('filename', 'N/A')}" for att in fields.get("attachment", [])]
        )
        summary = fields.get("summary", "<no summary>")
        creator = (fields.get("creator") or {}).get("displayName", "N/A")

        subtasks = "\n".join(
            [
                f"- {subtask.get('key', 'N/A')}: {(subtask.get('fields') or {}).get('summary', '')}"
                for subtask in fields.get("subtasks", [])
            ]
        )
        reporter = (fields.get("reporter") or {}).get("displayName", "N/A")
        comments = "\n".join(
            [
                f"- {(comment.get('updateAuthor') or {}).get('displayName', 'N/A')}: {comment.get('body', '')}"
                for comment in (fields.get("comment") or {}).get("comments", [])
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
        author = (data.get("updateAuthor") or {}).get("displayName", "N/A")
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
        ext = get_file_extension(filename)
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

        author = (metadata.get("author") or {}).get("displayName", "N/A")
        created = metadata.get("created", "N/A")
        updated = metadata.get("updated", created)
        update_author = (metadata.get("updateAuthor") or {}).get("displayName", "N/A")
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

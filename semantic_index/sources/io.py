import docx
import extract_msg
from extract_msg import Message
import pymupdf
import shutil
import tempfile
from pathlib import Path
from charset_normalizer import from_bytes


def _read_plaintext(path: str) -> str:
    with open(path, "rb") as f:
        raw_data = f.read()
    result = from_bytes(raw_data).best()
    if result is None:
        raise ValueError(f"Failed to decode file: {path}")
    return str(result)


def _read_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join([para.text for para in doc.paragraphs])


def _read_pdf(path: str) -> str:
    doc = pymupdf.open(path)
    return "".join([str(page.get_text()) for page in doc])


def _read_msg(path: str) -> str:
    with extract_msg.Message(path) as mail:
        mail: Message = mail
        result = f"{mail.sender} -> {mail.to}\n{mail.date}: {mail.subject}\n{mail.body}"
    return result


extension_to_reader = {
    ".txt": _read_plaintext,
    ".md": _read_plaintext,
    ".csv": _read_plaintext,
    ".sql": _read_plaintext,
    ".xml": _read_plaintext,
    ".log": _read_plaintext,
    ".docx": _read_docx,
    ".pdf": _read_pdf,
    ".msg": _read_msg,
}
supported_extensions = set(extension_to_reader.keys())


class TempDirectory:
    def __init__(self):
        self.path = Path(tempfile.mkdtemp())

    def __enter__(self) -> Path:
        return self.path

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        shutil.rmtree(self.path)

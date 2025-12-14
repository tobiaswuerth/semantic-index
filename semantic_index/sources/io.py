import docx
import extract_msg
from extract_msg import Message
import pymupdf
import shutil
import tempfile
from pathlib import Path
import logging
from charset_normalizer import from_bytes
import pandas as pd
import sys
import os
from odf import text, teletype
from odf.opendocument import load

from .external import run_subprocess_with_timeout


logger = logging.getLogger(__name__)


def _read_plaintext(path: str) -> str:
    with open(path, "rb") as f:
        raw_data = f.read()

    result = from_bytes(raw_data).best()
    if result is None:
        logger.warning(f"Failed to detect encoding for file: {path}, using fallback")
        return raw_data.decode(errors="replace")

    encoding = result.encoding
    logger.debug(f"Detected encoding '{encoding}' for file: {path}")
    return raw_data.decode(encoding)


def _read_pandas(path: str) -> str:
    df = pd.read_excel(path, sheet_name=None)
    csv = ""
    for sheet_name, sheet_df in df.items():
        csv += f"--- Sheet: {sheet_name} ---\n"
        csv += sheet_df.to_csv(index=False)
        csv += "\n"
    return csv


def _read_excel(path: str) -> str:
    try:
        return _read_pandas(path)
    except Exception as e:
        logger.warning(
            (
                f"Pandas failed to read Excel file {path} with error: {e}. "
                "Falling back to external script."
            )
        )

    try:
        read_script = "semantic_index/sources/external/read_excel.py"
        assert os.path.isfile(read_script), f"Script not found: {read_script}"
        assert os.path.isfile(path), f"Excel file not found: {path}"

        cmd = [sys.executable, read_script, path]
        result = run_subprocess_with_timeout(cmd, timeout_seconds=30)
        return result
    except Exception as e:
        logger.error(f"Failed to read Excel file {path} with external script: {e}")
        raise


def _read_odt(path: str) -> str:
    document = load(path)
    all_paragraphs = document.getElementsByType(text.P)
    content = "\n".join(teletype.extractText(p) for p in all_paragraphs)
    return content


def _read_docx(path: str) -> str:
    try:
        doc = docx.Document(path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        logger.warning(
            (
                f"python-docx failed to read DOCX file {path} with error: {e}. "
                "Falling back to external script."
            )
        )

    return _read_word(path)


def _read_word(path: str) -> str:
    try:
        read_script = "semantic_index/sources/external/read_word.py"
        assert os.path.isfile(read_script), f"Script not found: {read_script}"
        assert os.path.isfile(path), f"Word file not found: {path}"

        cmd = [sys.executable, read_script, path]
        result = run_subprocess_with_timeout(cmd, timeout_seconds=30)
        return result
    except Exception as e:
        logger.error(f"Failed to read Word file {path} with external script: {e}")
        raise


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
    ".pdf": _read_pdf,
    ".msg": _read_msg,
    # docs
    ".odt": _read_odt,
    ".doc": _read_word,
    ".dot": _read_word,
    ".wbk": _read_docx,
    ".docx": _read_docx,
    ".docm": _read_docx,
    ".dotx": _read_docx,
    ".dotm": _read_docx,
    # Spreadsheet
    ".ods": _read_pandas,
    ".csv": _read_plaintext,
    ".tsv": _read_plaintext,
    ".xls": _read_excel,
    ".xlt": _read_excel,
    ".xla": _read_excel,
    ".xlsx": _read_excel,
    ".xlsm": _read_excel,
    ".xltx": _read_excel,
    ".xltm": _read_excel,
    ".xlsb": _read_excel,
}
supported_extensions = set(extension_to_reader.keys())


class TempDirectory:
    def __init__(self):
        self.path = Path(tempfile.mkdtemp())

    def __enter__(self) -> Path:
        return self.path

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        shutil.rmtree(self.path)

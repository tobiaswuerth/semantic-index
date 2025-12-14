import win32com.client
import json
import pythoncom
import sys


def _read_word_file(path: str) -> str:
    """
    Reads a Word file using win32com.client and returns its content as a string.
    """
    pythoncom.CoInitialize()
    word = None
    doc = None

    try:
        word = win32com.client.Dispatch("Word.Application")
        word.DisplayAlerts = False
        word.ScreenUpdating = False
        word.Visible = False

        doc = word.Documents.Open(
            FileName=path,
            ConfirmConversions=False,
            ReadOnly=True,
            AddToRecentFiles=False,
            Revert=False,
            Visible=False,
            OpenAndRepair=False,
            NoEncodingDialog=True,
        )
        content = doc.Range().Text
    except Exception as e:
        print(f"ERROR: Word automation failed: {e}", file=sys.stderr)
        raise

    finally:
        if doc:
            doc.Close(SaveChanges=False)
        if word:
            word.Quit()

        del doc
        del word
        pythoncom.CoUninitialize()

    return json.dumps(content, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read_word.py <path_to_word_file>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        result_json = _read_word_file(file_path)
        print(result_json)
    except Exception:
        sys.exit(1)

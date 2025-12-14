import win32com.client
import json
import pythoncom
import sys


def _parse_cell(cell):
    if cell is None:
        return None
    if isinstance(cell, str):
        return " ".join(cell.split())
    return cell


def _parse_row(row):
    row_cleaned = []
    for cell in row:
        if cell is None:
            continue
        row_cleaned.append(_parse_cell(cell))
    if not row_cleaned:
        return None
    return row_cleaned


def _parse_sheet(sheet: win32com.client.CDispatch) -> dict | None:
    values = sheet.UsedRange.Value
    if values is None:
        return None

    rows = []
    if not isinstance(values, tuple):
        cell = _parse_cell(values)
        if cell is not None:
            rows.append([cell])
    else:
        for row in values:
            cleaned_row = _parse_row(row)
            if cleaned_row:
                rows.append(cleaned_row)
    if not rows:
        return None

    return {
        "name": sheet.Name,
        "rows": rows,
    }


def _read_excel_file(path: str) -> str:
    """
    Reads an Excel file using win32com.client and returns its content as a string.
    """
    pythoncom.CoInitialize()
    excel = None
    workbook = None

    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.DisplayAlerts = False
        excel.AskToUpdateLinks = False
        excel.ScreenUpdating = False
        excel.Visible = False

        # todo: when opening password-protected files, prevent prompts
        # setting Password and WriteResPassword to "" does not help
        workbook = excel.Workbooks.Open(
            Filename=path,
            UpdateLinks=0,
            ReadOnly=True,
            IgnoreReadOnlyRecommended=True,
            Editable=False,
            Notify=False,
            AddToMru=False,
            Local=False,
            CorruptLoad=0,
        )

        content = []
        for sheet in workbook.Sheets:
            sheet_data = _parse_sheet(sheet)
            if sheet_data:
                content.append(sheet_data)

    except Exception as e:
        print(f"ERROR: Excel automation failed: {e}", file=sys.stderr)
        raise

    finally:
        if workbook:
            workbook.Close(SaveChanges=False)
        if excel:
            excel.Quit()

        del workbook
        del excel
        pythoncom.CoUninitialize()

    return json.dumps(content, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read_excel.py <path_to_excel_file>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        result_json = _read_excel_file(file_path)
        print(result_json)
    except Exception:
        sys.exit(1)

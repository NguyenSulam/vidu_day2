from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


SPREADSHEET_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"pr": "http://schemas.openxmlformats.org/package/2006/relationships"}
EXCEL_EPOCH = datetime(1899, 12, 30)
EMPTY_VALUE = "[trống]"
OUTPUT_HEADERS = ["STT", "Ngày", "Tên phân xưởng", "Nội dung"]


@dataclass(frozen=True)
class RawReport:
    source_file: str
    workshop: str
    workshop_order: int
    source_stt: str
    work_date: date
    start_time: time
    shift_lead: str
    content: str


@dataclass(frozen=True)
class DailyReport:
    work_date: date
    workshop: str
    workshop_order: int
    start_time: time
    end_time: time
    shift_lead: str
    content: str


def column_name(cell_ref: str) -> str:
    return "".join(ch for ch in cell_ref if ch.isalpha())


def column_index(name: str) -> int:
    result = 0
    for ch in name:
        result = result * 26 + ord(ch.upper()) - 64
    return result - 1


def column_letter(index: int) -> str:
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def read_shared_strings(zipped_xlsx: ZipFile) -> list[str]:
    try:
        root = ET.fromstring(zipped_xlsx.read("xl/sharedStrings.xml"))
    except KeyError:
        return []

    values = []
    for item in root.findall("m:si", SPREADSHEET_NS):
        values.append("".join(text.text or "" for text in item.findall(".//m:t", SPREADSHEET_NS)))
    return values


def first_sheet_path(zipped_xlsx: ZipFile) -> str:
    workbook = ET.fromstring(zipped_xlsx.read("xl/workbook.xml"))
    sheet = workbook.find("m:sheets/m:sheet", SPREADSHEET_NS)
    if sheet is None:
        raise ValueError("Workbook does not contain any sheet")

    relationship_id = sheet.attrib[
        "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    ]
    relationships = ET.fromstring(zipped_xlsx.read("xl/_rels/workbook.xml.rels"))
    for rel in relationships.findall("pr:Relationship", REL_NS):
        if rel.attrib["Id"] == relationship_id:
            target = rel.attrib["Target"]
            return "xl/" + target.lstrip("/") if not target.startswith("xl/") else target

    raise ValueError("Cannot find first worksheet relationship")


def read_cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    value = cell.find("m:v", SPREADSHEET_NS)

    if cell_type == "inlineStr":
        return "".join(text.text or "" for text in cell.findall(".//m:t", SPREADSHEET_NS))

    if value is None:
        return ""

    raw_value = value.text or ""
    if cell_type == "s" and raw_value.isdigit():
        shared_index = int(raw_value)
        if shared_index < len(shared_strings):
            return shared_strings[shared_index]

    return raw_value


def read_xlsx_rows(path: Path) -> list[list[str]]:
    with ZipFile(path) as zipped_xlsx:
        shared_strings = read_shared_strings(zipped_xlsx)
        worksheet = ET.fromstring(zipped_xlsx.read(first_sheet_path(zipped_xlsx)))
        rows = []

        for row in worksheet.findall(".//m:sheetData/m:row", SPREADSHEET_NS):
            values: list[str] = []
            for cell in row.findall("m:c", SPREADSHEET_NS):
                cell_ref = cell.attrib.get("r", "A")
                index = column_index(column_name(cell_ref))
                while len(values) <= index:
                    values.append("")
                values[index] = read_cell_value(cell, shared_strings)
            rows.append(values)

        return rows


def parse_excel_date(value: str) -> date:
    if not str(value).strip():
        raise ValueError("Ngày bị trống")

    text = str(value).strip()
    try:
        return (EXCEL_EPOCH + timedelta(days=float(text))).date()
    except ValueError:
        pass

    for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue

    raise ValueError(f"Không đọc được ngày: {value!r}")


def parse_excel_time(value: str) -> time:
    if not str(value).strip():
        raise ValueError("Thời gian bị trống")

    text = str(value).strip()
    try:
        seconds = round(float(text) * 86400) % 86400
        return time(hour=seconds // 3600, minute=(seconds % 3600) // 60, second=seconds % 60)
    except ValueError:
        pass

    for pattern in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(text, pattern).time()
        except ValueError:
            continue

    raise ValueError(f"Không đọc được thời gian: {value!r}")


def add_hours(value: time, hours: int) -> time:
    base = datetime.combine(date(2000, 1, 1), value)
    return (base + timedelta(hours=hours)).time()


def format_time(value: time) -> str:
    return value.strftime("%H:%M")


def extract_workshop(path: Path) -> tuple[str, int]:
    match = re.search(r"px(\d+)", path.stem, flags=re.IGNORECASE)
    if not match:
        return path.stem, 999_999

    number = int(match.group(1))
    return f"Phân xưởng {number}", number


def read_step1(data_dir: Path) -> list[RawReport]:
    reports: list[RawReport] = []
    files = sorted(path for path in data_dir.glob("*.xlsx") if not path.name.startswith("~$"))

    for path in files:
        rows = read_xlsx_rows(path)
        workshop, workshop_order = extract_workshop(path)

        for row_number, row in enumerate(rows[1:], start=2):
            row = row + [""] * (5 - len(row))
            try:
                reports.append(
                    RawReport(
                        source_file=path.name,
                        workshop=workshop,
                        workshop_order=workshop_order,
                        source_stt=row[0],
                        work_date=parse_excel_date(row[1]),
                        start_time=parse_excel_time(row[2]),
                        shift_lead=row[3],
                        content=row[4],
                    )
                )
            except ValueError as exc:
                raise ValueError(f"{path.name}, dòng Excel {row_number}: {exc}") from exc

    return reports


def summarize_step2(raw_reports: Iterable[RawReport]) -> list[DailyReport]:
    reports = [
        DailyReport(
            work_date=raw.work_date,
            workshop=raw.workshop,
            workshop_order=raw.workshop_order,
            start_time=raw.start_time,
            end_time=add_hours(raw.start_time, 8),
            shift_lead=raw.shift_lead,
            content=raw.content,
        )
        for raw in raw_reports
    ]
    return sorted(reports, key=lambda item: (item.work_date, item.workshop_order, item.start_time))


def build_excel_rows_step3(reports: Iterable[DailyReport]) -> list[list[str | int]]:
    rows: list[list[str | int]] = [OUTPUT_HEADERS]
    for index, report in enumerate(reports, start=1):
        shift_lead = report.shift_lead if report.shift_lead.strip() else EMPTY_VALUE
        content = report.content if report.content.strip() else EMPTY_VALUE
        report_content = (
            f"Ca {format_time(report.start_time)}-{format_time(report.end_time)}. "
            f"Trưởng ca: {shift_lead}. Nội dung: {content}"
        )
        rows.append([index, report.work_date.isoformat(), report.workshop, report_content])
    return rows


def worksheet_xml(rows: list[list[str | int]]) -> str:
    sheet_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for column_index_value, value in enumerate(row, start=1):
            ref = f"{column_letter(column_index_value)}{row_index}"
            cells.append(
                f'<c r="{ref}" t="inlineStr" s="0"><is><t>{escape(str(value))}</t></is></c>'
            )
        sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        "<sheetData>"
        + "".join(sheet_rows)
        + "</sheetData></worksheet>"
    )


def write_xlsx(path: Path, rows: list[list[str | int]]) -> None:
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        "</Types>"
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Tong hop" sheetId="1" r:id="rId1"/></sheets>'
        "</workbook>"
    )
    workbook_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
        "</Relationships>"
    )
    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="1"><font><sz val="11"/><name val="Times New Roman"/><family val="2"/>'
        '<scheme val="minor"/></font></fonts>'
        '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
        '<borders count="1"><border/></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        '</styleSheet>'
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, "w", ZIP_DEFLATED) as zipped_xlsx:
        zipped_xlsx.writestr("[Content_Types].xml", content_types)
        zipped_xlsx.writestr("_rels/.rels", root_rels)
        zipped_xlsx.writestr("xl/workbook.xml", workbook)
        zipped_xlsx.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        zipped_xlsx.writestr("xl/worksheets/sheet1.xml", worksheet_xml(rows))
        zipped_xlsx.writestr("xl/styles.xml", styles_xml)


def default_output_path(output_dir: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return output_dir / f"Baocao_TH_{timestamp}.xlsx"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Đọc data/*.xlsx, tổng hợp theo ngày và xuất file Excel báo cáo 4 cột."
    )
    parser.add_argument("--data-dir", default="data", type=Path, help="Thư mục chứa file XLSX đầu vào.")
    parser.add_argument("--output-dir", default="output", type=Path, help="Thư mục lưu file XLSX tổng hợp.")
    parser.add_argument("--output-file", type=Path, help="Đường dẫn file XLSX đầu ra.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_dir = args.data_dir
    output_path = args.output_file or default_output_path(args.output_dir)

    if not data_dir.exists():
        print(f"Không tìm thấy thư mục dữ liệu: {data_dir}", file=sys.stderr)
        return 1

    try:
        raw_reports = read_step1(data_dir)
        daily_reports = summarize_step2(raw_reports)
        output_rows = build_excel_rows_step3(daily_reports)
        write_xlsx(output_path, output_rows)
    except Exception as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1

    blank_rows = sum(
        1 for item in daily_reports if not item.shift_lead.strip() or not item.content.strip()
    )
    print(f"Đã đọc {len(raw_reports)} dòng dữ liệu từ {data_dir}.")
    print(f"Đã tạo {len(output_rows) - 1} dòng báo cáo tổng hợp.")
    print(f"Số dòng có Trưởng ca hoặc Nội dung trống: {blank_rows}.")
    print(f"File đầu ra: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

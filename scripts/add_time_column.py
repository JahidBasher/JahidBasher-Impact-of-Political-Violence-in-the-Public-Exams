"""Create a dated copy of the selected Bangladesh GED workbook.

The original workbook is never modified. Event dates are matched from an official
UCDP GED CSV by ``relid`` and validated against the event year and ``best`` death
estimate before the derived workbook is written.

Usage:
    python3 scripts/add_time_column.py --ged-csv /path/to/GEDEvent_v26_1.csv
"""

import argparse
import csv
import shutil
from copy import copy
from datetime import datetime
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "data" / "bangladesh_ged_selected_data_2011_2025.xlsx"
DEFAULT_OUTPUT = ROOT / "data" / "bangladesh_ged_selected_data_2011_2025_with_time.xlsx"


def iso_day(value: str) -> str:
    """Return the YYYY-MM-DD portion of a UCDP timestamp after validation."""
    day = value[:10]
    datetime.strptime(day, "%Y-%m-%d")
    return day


def load_dates(csv_path: Path, wanted_relids: set[str]) -> dict[str, dict[str, str]]:
    matches: dict[str, dict[str, str]] = {}
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            relid = row["relid"]
            if relid not in wanted_relids:
                continue
            if relid in matches:
                raise ValueError(f"Duplicate relid in UCDP GED file: {relid}")
            matches[relid] = row

    missing = wanted_relids - matches.keys()
    if missing:
        raise ValueError(f"Missing {len(missing)} relids in UCDP GED file: {sorted(missing)}")
    return matches


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ged-csv", type=Path, required=True)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    source_book = openpyxl.load_workbook(args.input, read_only=True, data_only=True)
    source_sheet = source_book.active
    headers = [cell.value for cell in source_sheet[1]]
    required = {"year", "relid", "best"}
    if not required.issubset(headers):
        raise ValueError(f"Input workbook is missing columns: {sorted(required - set(headers))}")
    index = {name: position for position, name in enumerate(headers)}
    source_rows = list(source_sheet.iter_rows(min_row=2, values_only=True))
    wanted_relids = {str(row[index["relid"]]) for row in source_rows}
    if len(wanted_relids) != len(source_rows):
        raise ValueError("Input workbook contains duplicate relid values")
    dates = load_dates(args.ged_csv, wanted_relids)

    time_values: dict[str, str] = {}
    exact = 0
    ranges = 0
    for row in source_rows:
        relid = str(row[index["relid"]])
        match = dates[relid]
        if int(match["year"]) != int(row[index["year"]]):
            raise ValueError(f"Year mismatch for {relid}")
        if int(match["best"]) != int(row[index["best"]]):
            raise ValueError(f"Best-death mismatch for {relid}")

        start = iso_day(match["date_start"])
        end = iso_day(match["date_end"])
        if start == end:
            time_values[relid] = start
            exact += 1
        else:
            time_values[relid] = f"{start}/{end}"
            ranges += 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.input, args.output)
    workbook = openpyxl.load_workbook(args.output)
    sheet = workbook.active
    current_headers = [cell.value for cell in sheet[1]]
    if "time" in current_headers:
        raise ValueError("Output workbook already contains a time column")

    # Insert immediately after year, keeping all original columns and values intact.
    sheet.insert_cols(2, 1)
    sheet.cell(row=1, column=2, value="time")
    source_header = sheet.cell(row=1, column=1)
    time_header = sheet.cell(row=1, column=2)
    if source_header.has_style:
        time_header._style = copy(source_header._style)
    if source_header.number_format:
        time_header.number_format = source_header.number_format
    time_header.font = copy(source_header.font)
    time_header.fill = copy(source_header.fill)
    time_header.border = copy(source_header.border)
    time_header.alignment = copy(source_header.alignment)
    time_header.protection = copy(source_header.protection)

    for row_number in range(2, sheet.max_row + 1):
        relid = str(sheet.cell(row=row_number, column=3).value)
        cell = sheet.cell(row=row_number, column=2, value=time_values[relid])
        cell.number_format = "@"
    sheet.column_dimensions["B"].width = 23

    workbook.save(args.output)
    print(
        f"wrote {args.output.relative_to(ROOT)}: {len(time_values)} dates "
        f"({exact} exact days, {ranges} closed ranges)"
    )


if __name__ == "__main__":
    main()

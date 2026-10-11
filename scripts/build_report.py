"""Build the offline HTML report from the education Excel file and the JSON output.

Usage (from the repository root, after scripts/excel_to_json.py):
    python scripts/build_report.py
Requires: openpyxl.

The report is a single self-contained HTML file: data and fonts are embedded,
so it opens in any browser with no internet connection.
"""
import base64
import json
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
EDU_FILE = ROOT / "data" / "bangladesh_ssc_hsc_district_year_education_with_exam_dates.xlsx"
JSON_FILE = ROOT / "output" / "bangladesh_conflict_education.json"
TEMPLATE = ROOT / "report" / "template.html"
FONTS = ROOT / "report" / "fonts"
OUT_FILE = ROOT / "output" / "bangladesh_exams_conflict_report.html"

FONT_FACES = [
    # (family, weight range, file)
    ("Public Sans", "400 700", "PublicSans-Variable-latin.woff2"),
    ("Source Serif 4", "600", "SourceSerif4-SemiBold-latin.woff2"),
]


def font_css():
    rules = []
    for family, weight, name in FONT_FACES:
        data = base64.b64encode((FONTS / name).read_bytes()).decode()
        rules.append(
            f'@font-face {{ font-family: "{family}"; font-style: normal; font-weight: {weight}; '
            f'font-display: swap; src: url(data:font/woff2;base64,{data}) format("woff2"); }}'
        )
    return "\n".join(rules)


def event(e):
    mapping = e["district_mapping"]
    return {
        "relid": e["relid"],
        "type": e["relid"].split("-")[2],  # UCDP type of violence: 1 state-based, 2 non-state, 3 one-sided
        "place": e["where_coordinates"],
        "desc": e["where_description"],
        "best": e["best"],
        "source": e["source_article"],
        "method": mapping["method"],
        "confidence": mapping["confidence"],
        "note": mapping.get("note", ""),
    }


def build_data():
    ws = openpyxl.load_workbook(EDU_FILE, read_only=True).active
    rows = ws.iter_rows(values_only=True)
    columns = list(next(rows))
    data = [list(r) for r in rows if any(v is not None for v in r)]
    row_index = {(r[1], r[0]): i for i, r in enumerate(data)}

    doc = json.loads(JSON_FILE.read_text())
    events = {}
    for d in doc["districts"]:
        for y in d["years"]:
            if y["conflict"]["events"]:
                events[row_index[(d["name"], y["year"])]] = [event(e) for e in y["conflict"]["events"]]
    unlocated = [{**event(e), "year": e["year"]} for e in doc["unlocated_events"]]
    return {"columns": columns, "rows": data, "events": events, "unlocated": unlocated}


def main():
    if not JSON_FILE.exists():
        sys.exit(f"{JSON_FILE.relative_to(ROOT)} not found; run scripts/excel_to_json.py first")
    template = TEMPLATE.read_text(encoding="utf-8")
    for marker in ("/*FONTS*/", "/*DATA*/null"):
        if template.count(marker) != 1:
            sys.exit(f"template must contain {marker} exactly once")

    data = build_data()
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = template.replace("/*FONTS*/", font_css()).replace("/*DATA*/null", payload)
    OUT_FILE.write_text(html, encoding="utf-8")

    located = sum(len(v) for v in data["events"].values())
    print(f"wrote {OUT_FILE.relative_to(ROOT)}: {len(data['rows'])} rows, "
          f"{located} located events, {len(data['unlocated'])} unlocated, "
          f"{OUT_FILE.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()

"""Convert the education and GED Excel files into one JSON document.

Usage (from the repository root):
    python scripts/excel_to_json.py
Requires: openpyxl (and jsonschema, optional, to validate the output).

Structure is defined in schema/bangladesh_conflict_education.schema.json; mapping
decisions are documented in docs/district_mapping_notes.md.
"""
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
EDU_FILE = ROOT / "data" / "bangladesh_ssc_hsc_district_year_education_with_exam_dates.xlsx"
GED_FILE = ROOT / "data" / "bangladesh_ged_selected_data_2011_2025.xlsx"
SCHEMA_FILE = ROOT / "schema" / "bangladesh_conflict_education.schema.json"
OUT_FILE = ROOT / "output" / "bangladesh_conflict_education.json"

# Events whose district needed outside sources (see docs/district_mapping_notes.md).
# relid -> (confidence, note)
RESEARCHED = {
    "BNG-2013-2-X3374-6": ("medium", "Shibganj: Chapai Nawabganj clashes after Sayeedi verdict, Mar 2013"),
    "BNG-2013-2-X3374-11": ("medium-low", "Shibganj (Umarpur village): inferred, no report of this exact event found"),
    "BNG-2013-2-29-12": ("medium", "Shibganj Bazar shop arson, Chapai Nawabganj"),
    "BNG-2017-1-14718-12": ("high", "Militant hideout raid, Shibnagar, Shibganj, Chapai Nawabganj, Apr 2017"),
    "BNG-2015-3-1076-4": ("high", "Description names Bogra district"),
    "BNG-2017-1-14718-6": ("high", "Jamnagar village, Sherpur upazila, Bogra, 2 Mar 2017"),
    "BNG-2017-1-14718-13": ("high", "Bazrapur village, Moheshpur upazila, Jhenaidah, 7 May 2017"),
    "BNG-2013-2-29-9": ("medium", "Chupair village: matched to 27 Nov 2013 Kaliganj (Gazipur) clash"),
    "BNG-2013-2-X3374-20": ("medium", "Kaliganj: matched to Dec 2013 Jamaat killing in Kaliganj, Satkhira"),
    "BNG-2013-2-29-0": ("low", "Gopalpur: assumed Tangail; no report found, Gopalpur also exists in Natore"),
    "BNG-2024-2-17997-17": ("high", "Fish trader shot at Shimrail, Siddhirganj, Narayanganj, 21 Jul 2024"),
    "BNG-2024-2-17997-25": ("medium", "Description names Joypurhat"),
}
UNLOCATED_NOTES = {
    "BNG-2024-2-17997-19": "Place of killing unknown; case was filed in Joypurhat",
}

EXAM_FIELDS = ["institutions", "appeared", "passed", "failed", "pass_rate_pct",
               "a_plus", "a_plus_rate_pct", "examinees_per_1k_pop"]


def read_rows(path):
    ws = openpyxl.load_workbook(path, read_only=True).active
    rows = ws.iter_rows(values_only=True)
    header = next(rows)
    return [dict(zip(header, r)) for r in rows if any(v is not None for v in r)]


def exam_result(row, prefix):
    cols = ["Institutions", "Total Appeared", "Total Passed", "Total Failed", "Pass Rate (%)",
            "Total A+", "A+ Rate (%)", "Examinees Per 1k Pop"]
    return {field: row[f"{prefix} {col}"] for field, col in zip(EXAM_FIELDS, cols)}


def exam_session(value):
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError):
        return {"status": "not_held", "start_date": None,
                "note": f"{value}; results for this year are automatic passes, not exam outcomes"}
    return {"status": "held", "start_date": value}


def event(row):
    relid = row["relid"]
    if row["district"] == "Unknown":
        mapping = {"method": "unlocated", "confidence": "none"}
        if relid in UNLOCATED_NOTES:
            mapping["note"] = UNLOCATED_NOTES[relid]
    elif relid in RESEARCHED:
        confidence, note = RESEARCHED[relid]
        mapping = {"method": "researched", "confidence": confidence, "note": note}
    else:
        mapping = {"method": "direct", "confidence": "high"}
    return {
        "relid": relid,
        "source_article": row["source_article"],
        "where_coordinates": row["where_coordinates"],
        "where_description": row["where_description"] or None,
        "best": row["best"],
        "district_mapping": mapping,
    }


def build():
    edu = read_rows(EDU_FILE)
    ged = read_rows(GED_FILE)

    events_by_key = defaultdict(list)
    unlocated = []
    for row in ged:
        if row["district"] == "Unknown":
            unlocated.append({**event(row), "year": row["year"]})
        else:
            events_by_key[(row["district"], row["year"])].append(event(row))

    calendar = {}
    districts = {}
    for row in edu:
        year, name = row["Year"], row["District Name"]
        calendar.setdefault(year, {
            "year": year,
            "ssc": exam_session(row["SSC Exam Start Date"]),
            "hsc": exam_session(row["HSC Exam Start Date"]),
        })
        district = districts.setdefault(name, {
            "name": name,
            "division": row["Division"],
            "census": {
                "2011": {"population": row["Census 2011 Population"],
                         "male": row["Census 2011 Male"],
                         "female": row["Census 2011 Female"]},
                "2022": {"population": row["Census 2022 Population"]},
            },
            "exam_boards": {"ssc": row["SSC Education Board"], "hsc": row["HSC Education Board"]},
            "years": [],
        })
        events = events_by_key.pop((name, year), [])
        district["years"].append({
            "year": year,
            "estimated_population": row["Estimated Population"],
            "ssc": exam_result(row, "SSC"),
            "hsc": exam_result(row, "HSC"),
            "conflict": {
                "event_count": len(events),
                "deaths_best": sum(e["best"] for e in events),
                "events": events,
            },
        })

    if events_by_key:
        sys.exit(f"Events with no matching district-year in the education file: {sorted(events_by_key)}")

    for d in districts.values():
        d["years"].sort(key=lambda y: y["year"])
    years = sorted(calendar)

    return {
        "metadata": {
            "generated_on": date.today().isoformat(),
            "year_range": {"start": years[0], "end": years[-1]},
            "sources": [
                {"file": EDU_FILE.name,
                 "description": "District-year SSC/HSC results, population and exam start dates"},
                {"file": GED_FILE.name,
                 "description": "UCDP Georeferenced Event Dataset (GED) events in Bangladesh, with added district column"},
            ],
            "notes": "Events are matched to districts by the GED file's district column and by calendar year. "
                     "District assignment method is in each event's district_mapping; see docs/district_mapping_notes.md.",
        },
        "exam_calendar": [calendar[y] for y in years],
        "districts": sorted(districts.values(), key=lambda d: d["name"]),
        "unlocated_events": sorted(unlocated, key=lambda e: (e["year"], e["relid"])),
    }


def check(doc, n_ged_events):
    placed = 0
    for d in doc["districts"]:
        for y in d["years"]:
            c = y["conflict"]
            assert c["event_count"] == len(c["events"]), (d["name"], y["year"])
            assert c["deaths_best"] == sum(e["best"] for e in c["events"]), (d["name"], y["year"])
            placed += c["event_count"]
    assert placed + len(doc["unlocated_events"]) == n_ged_events, "events lost or duplicated"

    try:
        import jsonschema
    except ImportError:
        print("jsonschema not installed; skipped schema validation")
        return
    schema = json.loads(SCHEMA_FILE.read_text())
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = list(validator.iter_errors(doc))
    for e in errors[:10]:
        print(f"{e.json_path}: {e.message}")
    if errors:
        sys.exit(f"{len(errors)} schema errors")
    print("valid against schema")


if __name__ == "__main__":
    doc = build()
    check(doc, len(read_rows(GED_FILE)))
    OUT_FILE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    placed = sum(y["conflict"]["event_count"] for d in doc["districts"] for y in d["years"])
    print(f"wrote {OUT_FILE.relative_to(ROOT)}: {len(doc['districts'])} districts, "
          f"{placed} located events, {len(doc['unlocated_events'])} unlocated")

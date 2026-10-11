# Event `time` column: population method

## Files

The original file, `data/bangladesh_ged_selected_data_2011_2025.xlsx`, is retained unchanged. The derived file is `data/bangladesh_ged_selected_data_2011_2025_with_time.xlsx`.

The derived workbook adds one text column, `time`, immediately after `year`. Every original row and original field is retained.

## Source and matching

Dates come from the official UCDP Georeferenced Event Dataset (GED), version 26.1, which covers events through 2025 and provides day-level dates or bounded date ranges [UCDP GED codebook (2026/03), pp. 3–5].

Rows are joined by exact `relid`. Before a date is accepted, the script also requires the UCDP row's `year` and `best` death estimate to equal the corresponding values in the project workbook. All 227 project rows matched one and only one UCDP GED 26.1 row, and all 227 passed both validation checks [local validation (2026/10), `scripts/add_time_column.py` output].

The `source_article` publication date is not used as the event date. Publication can occur after an event, while UCDP supplies `date_start`, `date_end`, and `date_prec` specifically to represent temporal uncertainty [UCDP GED codebook (2026/03), Sections 3 and 5.6].

## Encoding

The `time` column is text in one of two ISO-style forms:

- `YYYY-MM-DD` when UCDP records one exact event day.
- `YYYY-MM-DD/YYYY-MM-DD` when UCDP records a closed interval from the earliest possible date through the latest possible date.

This update contains 204 single-day values and 23 intervals. Of the intervals, 12 have UCDP temporal precision 2 (a 2–6 day range) and 11 have temporal precision 4 (an 8–30 day range or month-level precision) [local validation (2026/10), UCDP GED 26.1 comparison; UCDP GED codebook (2026/03), Section 5.6].

No time of day is inferred. UCDP defines its normal temporal unit as a local calendar day, and its API/date fields use ISO `YYYY-MM-DD` values [UCDP GED codebook (2026/03), Sections 2, 3.1, and 5.6].

## Using `time` with the 50-day exam spans

If an exam starts on date `S`, its inclusive 50-calendar-day window ends on `S + 49 days`.

For a single-day event, set `event_start = event_end = time`. For an interval, split `time` at `/`. Treat an event as overlapping an exam window when:

```text
event_start <= exam_end AND event_end >= exam_start
```

Do not replace an interval with its first day or midpoint. When the interval only partly overlaps the exam period, classify it separately as an uncertain overlap or perform lower- and upper-bound sensitivity analyses.

## Reproduction

Download the official UCDP GED 26.1 CSV, extract `GEDEvent_v26_1.csv`, and run:

```bash
python3 scripts/add_time_column.py --ged-csv /path/to/GEDEvent_v26_1.csv
```

The script refuses to write dates if a `relid` is missing or duplicated, or if `year` or `best` differs. It writes only the derived workbook and never saves over the original.

## Version limitation

The project's original UCDP release was not recorded. The dates therefore come from GED 26.1, a newer identifiable release. UCDP notes that discrepancies can appear across releases because events may be revised [UCDP GED codebook (2026/03), Section 3]. Analyses should cite GED 26.1 for the added temporal fields while also retaining the project's provenance note for its original selected extract.

## Sources

[UCDP GED 26.1 data, 2026/03] Uppsala Conflict Data Program. "UCDP Georeferenced Event Dataset, version 26.1." Uppsala University. https://ucdp.uu.se/downloads/ged/ged261-csv.zip

[UCDP GED codebook, 2026/03] Stina Högbladh. "UCDP GED Codebook version 26.1." Uppsala Conflict Data Program, Uppsala University. https://ucdp.uu.se/downloads/ged/ged261.pdf

[local validation, 2026/10] Project validation performed by `scripts/add_time_column.py` against the original workbook and UCDP GED 26.1 CSV. `scripts/add_time_column.py`

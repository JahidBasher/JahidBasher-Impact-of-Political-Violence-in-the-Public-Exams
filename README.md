# Bangladesh Exams and Conflict

District-level SSC and HSC exam results for Bangladesh (64 districts, 2011–2025), linked to organized-violence events from the Uppsala Conflict Data Program (UCDP). Each conflict event is assigned to a district, so results and events can be compared by district and year.

## View the report

Open [`output/bangladesh_exams_conflict_report.html`](output/bangladesh_exams_conflict_report.html) in any web browser. It is a single file with everything embedded and works without an internet connection.

The report shows the education results table with one extra column, **Conflict summary**. Click any row with events to see them: place, deaths, type of violence and news source. Filters for year, division and district are at the top, and every column can be sorted.

## What's in the repository

```
data/
  bangladesh_ssc_hsc_district_year_education_with_exam_dates.xlsx   education results (input)
  bangladesh_ged_selected_data_2011_2025.xlsx                        conflict events with district column (input)
  bangladesh_ged_selected_data_2011_2025_with_time.xlsx              dated copy; original input retained unchanged
output/
  bangladesh_conflict_education.json      both datasets combined, nested district → year → events
  bangladesh_exams_conflict_report.html   offline interactive report
  political_violence_exam_results_twfe.html   executed analysis notebook as a browser-readable report
notebooks/
  political_violence_exam_results_twfe.ipynb  documented SSC/HSC two-way fixed-effects analysis
schema/
  bangladesh_conflict_education.schema.json   JSON Schema for the combined file
scripts/
  excel_to_json.py    builds the JSON from the two Excel files and validates it
  build_report.py     builds the HTML report from the JSON and the education file
  build_analysis_notebook.py   builds, executes and exports the documented analysis notebook
report/
  template.html       report layout, styles and behaviour
  fonts/              embedded fonts and their licences (SIL Open Font License 1.1)
docs/
  district_mapping_notes.md   how each event was assigned to a district, with confidence levels
  time_column_method.md       how the derived event time column was populated and validated
```

## Data

### Education results

`data/bangladesh_ssc_hsc_district_year_education_with_exam_dates.xlsx` has one row per district per year (64 × 15 = 960 rows), with population (2011 and 2022 census, yearly estimate), the education board, and for both SSC and HSC: institutions, examinees, passes, failures, pass rate, A+ count and rate, examinees per 1,000 people, and the exam start date.

**Source:** _to be added by the maintainer._

HSC 2020 was not held because of COVID-19. That year's HSC figures are automatic passes (100% pass rate), not exam results, and should be left out of pass-rate analysis.

### Conflict events

`data/bangladesh_ged_selected_data_2011_2025.xlsx` has 227 events from the UCDP Georeferenced Event Dataset (GED). Each event is an incident of organized violence; `best` is UCDP's best estimate of deaths. The `district` column was added to this project; every other column is UCDP's.

**Source:** UCDP, https://ucdp.uu.se. The UCDP release used was not recorded; add it here.

Things to know when using the events:

- **District assignment.** 202 events were placed from the place name, 12 needed checking against news reports, and 13 are coded only as "Bangladesh" and have district `Unknown`. Each event's method and confidence are recorded. See [`docs/district_mapping_notes.md`](docs/district_mapping_notes.md).
- **Type of violence.** The digit after the year in `relid` is UCDP's type: 1 state vs armed group, 2 clashes between non-state groups, 3 one-sided violence against civilians.
- **ID prefixes.** 51 events have `MYA`, `AFG` or `IND` IDs although they happened in Bangladesh: Rohingya camp killings and Myanmar border spillover, Islamic State attacks, and Indian border-guard shootings. The notes file explains each group.
- **Matching is by calendar year.** An event late in a year is linked to that year's exams even if the exams came first. HSC started in December in 2021 and November in 2022, and SSC started in September in 2022. Event dates (`date_start`, `date_end`) are not in this extract. The JSON schema already accepts them if the data is downloaded again with dates.

### Combined JSON

`output/bangladesh_conflict_education.json` nests the data as districts → years → events. District facts that never change (division, census figures, exam boards) are stored once per district, and national exam dates once per year. Each district-year has `conflict.event_count`, `conflict.deaths_best` and the list of `events` (empty when there were none). Unlocated events are in `unlocated_events`. The full structure is defined in [`schema/bangladesh_conflict_education.schema.json`](schema/bangladesh_conflict_education.schema.json).

## Rebuilding the outputs

Run this after changing either Excel file or the report template. It needs Python 3.9 or later.

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python scripts/excel_to_json.py      # writes output/bangladesh_conflict_education.json and validates it
python scripts/build_report.py       # writes output/bangladesh_exams_conflict_report.html
```

`excel_to_json.py` stops with an error if an event's district and year don't match a row in the education file, if counts don't add up, or if the output doesn't match the schema.

If you change the district of one of the 12 researched events, update the `RESEARCHED` list near the top of `scripts/excel_to_json.py` to match.

## Citing

If you use the conflict data, cite UCDP as its codebook asks:

> Sundberg, Ralph, and Erik Melander. 2013. "Introducing the UCDP Georeferenced Event Dataset." *Journal of Peace Research* 50(4): 523–532.

Also give the UCDP dataset version, once it has been recorded above.

## Licences

- **This project's code and documentation:** _licence to be chosen by the maintainer._
- **UCDP data:** see the terms of use on the UCDP website.
- **Fonts** (Public Sans, Source Serif 4): SIL Open Font License 1.1, in [`report/fonts/`](report/fonts/).

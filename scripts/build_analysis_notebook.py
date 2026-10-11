"""Build, execute, and export the beginner-friendly TWFE analysis notebook."""

from pathlib import Path
from textwrap import dedent

import nbformat as nbf
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor


ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_DIR = ROOT / "notebooks"
OUTPUT_DIR = ROOT / "output"
NOTEBOOK_PATH = NOTEBOOK_DIR / "political_violence_exam_results_twfe.ipynb"
HTML_PATH = OUTPUT_DIR / "political_violence_exam_results_twfe.html"


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


cells = [
    md(
        r"""
        # Political violence during SSC and HSC examinations

        ## A district-level analysis of Bangladesh, 2011–2025

        **Audience.** This notebook is written for sociology students with little prior experience in Python, mathematics, or regression analysis. Each code cell is preceded by a plain-language explanation. The central question is whether political violence during a 50-day examination period is *associated with* district exam results. The design does not by itself prove causation.

        ## Key terms

        | Term | Description |
        |---|---|
        | Association | A pattern in which two measured quantities vary together. Association alone does not establish that one caused the other. |
        | Binary exposure | An exposure recorded with two values: 1 when the condition is present and 0 when it is absent. |
        | Causal effect | A change in an outcome produced by a change in an exposure, holding every other relevant influence constant. This notebook does not claim to identify a causal effect. |
        | Confounder | A factor related to both the exposure and outcome that can distort their measured association. |
        | Confidence interval | A range showing the uncertainty around an estimated association. Wider intervals mean greater uncertainty. |
        | Conflict data | The workbook containing organized-violence events, locations, deaths, and UCDP event dates. |
        | District | The geographic unit observed repeatedly in the panel data. Bangladesh has 64 districts in this dataset. |
        | District fixed effect | A control for district characteristics that do not change over the study period, such as persistent geographic differences. |
        | Education data | The workbook containing district-year SSC and HSC participation and result measures. |
        | Exam window | The exam start date plus the following 49 days, giving 50 calendar days including the start date. |
        | Exposure | The political-violence measure used to compare district-years, such as whether an event occurred during an exam window. |
        | Fixed effect | A statistical control for a group, such as a district or year, that absorbs that group's average level. |
        | GED | Georeferenced Event Dataset, an event-level dataset maintained by UCDP. |
        | HSC | Higher Secondary Certificate examination. |
        | Natural logarithm | A mathematical transformation used here to reduce the influence of a few unusually large death counts. |
        | Outcome | The result being studied: pass rate or A+ rate. |
        | Panel data | Data that follow the same districts over multiple years. |
        | Percentage point | The direct difference between percentages; for example, 80% minus 78% is 2 percentage points. |
        | p-value | A model-based measure of how unusual an estimate would be if the true coefficient were zero. It is not the probability that a hypothesis is true. |
        | Political violence | Organized-violence events included in the selected UCDP GED extract used by this project. |
        | Regression model | A statistical method that summarizes how an outcome varies with an exposure and specified controls. |
        | Results | The estimated associations produced by the statistical models. |
        | Robustness check | A repeat analysis using a reasonable alternative decision to see whether the conclusion changes. |
        | SSC | Secondary School Certificate examination. |
        | Standard error | A measure of uncertainty around an estimated coefficient. |
        | Statistical power | The ability of an analysis to detect a genuine association; sparse exposure generally reduces it. |
        | Spillover | A situation in which violence in one district also affects outcomes in another district. |
        | Temporal uncertainty | Uncertainty about the exact day of an event, represented here by a bounded date interval. |
        | Treated district-year | A district-year with at least one qualifying violence event during the relevant exam window. |
        | Two-way | The use of two groups of fixed effects—in this notebook, districts and years. |
        | TWFE model | A two-way fixed-effects model containing district fixed effects and year fixed effects. |
        | UCDP | Uppsala Conflict Data Program, the organization that maintains the conflict-event source data. |
        | Year | The calendar year attached to an exam result and violence event. |
        | Year fixed effect | A control for national changes in a year that affect every district, such as changes in examination difficulty. |
        """
    ),
    md(
        """
        ## Table of contents

        1. [Executive summary](#Executive-summary)
        2. [Background](#Background)
        3. [Initial hypotheses](#Initial-hypotheses)
        4. [Analysis proposal](#Analysis-proposal)
        5. [Methodology](#Methodology)
        6. [Load and validate the data](#Load-and-validate-the-data)
        7. [Construct the exam-window measures](#Construct-the-exam-window-measures)
        8. [Descriptive analysis](#Descriptive-analysis)
        9. [Two-way fixed-effects analysis](#Two-way-fixed-effects-analysis)
        10. [Robustness checks](#Robustness-checks)
        11. [Results and findings](#Results-and-findings)
        12. [Limitations and responsible interpretation](#Limitations-and-responsible-interpretation)
        13. [Reproduction](#Reproduction)
        14. [Sources](#Sources)
        """
    ),
    md(
        """
        ## Executive summary

        This analysis is statistically possible after adding UCDP event dates, but the relevant violence exposure is uncommon. Only **24 SSC district-years** and **32 HSC district-years** have at least one definitely in-window, located event. HSC exposure is especially concentrated in 2024.

        The primary TWFE estimates show almost no association between an in-window event and either SSC or HSC pass rates. The SSC A+ estimate is negative in the baseline model, while the HSC A+ estimate is positive but uncertain. These secondary findings change across reasonable specifications, so they should not be treated as stable causal effects.

        The defensible conclusion is narrow: **the available data do not show a robust relationship between in-window political violence and pass rates.** Sparse treatment, concentration in a few years and districts, possible time-varying confounding, and spillovers limit causal interpretation.
        """
    ),
    md(
        """
        ## Background

        The project links district-year SSC and HSC results for 64 Bangladeshi districts to organized-violence events selected from the Uppsala Conflict Data Program's Georeferenced Event Dataset (UCDP GED) [project README (2026/10), Data]. The dated conflict workbook matches events to UCDP GED 26.1 by `relid`, with dates represented as exact days or bounded intervals [time method (2026/10), Source and matching]. UCDP defines an event as an incident of lethal organized violence at a location and date, while acknowledging that some dates are known only within a range [UCDP GED codebook (2026/03), Sections 2 and 5.6].

        ```mermaid
        graph TD
          A[Education data] --> C[Panel data]
          B[Conflict data] --> D[Exam window]
          D --> C
          C --> E[TWFE model]
          E --> F[Results]
        ```

        The diagram shows the analysis in one sentence: education outcomes and dated violence exposure are combined into district-year panel data, then a TWFE model estimates their association.
        """
    ),
    md(
        """
        ## Initial hypotheses

        **Primary null hypothesis (H0).** Experiencing political violence during an exam window has no association with the district pass rate after district and year fixed effects are included.

        **Primary research hypothesis (H1).** Experiencing political violence during an exam window is associated with a lower district pass rate.

        **Secondary hypothesis (H2).** Greater violence intensity—measured by event count or deaths—is associated with a lower A+ rate.

        These hypotheses specify what will be tested before looking at model results. A result that differs from H1 or H2 is still informative; it should not be adjusted to fit the expectation.
        """
    ),
    md(
        """
        ## Analysis proposal

        1. Validate that the education panel contains one row per district-year and that all conflict events have usable `time` values.
        2. Define each exam window as its start date through start date plus 49 days.
        3. Construct a primary binary exposure: at least one located event whose full possible date interval falls inside the exam window.
        4. Describe how exposure varies by exam, year, and district before fitting a regression.
        5. Estimate separate SSC and HSC TWFE models for pass rate and A+ rate.
        6. Repeat the models with event counts, deaths, possible overlaps, alternative fixed effects, and influential observations removed.
        7. Interpret effect size, uncertainty, consistency, limitations, and practical importance in plain language.
        """
    ),
    md(
        r"""
        ## Methodology

        ### Main comparison

        The main model compares a district with itself across years while also removing the national average for each year. Conceptually, it asks:

        *When a district has violence during an exam window, is its result unusually high or low relative to both its own typical result and the national pattern that year?*

        The model is:

        $$
        Result_{d,t} = \beta Violence_{d,t} + District_d + Year_t + Error_{d,t}
        $$

        - $d$ identifies a district.
        - $t$ identifies a year.
        - $\beta$ is the estimated association reported in percentage points.
        - District fixed effects remove stable differences between districts.
        - Year fixed effects remove national changes shared by all districts.

        Standard errors are clustered by district because observations for the same district may remain related across years.

        ### Exam timing

        A 50-day inclusive window ends 49 days after its start. An exact event is in-window when its date falls between those endpoints. A ranged event is **definitely in-window** only when its full interval is inside the exam window. It is **possibly in-window** when any part overlaps. This preserves UCDP's temporal uncertainty instead of assigning an invented day [UCDP GED codebook (2026/03), Sections 3 and 5.6].

        ### Important exclusion

        HSC 2020 is excluded because the examination was not held normally and the recorded 100% pass outcomes were automatic rather than conventional examination results [project README (2026/10), Education results].

        ### Interpretation rule

        The coefficient is treated as an adjusted association, not a causal effect. TWFE cannot remove unmeasured district conditions that change over time, reverse causality, or violence spillovers into neighboring districts.
        """
    ),
    md(
        """
        ## Load and validate the data

        The next cell imports the analysis libraries and locates the project whether the notebook is run from the repository root or from the `notebooks` directory. `pandas` manages tables, `numpy` performs numerical calculations, and `matplotlib` draws charts.
        """
    ),
    code(
        """
        from pathlib import Path
        from datetime import timedelta
        from math import erfc, sqrt
        import platform
        import warnings

        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt
        from IPython.display import display

        warnings.filterwarnings("ignore", category=FutureWarning)
        plt.style.use("seaborn-v0_8-whitegrid")
        plt.rcParams.update({"figure.figsize": (10, 5.5), "font.size": 11})

        ROOT = Path.cwd()
        if not (ROOT / "data").exists():
            ROOT = ROOT.parent

        EDUCATION_FILE = ROOT / "data" / "bangladesh_ssc_hsc_district_year_education_with_exam_dates.xlsx"
        CONFLICT_FILE = ROOT / "data" / "bangladesh_ged_selected_data_2011_2025_with_time.xlsx"

        print("Project root:", ROOT)
        print("Education workbook found:", EDUCATION_FILE.exists())
        print("Dated conflict workbook found:", CONFLICT_FILE.exists())
        """
    ),
    md(
        """
        The next cell reads the two workbooks and performs checks that would stop the notebook if rows were duplicated, districts were missing, or dates were unusable. Stopping is safer than silently analyzing malformed data.
        """
    ),
    code(
        """
        education = pd.read_excel(EDUCATION_FILE)
        conflict = pd.read_excel(CONFLICT_FILE, dtype={"time": "string"})

        # Core structure checks
        assert len(education) == 960, "Expected 960 education rows (64 districts × 15 years)."
        assert education[["District Name", "Year"]].duplicated().sum() == 0
        assert education["District Name"].nunique() == 64
        assert education["Year"].nunique() == 15
        assert len(conflict) == 227
        assert conflict["relid"].duplicated().sum() == 0
        assert conflict["time"].notna().all()

        # Split an exact date or a closed date interval into start and end.
        time_parts = conflict["time"].str.split("/", n=1, expand=True)
        conflict["event_start"] = pd.to_datetime(time_parts[0], errors="raise")
        conflict["event_end"] = pd.to_datetime(time_parts[1].fillna(time_parts[0]), errors="raise")
        assert (conflict["event_end"] >= conflict["event_start"]).all()
        assert (conflict["event_start"].dt.year == conflict["year"]).all()

        validation = pd.DataFrame({
            "Check": [
                "Education district-years", "Districts", "Years", "Conflict events",
                "Exact event dates", "Date ranges", "Unlocated conflict events"
            ],
            "Value": [
                len(education), education["District Name"].nunique(), education["Year"].nunique(),
                len(conflict), (conflict["event_start"] == conflict["event_end"]).sum(),
                (conflict["event_start"] != conflict["event_end"]).sum(),
                (conflict["district"] == "Unknown").sum()
            ]
        })
        display(validation)
        """
    ),
    md(
        """
        ## Construct the exam-window measures

        SSC and HSC results are converted into a common “long” format: each row represents one district, one year, and one exam. The code keeps the appropriate education board, pass rate, A+ rate, and exam start date together.
        """
    ),
    code(
        """
        panel_parts = []
        for exam in ["SSC", "HSC"]:
            part = education[[
                "District Name", "Year", f"{exam} Education Board",
                f"{exam} Pass Rate (%)", f"{exam} A+ Rate (%)",
                f"{exam} Total Appeared", f"{exam} Exam Start Date"
            ]].copy()
            part.columns = [
                "district", "year", "board", "pass_rate", "a_plus_rate",
                "appeared", "exam_start_raw"
            ]
            part["exam"] = exam
            part["exam_start"] = pd.to_datetime(part["exam_start_raw"], errors="coerce")
            part["exam_end"] = part["exam_start"] + pd.to_timedelta(49, unit="D")
            panel_parts.append(part)

        panel = pd.concat(panel_parts, ignore_index=True)
        panel["exam_held"] = panel["exam_start"].notna()

        # The calendar must be national: one start date per exam-year.
        calendar_check = (
            panel.groupby(["exam", "year"])["exam_start_raw"]
            .nunique(dropna=False)
            .max()
        )
        assert calendar_check == 1

        # HSC 2020 has no conventional exam outcome, so it is excluded from modeling.
        model_panel = panel.loc[panel["exam_held"]].copy()
        assert not ((model_panel["exam"] == "HSC") & (model_panel["year"] == 2020)).any()

        display(
            model_panel.groupby("exam").agg(
                observations=("district", "size"),
                districts=("district", "nunique"),
                years=("year", "nunique")
            )
        )
        """
    ),
    md(
        """
        Each located conflict event is now compared with the relevant SSC and HSC windows for its year. Events whose district is `Unknown` are summarized but cannot be assigned to a district-year exposure.
        """
    ),
    code(
        """
        located_conflict = conflict.loc[conflict["district"] != "Unknown"].copy()
        event_exam_parts = []

        for exam in ["SSC", "HSC"]:
            exam_calendar = (
                panel.loc[panel["exam"] == exam, ["year", "exam_start", "exam_end"]]
                .drop_duplicates("year")
            )
            part = located_conflict.merge(exam_calendar, on="year", how="left")
            part["exam"] = exam
            part["possible_overlap"] = (
                (part["event_start"] <= part["exam_end"]) &
                (part["event_end"] >= part["exam_start"])
            )
            part["definite_overlap"] = (
                (part["event_start"] >= part["exam_start"]) &
                (part["event_end"] <= part["exam_end"])
            )
            event_exam_parts.append(part)

        event_exam = pd.concat(event_exam_parts, ignore_index=True)

        def aggregate_exposure(flag, prefix):
            selected = event_exam.loc[event_exam[flag]].copy()
            return (
                selected.groupby(["district", "year", "exam"], as_index=False)
                .agg(**{
                    f"{prefix}_event_count": ("relid", "size"),
                    f"{prefix}_deaths": ("best", "sum")
                })
            )

        definite = aggregate_exposure("definite_overlap", "definite")
        possible = aggregate_exposure("possible_overlap", "possible")
        model_panel = model_panel.merge(definite, on=["district", "year", "exam"], how="left")
        model_panel = model_panel.merge(possible, on=["district", "year", "exam"], how="left")

        exposure_columns = [
            "definite_event_count", "definite_deaths",
            "possible_event_count", "possible_deaths"
        ]
        model_panel[exposure_columns] = model_panel[exposure_columns].fillna(0)
        model_panel["definite_any"] = (model_panel["definite_event_count"] > 0).astype(int)
        model_panel["possible_any"] = (model_panel["possible_event_count"] > 0).astype(int)
        model_panel["definite_log_deaths"] = np.log1p(model_panel["definite_deaths"])

        window_summary = []
        for exam in ["SSC", "HSC"]:
            events = event_exam.loc[
                (event_exam["exam"] == exam) & event_exam["definite_overlap"]
            ]
            cells = model_panel.loc[
                (model_panel["exam"] == exam) & (model_panel["definite_any"] == 1)
            ]
            window_summary.append({
                "Exam": exam,
                "Located events definitely in window": len(events),
                "Deaths (best estimate)": int(events["best"].sum()),
                "Treated district-years": len(cells),
                "Treated districts": cells["district"].nunique(),
                "Usable district-years": (model_panel["exam"] == exam).sum()
            })

        window_summary = pd.DataFrame(window_summary)
        display(window_summary)
        """
    ),
    md(
        """
        **Reading the table.** “Located events” excludes events that cannot be assigned below the national level. “Treated district-years” counts district-years with at least one qualifying event. This is the effective treatment variation available to the fixed-effects models.
        """
    ),
    md(
        """
        ## Descriptive analysis

        Descriptive charts show where the identifying information comes from. They should be examined before regression results because a coefficient can be technically estimable even when exposure is highly concentrated.
        """
    ),
    code(
        """
        # Average pass rates by year and exam.
        pass_trend = (
            model_panel.groupby(["year", "exam"], as_index=False)["pass_rate"].mean()
        )

        fig, ax = plt.subplots()
        colors = {"SSC": "#1769AA", "HSC": "#D97706"}
        for exam in ["SSC", "HSC"]:
            d = pass_trend.loc[pass_trend["exam"] == exam]
            ax.plot(d["year"], d["pass_rate"], marker="o", linewidth=2, label=exam,
                    color=colors[exam])
        ax.set(title="Average district pass rate by year",
               xlabel="Year", ylabel="Average pass rate (%)")
        ax.legend(title="Exam")
        ax.set_xticks(range(2011, 2026, 2))
        plt.show()
        """
    ),
    code(
        """
        # Number of districts with at least one definitely in-window event.
        treated_by_year = (
            model_panel.groupby(["year", "exam"], as_index=False)["definite_any"].sum()
        )
        pivot = treated_by_year.pivot(index="year", columns="exam", values="definite_any").fillna(0)

        ax = pivot.plot(kind="bar", color=[colors["HSC"], colors["SSC"]], width=0.82)
        ax.set(title="Districts exposed to violence during each exam window",
               xlabel="Year", ylabel="Number of districts")
        ax.legend(title="Exam")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

        concentration = (
            event_exam.loc[event_exam["definite_overlap"]]
            .groupby(["exam", "year"], as_index=False)
            .agg(events=("relid", "size"), deaths=("best", "sum"))
            .sort_values(["exam", "events"], ascending=[True, False])
        )
        display(concentration)
        """
    ),
    md(
        """
        The charts show two relevant patterns. Results change substantially across years, supporting the use of year fixed effects. Violence exposure is sparse and uneven; in particular, HSC-window events are concentrated in 2024. This makes the HSC estimate highly dependent on comparisons made within that year.
        """
    ),
    md(
        """
        ## Two-way fixed-effects analysis

        The function below performs the regression. It creates indicator columns for districts and years, estimates the coefficient that best fits the data, and calculates district-clustered standard errors. The internal matrix operations are standard regression calculations; students do not need to reproduce them by hand.
        """
    ),
    code(
        """
        def fit_clustered_fe(data, outcome, exposure, board_year=False):
            # Estimate one TWFE model with district-clustered uncertainty.
            needed = ["district", "year", "board", outcome, exposure]
            work = data[needed].dropna().copy()

            # The first two columns are the intercept and the exposure of interest.
            pieces = [
                pd.Series(1.0, index=work.index, name="intercept"),
                work[exposure].astype(float).rename(exposure),
                pd.get_dummies(work["district"], prefix="district", drop_first=True, dtype=float)
            ]

            if board_year:
                # Board-by-year controls absorb examination-board shocks in each year.
                board_year_id = work["board"].astype(str) + " × " + work["year"].astype(str)
                pieces.append(pd.get_dummies(board_year_id, prefix="board_year",
                                             drop_first=True, dtype=float))
            else:
                pieces.append(pd.get_dummies(work["year"], prefix="year",
                                             drop_first=True, dtype=float))

            X_frame = pd.concat(pieces, axis=1)
            X = X_frame.to_numpy(dtype=float)
            y = work[outcome].to_numpy(dtype=float)

            beta = np.linalg.lstsq(X, y, rcond=None)[0]
            residual = y - X @ beta
            bread = np.linalg.pinv(X.T @ X)

            # Cluster scores allow observations from one district to be correlated.
            meat = np.zeros((X.shape[1], X.shape[1]))
            for district in work["district"].unique():
                mask = (work["district"] == district).to_numpy()
                score = X[mask].T @ residual[mask]
                meat += np.outer(score, score)

            n = len(work)
            clusters = work["district"].nunique()
            rank = np.linalg.matrix_rank(X)
            correction = (clusters / (clusters - 1)) * ((n - 1) / (n - rank))
            covariance = correction * bread @ meat @ bread
            standard_errors = np.sqrt(np.maximum(np.diag(covariance), 0))

            coefficient = beta[1]
            standard_error = standard_errors[1]
            # With 64 district clusters, a normal approximation is used for
            # the 95% interval and the two-sided p-value.
            critical = 1.96
            z_value = coefficient / standard_error
            p_value = erfc(abs(z_value) / sqrt(2))

            return {
                "estimate_pp": coefficient,
                "clustered_se": standard_error,
                "ci_low": coefficient - critical * standard_error,
                "ci_high": coefficient + critical * standard_error,
                "p_value": p_value,
                "observations": n,
                "district_clusters": clusters,
                "treated_cells": int((work[exposure] > 0).sum())
            }

        print("Regression function defined successfully.")
        """
    ),
    md(
        """
        ### Main models

        The primary exposure is `definite_any`: one when at least one event's full possible date interval lies inside the exam window, and zero otherwise. Separate models are fitted for SSC and HSC pass rates and A+ rates.
        """
    ),
    code(
        """
        main_rows = []
        outcome_labels = {"pass_rate": "Pass rate", "a_plus_rate": "A+ rate"}

        for exam in ["SSC", "HSC"]:
            exam_data = model_panel.loc[model_panel["exam"] == exam]
            for outcome in ["pass_rate", "a_plus_rate"]:
                result = fit_clustered_fe(exam_data, outcome, "definite_any")
                main_rows.append({
                    "Exam": exam,
                    "Outcome": outcome_labels[outcome],
                    **result
                })

        main_results = pd.DataFrame(main_rows)
        main_display = main_results.rename(columns={
            "estimate_pp": "Estimate (percentage points)",
            "clustered_se": "Clustered SE",
            "ci_low": "95% CI lower",
            "ci_high": "95% CI upper",
            "p_value": "p-value",
            "observations": "Observations",
            "treated_cells": "Treated district-years"
        })
        main_display["p-value"] = main_display["p-value"].map(
            lambda value: "<0.001" if value < 0.001 else f"{value:.3f}"
        )
        display(main_display[[
            "Exam", "Outcome", "Estimate (percentage points)", "Clustered SE",
            "95% CI lower", "95% CI upper", "p-value", "Observations",
            "Treated district-years"
        ]].round(3))
        """
    ),
    md(
        """
        **How to read a row.** The estimate is the adjusted difference in percentage points associated with having at least one in-window event. If the confidence interval crosses zero, the data are compatible with both a small negative association and a small positive association. The interval describes uncertainty under the model; it does not test every possible source of bias.
        """
    ),
    code(
        """
        # A coefficient plot makes direction, size, and uncertainty easier to compare.
        plot_data = main_results.copy()
        plot_data["label"] = plot_data["Exam"] + " — " + plot_data["Outcome"]
        plot_data = plot_data.iloc[::-1].reset_index(drop=True)

        fig, ax = plt.subplots(figsize=(9, 5))
        y_pos = np.arange(len(plot_data))
        estimates = plot_data["estimate_pp"].to_numpy()
        lower = estimates - plot_data["ci_low"].to_numpy()
        upper = plot_data["ci_high"].to_numpy() - estimates
        ax.errorbar(estimates, y_pos, xerr=[lower, upper], fmt="o", color="#1769AA",
                    ecolor="#4B5563", capsize=4, markersize=7)
        ax.axvline(0, color="black", linewidth=1)
        ax.set_yticks(y_pos, plot_data["label"])
        ax.set(title="Main TWFE estimates with 95% confidence intervals",
               xlabel="Estimated association (percentage points)", ylabel="")
        plt.tight_layout()
        plt.show()
        """
    ),
    md(
        """
        ### Alternative violence measures

        A binary exposure is easy to interpret but treats one event and many events alike. The next models use event count and the natural logarithm of one plus deaths. The logarithm reduces the influence of a few unusually deadly observations; adding one allows zero-death district-years to remain in the sample.
        """
    ),
    code(
        """
        intensity_rows = []
        exposure_labels = {
            "definite_any": "Any event",
            "definite_event_count": "Event count",
            "definite_log_deaths": "log(1 + deaths)"
        }

        for exam in ["SSC", "HSC"]:
            exam_data = model_panel.loc[model_panel["exam"] == exam]
            for outcome in ["pass_rate", "a_plus_rate"]:
                for exposure in exposure_labels:
                    result = fit_clustered_fe(exam_data, outcome, exposure)
                    intensity_rows.append({
                        "Exam": exam,
                        "Outcome": outcome_labels[outcome],
                        "Exposure": exposure_labels[exposure],
                        **result
                    })

        intensity_results = pd.DataFrame(intensity_rows)
        intensity_display = intensity_results[[
            "Exam", "Outcome", "Exposure", "estimate_pp", "clustered_se",
            "ci_low", "ci_high", "p_value"
        ]].rename(columns={
            "estimate_pp": "Estimate", "clustered_se": "Clustered SE",
            "ci_low": "95% CI lower", "ci_high": "95% CI upper",
            "p_value": "p-value"
        })
        intensity_display["p-value"] = intensity_display["p-value"].map(
            lambda value: "<0.001" if value < 0.001 else f"{value:.3f}"
        )
        display(
            intensity_display.round(3)
        )
        """
    ),
    md(
        """
        ## Robustness checks

        The same conclusion is more credible when it survives reasonable alternative decisions. These checks use five specifications:

        - **Baseline:** definite in-window exposure with district and year fixed effects.
        - **Possible overlap:** includes partially overlapping uncertain date ranges.
        - **Exclude 2024:** tests dependence on the year with the largest HSC concentration.
        - **Exclude Dhaka and Cox's Bazar:** tests dependence on two high-event districts.
        - **Board-by-year controls:** replaces national year effects with separate controls for each education board in each year.
        """
    ),
    code(
        """
        robustness_rows = []

        for exam in ["SSC", "HSC"]:
            base = model_panel.loc[model_panel["exam"] == exam].copy()
            for outcome in ["pass_rate", "a_plus_rate"]:
                specifications = [
                    ("Baseline", base, "definite_any", False),
                    ("Possible overlap", base, "possible_any", False),
                    ("Exclude 2024", base.loc[base["year"] != 2024], "definite_any", False),
                    ("Exclude Dhaka and Cox's Bazar",
                     base.loc[~base["district"].isin(["Dhaka", "Cox's Bazar"])],
                     "definite_any", False),
                    ("Board-by-year controls", base, "definite_any", True)
                ]

                for label, data, exposure, board_year in specifications:
                    result = fit_clustered_fe(data, outcome, exposure, board_year=board_year)
                    robustness_rows.append({
                        "Exam": exam,
                        "Outcome": outcome_labels[outcome],
                        "Specification": label,
                        **result
                    })

        robustness = pd.DataFrame(robustness_rows)
        robustness_display = robustness[[
            "Exam", "Outcome", "Specification", "estimate_pp", "clustered_se",
            "ci_low", "ci_high", "p_value", "treated_cells"
        ]].rename(columns={
            "estimate_pp": "Estimate", "clustered_se": "Clustered SE",
            "ci_low": "95% CI lower", "ci_high": "95% CI upper",
            "p_value": "p-value", "treated_cells": "Treated cells"
        })
        robustness_display["p-value"] = robustness_display["p-value"].map(
            lambda value: "<0.001" if value < 0.001 else f"{value:.3f}"
        )
        display(
            robustness_display.round(3)
        )
        """
    ),
    code(
        """
        # Visual comparison of robustness estimates.
        for exam in ["SSC", "HSC"]:
            subset = robustness.loc[robustness["Exam"] == exam].copy()
            subset["label"] = subset["Outcome"] + " — " + subset["Specification"]
            subset = subset.iloc[::-1].reset_index(drop=True)
            fig, ax = plt.subplots(figsize=(10, 7))
            y_pos = np.arange(len(subset))
            est = subset["estimate_pp"].to_numpy()
            ax.errorbar(
                est, y_pos,
                xerr=[est - subset["ci_low"].to_numpy(), subset["ci_high"].to_numpy() - est],
                fmt="o", color=colors[exam], ecolor="#6B7280", capsize=3
            )
            ax.axvline(0, color="black", linewidth=1)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(subset["label"].tolist())
            ax.set(title=f"{exam} robustness checks", xlabel="Estimated association (percentage points)", ylabel="")
            fig.subplots_adjust(left=0.39, right=0.97, top=0.92, bottom=0.12)
            plt.show()
        """
    ),
    md(
        """
        ## Results and findings

        ### Primary finding: pass rates

        The baseline SSC and HSC pass-rate coefficients are very close to zero, and their confidence intervals cross zero. Event-count and death-intensity alternatives do not reveal a stable pass-rate relationship. The data therefore do not support the hypothesis that in-window violence has a robust association with district pass rates.

        ### Secondary finding: A+ rates

        The baseline SSC A+ coefficient is negative, but its size changes when board-by-year controls or influential observations are considered. The HSC A+ coefficient is positive in several baseline intensity models, yet HSC exposure is dominated by 2024 and changes materially when 2024 is removed. These are specification-sensitive secondary results, not reliable causal findings.

        ### Substantive interpretation

        A coefficient should be judged by its size and stability, not only by whether a p-value is below a threshold. Here, the most consistent result is the absence of a meaningful pass-rate association. The A+ patterns are less stable and should motivate further data collection rather than a strong conclusion.

        ### Decision on the hypotheses

        - **H0 cannot be rejected consistently for pass rates.** The estimated pass-rate associations are near zero and uncertain.
        - **H1 is not supported by the pass-rate models.**
        - **H2 receives mixed and unstable support.** Some A+ intensity coefficients differ from zero, but their direction and magnitude are not robust across exams and specifications.
        """
    ),
    md(
        """
        ## Limitations and responsible interpretation

        1. **Sparse exposure.** Only a small fraction of district-years are treated, reducing statistical power and making estimates sensitive to individual events.
        2. **Concentration.** HSC-window violence is concentrated in 2024, while SSC exposure is concentrated partly in 2013. Year fixed effects do not eliminate within-year concentration.
        3. **Unlocated events.** National-level events with district `Unknown` cannot enter district models. Excluding them may understate exposure in affected districts.
        4. **Time-varying confounding.** Local political competition, strikes, school closures, infrastructure, economic shocks, or administrative responses may affect both violence and exam outcomes.
        5. **Spillovers.** Violence in one district can disrupt transport, news, fear, or schooling in neighboring districts, violating the assumption that one district's exposure does not affect another.
        6. **Outcome aggregation.** District averages can conceal unequal effects across schools, gender, class, rurality, and socioeconomic groups.
        7. **Source provenance.** The original education source and original UCDP release were not recorded in the project README. The added dates use identifiable UCDP GED 26.1 fields, but the selected extract may originate from an earlier release [project README (2026/10), Data; time method (2026/10), Version limitation].
        8. **No causal identification strategy.** TWFE improves comparison but does not create random exposure. The findings should be reported as adjusted associations.

        A stronger future study would document the education source, add school-level or upazila-level results, measure pre-exam disruption, include strike and school-closure data, and pre-register the exposure definition before model estimation.
        """
    ),
    md(
        """
        ## Reproduction

        Run the following commands from the project root:

        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements-notebook.txt
        jupyter execute notebooks/political_violence_exam_results_twfe.ipynb
        ```

        The notebook reads the source workbooks without modifying them. Package versions used for the executed copy are shown below.
        """
    ),
    code(
        """
        import matplotlib

        versions = pd.DataFrame({
            "Component": ["Python", "pandas", "numpy", "matplotlib"],
            "Version": [platform.python_version(), pd.__version__, np.__version__, matplotlib.__version__]
        })
        display(versions)
        """
    ),
    md(
        """
        ## Sources

        [project README, 2026/10] Project maintainers. “Bangladesh Exams and Conflict.” Local project documentation. [README](../README.md)

        [time method, 2026/10] Project maintainers. “Event `time` column: population method.” Local project documentation. [Method note](../docs/time_column_method.md)

        [UCDP GED 26.1 data, 2026/03] Uppsala Conflict Data Program. “UCDP Georeferenced Event Dataset, version 26.1.” Uppsala University. https://ucdp.uu.se/downloads/ged/ged261-csv.zip

        [UCDP GED codebook, 2026/03] Stina Högbladh. “UCDP GED Codebook version 26.1.” Uppsala Conflict Data Program, Uppsala University. https://ucdp.uu.se/downloads/ged/ged261.pdf
        """
    ),
]


notebook = nbf.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.12"},
    },
)

NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
nbf.write(notebook, NOTEBOOK_PATH)

executor = ExecutePreprocessor(timeout=180, kernel_name="python3")
executor.preprocess(notebook, {"metadata": {"path": str(ROOT)}})
nbf.write(notebook, NOTEBOOK_PATH)

exporter = HTMLExporter()
exporter.exclude_input_prompt = True
exporter.exclude_output_prompt = True
html, _ = exporter.from_notebook_node(notebook)
HTML_PATH.write_text(html, encoding="utf-8")

print(f"wrote {NOTEBOOK_PATH.relative_to(ROOT)}")
print(f"wrote {HTML_PATH.relative_to(ROOT)}")

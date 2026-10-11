# LaTeX report package

Main source:

- `political_violence_exam_results_report.tex`

Before submission, replace the five bracketed fields near the top of the `.tex`
file: student name, student ID, course, instructor, and submission date.

The `figures/` directory contains five PNG figures extracted directly from the
executed Jupyter notebook. Keep that directory beside the `.tex` file.

Compile from this directory with any full TeX Live or MacTeX installation:

```bash
pdflatex political_violence_exam_results_report.tex
pdflatex political_violence_exam_results_report.tex
```

The second run populates the table of contents and all cross-references. No
BibTeX step is required because the source list is included in the document.

This environment did not contain a LaTeX engine, so the source was checked but
could not be compiled locally. The report uses standard packages included in a
normal TeX Live or MacTeX installation.

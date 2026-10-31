# Singapore Jobs Explorer

A small Streamlit dashboard for career coaches and job seekers to explore Singapore job postings, compare salary bands, and spot roles worth investigating. The project follows the assignment's data workflow: load, clean, explore, and communicate.

The instructor-provided `data/SGJobData.csv` is included. The dashboard loads its first 50,000 rows by default, matching the assignment's recommended development sample; the sidebar also lets you switch to all rows. The included `data/demo_jobs.csv` is fictional demonstration data.

## Start the dashboard

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Use the sidebar to select the local course CSV, upload another copy, or select the fictional demo data. The dashboard accepts the assignment's column names, including `title`, `categories`, `employmentTypes`, `positionLevels`, `salary_minimum`, `salary_maximum`, `metadata_originalPostingDate`, `metadata_newPostingDate`, `numberOfVacancies`, and `minimumYearsExperience`.

## Project files

- `app.py` — interactive dashboard with overview, salary, role, and time views.
- `data_utils.py` — CSV loading, column checks, cleaning, and category parsing.
- `notebooks/analysis_walkthrough.md` — reproducible EDA steps for the course dataset.
- `data/SGJobData.csv` — instructor-provided job postings CSV.
- `data/demo_jobs.csv` — small fictional sample for a quick interface preview.
- `report.md` — written submission with findings from the supplied CSV.
- `presentation_script.md` — timed, five-person presentation script for a 10-minute team slot.

## Data handling notes

The app does not overwrite the uploaded file. It standardises column names, parses dates and numeric fields, expands the first category from the JSON-style `categories` field, and derives a midpoint salary only when both salary bounds are available. Missing salaries stay missing; they are not treated as zero. Charts exclude missing values where the metric requires a number. Filters and all charts use the same filtered rows.

For a million-row file, begin with the 50,000-row sample as the assignment recommends. The full-file option and Streamlit upload keep the selected data in memory, so use them only when the machine has enough memory.

## Course concepts used

- SQL/database lessons inform structured fields and data-dictionary checks.
- NumPy and Pandas lessons inform numeric summaries, type conversion, filtering, grouping, and date handling.
- EDA lessons inform data-quality checks and summary questions.
- Visualization lesson informs chart selection and readable labels.

## Before presenting

1. Check whether your analysis uses the first 50,000 rows or the full file, and say which in the presentation.
2. Review missingness and salary quality before interpreting salary comparisons.
3. Add your team's own challenge and learning to `report.md` and `presentation_script.md`.
4. Capture 2–4 screenshots from the dashboard for the report, or show the app live.
5. Rehearse the handoffs and keep the presentation to 10 minutes.


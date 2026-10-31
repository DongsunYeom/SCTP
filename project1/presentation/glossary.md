# Glossary — words you will hear in the talk

Read this before rehearsing. Every term here is one a non-technical speaker might need to explain.

| Term | Plain-language meaning | Example from our project |
|---|---|---|
| **Dataset** | One large table of information. | The job-postings file, with 1,048,585 rows. |
| **Row** | One record in a table. | One row = one job advert. |
| **Column** | One type of information in the table. | "Salary minimum" is one column. |
| **Cleaning / tidying** | Fixing or removing entries that are empty, wrong, or badly written, before analysis. | Removing 3,988 empty rows. |
| **Missing value** | An entry that is blank. | A salary field left empty. |
| **Sample** | A small slice of a big file, used for checking first. | The first 50,000 rows. |
| **Category** | The industry a job belongs to. | "Information Technology", "Customer Service". |
| **Posting** | One job advert published by an employer or recruiter. | 1,044,597 postings after cleaning. |
| **Vacancy** | One open seat. One posting can offer several. | 2,725,717 vacancies in total. |
| **Listed salary** | The pay range written in the advert. What is offered, not what is paid. | "S$2,800 – S$4,000 a month". |
| **Median** | The middle value. Half above, half below. | Median advertised salary of S$3,850 a month. |
| **Average (mean)** | All values added and divided by how many there are. Pulled up by very high values. | About S$824 above the median. |
| **Percentile / middle half** | A position in the ranking. "25th percentile" means 25% of values are below it. | The middle half runs from S$2,950 to S$5,500. |
| **Outlier** | A value far outside the normal range. Often an entry error. | A monthly salary of S$25 million in the raw file. |
| **Seniority / career level** | How senior the role is, from entry to management. | Entry, Junior, Mid, Senior, Management. |
| **Applications per vacancy** | Roughly how many people applied for each open seat. A measure of competition. | 0.15 for Personal Care / Beauty; 2.16 for Risk Management. |
| **Coverage** | The share of postings that have a value for something. | 99% of postings list a salary. |
| **Duplicate** | The same entry appearing twice. We checked for these and found none with a repeated job ID. | Zero repeated job IDs. |
| **Dashboard** | A web page with charts and filters that summarises data at a glance. | The Singapore Jobs Explorer app. |
| **Filter** | A control that narrows what the charts show. | Choosing one industry in the sidebar. |
| **Tab** | A labelled page inside the dashboard. | Overview, Salary, Posting trends, Data quality. |
| **Data collection change** | A change in how information was recorded over time, which makes older and newer numbers hard to compare. | Views and application counts before about May 2023 are not comparable. |
| **Limitation** | Something the data or method cannot tell us. | Adverts do not show who was hired. |

## Terms to avoid on stage (and what to say instead)

| Avoid | Say instead |
|---|---|
| "Schema", "field", "attribute" | "Column", or describe what it holds |
| "Null", "NaN" | "Blank", "empty", or "missing" |
| "Aggregate", "group by" | "Add up by category" or "count for each" |
| "Regression", "model", "predict" | "We did not predict hiring; we only described the adverts" |
| "Log scale" | "A scale where each step is ten times the one before" (only if you must mention it) |
| "ETL", "pipeline" | "The steps that cleaned the file" |

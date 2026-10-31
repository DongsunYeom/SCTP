# 10-minute slide outline — Singapore Jobs Explorer

| Slide | On-screen headline | Main evidence | Speaker | Time |
|---:|---|---|---|---:|
| 1 | Singapore Jobs Explorer | Project title and purpose | 1 | 0:00 |
| 2 | A career conversation needs a quick view of the market | Audience and project question | 1 | 0:15 |
| 3 | We checked the file before trusting its charts | 1,048,585 source rows; 3,988 removed; 1,044,597 retained | 2 | 1:30 |
| 4 | Advertised pay rises across seniority bands | Median salary by band; overall median and middle half | 3 | 3:00 |
| 5 | Posting volume and pay tell different stories | IT vs Admin / Secretarial | 3 | 4:00 |
| 6 | Applications per vacancy varies by category | Four category ratios | 3 | 4:40 |
| 7 | Seven views turn the file into an exploration tool | Dashboard tabs and filters | 4 | 5:00 |
| 8 | Start broad, then narrow the question | Five-step live walkthrough | 4 | 5:25 |
| 9 | The dashboard shows advert patterns, with limits | Hiring, causality and trend caveats | 5 | 7:50 |
| 10 | A starting point for a better career conversation | Next steps and close | 5 | 9:00 |

## Live demo cue

After slide 7, show the app. Prioritize Overview and its filters, Demand vs competition, and Career recommender. Mention the remaining tabs briefly. Keep the walkthrough under 2 minutes 25 seconds.

## Data notes

- The app loads `data/SGJobData.csv` when present; otherwise it loads fictional demo data. State which source is active.
- Full-file findings on slides 4–6 are from the cleaned course dataset / project analysis. Category membership overlaps, so category posting counts do not sum to the total number of postings.
- Trend interpretation starts in May 2023. The later drop is visible but unexplained.
- Applications per vacancy is total applications divided by total vacancies in the records; it is not a unique-applicant count.

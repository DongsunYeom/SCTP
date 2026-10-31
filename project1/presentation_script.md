# Singapore Jobs Explorer — 10-minute presentation script

**Audience:** Career coaches and job seekers in Singapore  
**Team:** 5 speakers  
**Core message:** Job adverts help us compare roles and listed pay; they do not tell us who was hired.

## Run of show

| Speaker | Time | Slides | Focus |
|---|---:|---:|---|
| 1 | 0:00–1:30 | 1–2 | Audience and project question |
| 2 | 1:30–3:00 | 3 | Source data and cleaning |
| 3 | 3:00–5:00 | 4–6 | Three findings |
| 4 | 5:00–7:50 | 7–8 | Dashboard and short live walkthrough |
| 5 | 7:50–10:00 | 9–10 | Limits, next steps, close |

## Speaker 1 — Why this project (1 min 30 sec)

“Good morning/afternoon. We are Group 7, and this is Singapore Jobs Explorer.

A career coach or job seeker may want to compare roles, advertised pay and how many applications there are for each vacancy. Finding that information one advert at a time takes time. We built a dashboard that brings these views together and lets users narrow them by industry, career level and employment type.

Our project question is: where are roles being advertised, what pay is listed, and how does competition vary?

The dashboard is a starting point for a career conversation. It describes adverts; it does not predict whether someone will get hired, and it cannot tell us who was hired. [Speaker 2] will explain the data we used.”

## Speaker 2 — Data and preparation (1 min 30 sec)

“We used a Singapore job-advert file with 1,048,585 rows. Each row represents one advert, with information such as its title, salary range, category and dates.

Before analysis, we removed 3,988 empty records that had no usable advert details. That left 1,044,597 postings. We treated a salary of zero as ‘not disclosed,’ rather than as a real salary. We also corrected records where the minimum and maximum were reversed, and excluded impossible pay values from salary summaries.

These steps matter because a chart is only useful when its inputs make sense. The salary figures we show are advertised amounts, not confirmed take-home pay. [Speaker 3] will share three patterns we found.”

## Speaker 3 — What the data shows (2 min)

“First, advertised pay rises across seniority bands. The median monthly salary ranges from S$2,675 for entry-level postings to S$6,500 for management postings. Across all postings, the median is S$3,850. The middle half of listed salaries falls between S$2,950 and S$5,500. We use the median because a small number of unusually high figures can pull an average upward.

Second, posting volume and pay tell different stories. Information Technology has 140,866 category postings, with a median listed salary of S$6,500. Admin and Secretarial has 117,854 postings, with a median of S$2,900. One advert can belong to more than one category, so category totals overlap.

Third, applications per vacancy varies. In our summary it is 0.15 for Personal Care and Beauty, 0.21 for Food and Beverage, 1.48 for Marketing and Public Relations, and 2.16 for Risk Management. This is total applications divided by total vacancies in the records. It is a rough indicator, not a count of unique job seekers.

Together, these patterns help someone decide which roles to explore further. They do not tell us which role is right for a particular person. [Speaker 4] will show how the dashboard supports that exploration.”

## Speaker 4 — Dashboard walkthrough (2 min 50 sec)

“The app has seven views: Overview, Salary, Trends, Demand versus competition, Skills, Career recommender and Data quality. The filters for category, career level and employment type update the results across the dashboard.

I’ll start with Overview. Here, we can see the posting count, category count, median listed salary and salary coverage, then compare common titles and categories. I’ll select a category to narrow the results.

The Salary view compares median advertised pay. Trends shows monthly posting counts. We begin at May 2023 because collection methods changed around that time. The later drop is visible, but we have not confirmed its cause, so we should not call it a market slowdown.

In Demand versus competition, each point represents a category. The horizontal direction shows applications per vacancy, and the vertical direction shows posting volume. This helps us choose categories to investigate. The Skills view looks for keywords in job titles; a salary association does not prove that learning a skill causes higher pay.

Finally, Career recommender ranks category-and-seniority tracks using weights for demand, pay, low competition and ease of entry. The user can change those priorities. It is a guide for exploration, not a hiring prediction. Data quality provides checks such as missing values.

This is how the app turns a large file into a few questions a coach and job seeker can explore together. [Speaker 5] will close with the limits and next steps.”

## Speaker 5 — Limits and close (2 min 10 sec)

“There are three limits to keep in mind.

First, these are adverts, not hiring outcomes. We do not know who was hired, how many people actually searched for each role, or whether the listed pay was ultimately offered.

Second, some records are incomplete or unreliable. We removed empty records and excluded impossible salary values from pay summaries. The dashboard keeps data-quality checks visible, but users should still treat the numbers as estimates from adverts.

Third, trends before May 2023 are not comparable because collection changed. Posting counts also fall later in the series, and we have not established why. We should describe that pattern without guessing at its cause.

With more time, we would investigate the later decline, review extreme salary values individually, and ask career coaches and job seekers to try the app and tell us what is confusing.

Singapore Jobs Explorer gives a first look at advertised roles, pay and competition. Use it to decide what to ask next, then confirm with current sources and people. It is a starting point for a better career conversation, not a replacement for one.

Thank you. We are happy to take questions.”

## Rehearsal notes

- Keep Speaker 4’s live walkthrough to the steps above; skip detailed exploration of every chart if time is short.
- Confirm the full course CSV is available before presenting. If it is missing, the app loads fictional demo data; say so clearly and do not quote the full-file findings as if they came from the demo.
- Have screenshots of Overview and Demand versus competition ready in case the live app cannot be shown.
- Keep the distinction clear: one row is a posting, a vacancy is an open seat, and category counts can overlap.

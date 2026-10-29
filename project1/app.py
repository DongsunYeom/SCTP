from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

import numpy as np

from data_utils import (
    TREND_CUTOFF,
    career_tracks,
    category_market,
    clean_jobs,
    fit_score,
    monthly_postings,
    quality_summary,
    read_jobs,
    skill_premiums,
)


ROOT = Path(__file__).parent
DEMO_FILE = ROOT / "data" / "demo_jobs.csv"
COURSE_FILE = ROOT / "data" / "SGJobData.csv"

st.set_page_config(page_title="Singapore Jobs Explorer", page_icon="📊", layout="wide")
st.title("Singapore Jobs Explorer")
st.caption("A practical view of role demand and salary ranges for career conversations.")

with st.sidebar:
    st.header("Choose data")
    upload = st.file_uploader("Upload the course jobs CSV", type=["csv"])
    if upload is None:
        choices = (["Course dataset", "Fictional demo data"] if COURSE_FILE.exists() else ["Fictional demo data"])
        data_choice = st.radio("Data source", choices)
        row_choice = st.radio("Course data size", ["First 50,000 rows (recommended)", "All rows"], disabled=data_choice != "Course dataset")
    else:
        data_choice = "Uploaded course data"
        row_choice = "All rows"
    st.caption("The demo data is fictional. The course CSV contains about 1 million rows; start with 50,000 for a faster session.")

if upload is not None:
    raw = read_jobs(upload)
    data_label = "Uploaded course data"
elif data_choice == "Course dataset":
    sample_rows = 50_000 if row_choice.startswith("First") else None
    raw = read_jobs(COURSE_FILE, nrows=sample_rows)
    data_label = "Course data · first 50,000 rows" if sample_rows else "Full course dataset"
else:
    raw = read_jobs(DEMO_FILE)
    data_label = "Fictional demo data"

df = clean_jobs(raw)
with st.sidebar:
    st.divider()
    st.subheader("Filters")
    category_options = sorted(df["category"].dropna().astype(str).unique())
    selected_categories = st.multiselect("Industry / category", category_options, default=category_options)
    level_options = sorted(df["positionLevels"].dropna().astype(str).unique())
    selected_levels = st.multiselect("Career level", level_options, default=level_options)
    employment_options = sorted(df["employmentTypes"].dropna().astype(str).unique())
    selected_employment = st.multiselect("Employment type", employment_options, default=employment_options)

filtered = df[
    df["category"].astype(str).isin(selected_categories)
    & df["positionLevels"].astype(str).isin(selected_levels)
    & df["employmentTypes"].astype(str).isin(selected_employment)
].copy()

st.info(f"Showing **{data_label}** · {len(filtered):,} of {len(df):,} postings after filters")
if filtered.empty:
    st.warning("No postings match these filters. Select more categories, levels, or employment types.")
    st.stop()

salary = filtered["average_salary"].dropna()
metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Job postings", f"{len(filtered):,}")
metric2.metric("Categories", f"{filtered['category'].nunique():,}")
metric3.metric("Median listed salary", f"S${salary.median():,.0f}" if not salary.empty else "Not available")
metric4.metric("Salary coverage", f"{filtered['average_salary'].notna().mean():.0%}")

overview, salary_tab, trends_tab, demand_tab, skills_tab, career_tab, quality_tab = st.tabs(
    ["Overview", "Salary", "Trends", "Demand vs competition", "Skills", "Career recommender", "Data quality"]
)
# Views below use only postings with a title; the source file has 3,988 blank rows.
complete = filtered.dropna(subset=["title"])

with overview:
    left, right = st.columns(2)
    titles = filtered.dropna(subset=["title_key"]).groupby("title_key", as_index=False).agg(Role=("title", "first"), Postings=("title", "size"))
    role_counts = titles.sort_values("Postings", ascending=False).head(12)
    category_counts = filtered["category"].fillna("Unspecified").value_counts().head(10).rename_axis("Category").reset_index(name="Postings")
    left.subheader("Most-posted job titles")
    left.plotly_chart(px.bar(role_counts.sort_values("Postings"), x="Postings", y="Role", orientation="h", color_discrete_sequence=["#2F6B5F"]), use_container_width=True)
    right.subheader("Posting volume by category")
    right.plotly_chart(px.bar(category_counts.sort_values("Postings"), x="Postings", y="Category", orientation="h", color_discrete_sequence=["#D18B47"]), use_container_width=True)
    st.caption("These charts describe posting volume, not the number of unique employers or actual hires.")

with salary_tab:
    salary_rows = filtered.dropna(subset=["average_salary"])
    if salary_rows.empty:
        st.warning("No valid salary values are available for the current selection.")
    else:
        salary_by_category = salary_rows.groupby("category", as_index=False)["average_salary"].median().sort_values("average_salary", ascending=False).head(12)
        st.subheader("Median listed salary by category")
        st.plotly_chart(px.bar(salary_by_category.sort_values("average_salary"), x="average_salary", y="category", orientation="h", labels={"average_salary": "Median salary (S$)", "category": "Category"}, color_discrete_sequence=["#2F6B5F"]), use_container_width=True)
        st.caption("Salary values are posting-level midpoints where both bounds exist, unless the source provides `average_salary`.")

with trends_tab:
    dated = filtered.dropna(subset=["posted_date"])
    if dated.empty:
        st.warning("No dates could be parsed from the current file.")
    else:
        show_early = st.checkbox("Include months before May 2023 (data collection changed; not comparable)", value=False)
        monthly = monthly_postings(dated)
        if not show_early:
            monthly = monthly[monthly["month"] >= TREND_CUTOFF]
        st.subheader("Postings by month")
        st.plotly_chart(px.line(monthly, x="month", y="Postings", markers=True, color_discrete_sequence=["#2F6B5F"]), use_container_width=True)

        st.subheader("Compare categories over time")
        top_categories = dated["category"].value_counts().head(5).index.tolist()
        chosen = st.multiselect("Categories", sorted(dated["category"].dropna().unique()), default=top_categories)
        if chosen:
            by_category = monthly_postings(dated[dated["category"].isin(chosen)], by_category=True)
            if not show_early:
                by_category = by_category[by_category["month"] >= TREND_CUTOFF]
            st.plotly_chart(px.line(by_category, x="month", y="Postings", color="category", markers=True), use_container_width=True)
        st.caption("Trends use the posting date and the first category listed for each job. Read them from May 2023 onward.")

with demand_tab:
    market = category_market(complete)
    if market.empty or "metadata_totalNumberJobApplication" not in complete:
        st.info("Demand and competition need the application and vacancy columns, which are missing from this file.")
    else:
        min_postings = st.slider("Minimum postings per category", 500, 20_000, 2_000, step=500)
        view = market[market["postings"] >= min_postings].dropna(subset=["median_salary", "apps_per_vacancy"]).copy()
        if view.empty:
            st.warning("No categories meet this minimum. Lower the slider.")
        else:
            x_split = view["apps_per_vacancy"].median()
            y_split = view["postings"].median()
            view["Quadrant"] = np.select(
                [
                    (view["apps_per_vacancy"] < x_split) & (view["postings"] >= y_split),
                    (view["apps_per_vacancy"] < x_split) & (view["postings"] < y_split),
                    (view["apps_per_vacancy"] >= x_split) & (view["postings"] >= y_split),
                ],
                ["Big and open", "Small and open", "Big and crowded"],
                default="Small and crowded",
            )
            st.subheader("Demand (postings) against competition (applications per vacancy)")
            fig = px.scatter(
                view, x="apps_per_vacancy", y="postings", color="Quadrant", size="median_salary",
                hover_name="category", log_y=True,
                labels={"apps_per_vacancy": "Applications per vacancy", "postings": "Postings (log scale)"},
                color_discrete_map={"Big and open": "#2F6B5F", "Small and open": "#8FB8A8", "Big and crowded": "#D18B47", "Small and crowded": "#B8C4CC"},
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                f"Splits are the median of the categories shown: {x_split:.1f} applications per vacancy and {y_split:,.0f} postings. "
                "A posting counts in every category it belongs to. Applications per vacancy = total applications ÷ total vacancies."
            )
            table = view.sort_values("apps_per_vacancy")[["category", "postings", "median_salary", "apps_per_vacancy", "entry_friendly_share", "Quadrant"]]
            st.dataframe(
                table.rename(columns={
                    "category": "Category", "postings": "Postings", "median_salary": "Median salary (S$)",
                    "apps_per_vacancy": "Applications per vacancy", "entry_friendly_share": "Entry-friendly share",
                }).round({"Median salary (S$)": 0, "Applications per vacancy": 2, "Entry-friendly share": 2}),
                hide_index=True, use_container_width=True,
            )

with skills_tab:
    min_skill_postings = st.slider("Minimum postings per keyword", 100, 5_000, 500, step=100)
    skills = skill_premiums(complete, min_skill_postings)
    if skills.empty:
        st.warning("No keyword has enough postings. Lower the slider.")
    else:
        st.subheader("Salary premium for job titles mentioning each keyword")
        fig = px.bar(
            skills.sort_values("premium_pct"), x="premium_pct", y="skill", orientation="h",
            labels={"premium_pct": "Premium vs all postings (%)", "skill": "Keyword in job title"},
            color=np.where(skills.sort_values("premium_pct")["premium_pct"] >= 0, "Above overall median", "Below overall median"),
            color_discrete_map={"Above overall median": "#2F6B5F", "Below overall median": "#C0392B"},
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Skills are detected from job titles only, using the keyword list in data_utils.py. "
            "Premium = median salary of postings with the keyword ÷ median salary of all postings − 1. "
            "It shows association, not the effect of learning the skill."
        )
        st.dataframe(
            skills.rename(columns={"skill": "Keyword", "postings": "Postings", "median_salary": "Median salary (S$)", "premium_pct": "Premium (%)"})
            .round({"Median salary (S$)": 0, "Premium (%)": 1}),
            hide_index=True, use_container_width=True,
        )

with career_tab:
    st.subheader("Find career tracks that fit what matters to you")
    st.caption("A track is one category and one seniority band. Each factor is scored 0–100 across all tracks, then combined using your weights.")
    w_demand, w_pay, w_competition, w_access = st.columns(4)
    weights = {
        "demand": w_demand.slider("Demand", 0, 5, 3),
        "pay": w_pay.slider("Pay", 0, 5, 3),
        "competition": w_competition.slider("Low competition", 0, 5, 2),
        "access": w_access.slider("Easy to enter", 0, 5, 2),
    }
    min_track_postings = st.slider("Minimum postings per track", 200, 5_000, 1_000, step=100)
    tracks = career_tracks(complete, min_track_postings)
    if tracks.empty:
        st.warning("No career tracks meet this minimum. Lower the slider.")
    else:
        tracks = tracks.assign(fit=fit_score(tracks, weights)).sort_values("fit", ascending=False).head(15)
        st.dataframe(
            tracks.assign(**{"Needs ≤3 years (%)": tracks["accessible_share"] * 100})[
                ["track", "fit", "postings", "median_salary", "apps_per_vacancy", "Needs ≤3 years (%)"]
            ].rename(columns={
                "track": "Career track", "fit": "Fit score", "postings": "Postings",
                "median_salary": "Median salary (S$)", "apps_per_vacancy": "Applications per vacancy",
            }).round({"Fit score": 0, "Median salary (S$)": 0, "Applications per vacancy": 2, "Needs ≤3 years (%)": 0}),
            hide_index=True, use_container_width=True,
        )
        st.caption("This ranks tracks by the weights you set. It is a guide for exploration, not a prediction of hiring or success.")

with quality_tab:
    st.subheader("Checks on the selected data")
    quality = quality_summary(filtered)
    st.dataframe(pd.DataFrame([{"Check": key.replace("_", " ").title(), "Count": value} for key, value in quality.items()]), hide_index=True, use_container_width=True)
    st.write("Missing salary values remain missing. Dates that cannot be parsed are excluded from the time trend. Review these counts before using the charts in a decision.")
    st.subheader("Preview")
    st.dataframe(filtered.head(100), use_container_width=True)


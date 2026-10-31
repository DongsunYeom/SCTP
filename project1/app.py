# Standard library: Path helps build file locations relative to this script.
from pathlib import Path

# pandas: table library used for the data frames.
import pandas as pd

# plotly.express: quick way to make interactive charts.
import plotly.express as px

# streamlit: the web app framework that builds the page from Python code.
import streamlit as st

# numpy: number library, used here for np.select and np.where.
import numpy as np


# Helper functions and constants from data_utils.py (our own module).
from data_utils import (
    # Cutoff date; months before it are not comparable because data collection changed.
    TREND_CUTOFF,
    # Builds the career-track table (category + seniority band).
    career_tracks,
    # Builds the per-category market table (postings, salary, competition).
    category_market,
    # Cleans the raw job data (types, missing values, derived columns).
    clean_jobs,
    # Scores career tracks against the user's weights.
    fit_score,
    # Counts job postings per month.
    monthly_postings,
    # Summarises data-quality checks (missing values, etc.).
    quality_summary,
    # Reads a CSV file of job postings into a data frame.
    read_jobs,
    # Calculates the salary premium for each keyword in job titles.
    skill_premiums,
)


# Folder that contains this app.py file.
ROOT = Path(__file__).parent

# Path to the small fictional demo dataset.
DEMO_FILE = ROOT / "data" / "demo_jobs.csv"

# Path to the full course dataset (SGJobData.csv).
COURSE_FILE = ROOT / "data" / "SGJobData.csv"


# Set the browser tab title, tab icon, and use the full browser width.
st.set_page_config(page_title="Singapore Jobs Explorer", page_icon="📊", layout="wide")

# Show the main heading at the top of the page.
st.title("Singapore Jobs Explorer")

# Show a short grey description under the heading.
st.caption("A practical view of role demand and salary ranges for career conversations.")


# If the course CSV file exists on disk...
if COURSE_FILE.exists():
    # ...load the course dataset.
    raw = read_jobs(COURSE_FILE)
    # Label shown in the info box so the user knows which data is used.
    data_label = "Full course dataset"

# Otherwise (the course file is missing)...
else:
    # ...load the demo dataset instead.
    raw = read_jobs(DEMO_FILE)
    # Label shown in the info box for the demo data.
    data_label = "Fictional demo data"


# Clean the raw data so the charts and filters work on consistent columns.
df = clean_jobs(raw)


# Put the following widgets in the left sidebar.
with st.sidebar:
    # Draw a horizontal line to separate the sidebar sections.
    st.divider()

    # Show the "Filters" heading in the sidebar.
    st.subheader("Filters")

    # Unique, sorted list of industry categories (missing values removed).
    category_options = sorted(df["category"].dropna().astype(str).unique())
    # Dropdown for industry categories; starts empty, which means "all".
    selected_categories = st.multiselect("Industry / category", category_options)

    # Unique, sorted list of career levels (missing values removed).
    level_options = sorted(df["positionLevels"].dropna().astype(str).unique())
    # Dropdown for career levels; starts empty, which means "all".
    selected_levels = st.multiselect("Career level", level_options)

    # Unique, sorted list of employment types (missing values removed).
    employment_options = sorted(df["employmentTypes"].dropna().astype(str).unique())
    # Dropdown for employment types; starts empty, which means "all".
    selected_employment = st.multiselect("Employment type", employment_options)


# An empty dropdown means "no filter", so every option stays included.
# Keep the rows whose category, level and employment type match the selections.
filtered = df[
    # If nothing is picked for category, use all category options.
    df["category"].astype(str).isin(selected_categories or category_options)
    # Same rule for career level.
    & df["positionLevels"].astype(str).isin(selected_levels or level_options)
    # Same rule for employment type.
    & df["employmentTypes"].astype(str).isin(selected_employment or employment_options)
# Copy the result so later changes do not affect the original filtered view.
].copy()


# Show how many postings match the current data source and filters.
st.info(f"Showing **{data_label}** · {len(filtered):,} of {len(df):,} postings after filters")

# If no rows are left after filtering...
if filtered.empty:
    # ...warn the user to change the filters.
    st.warning("No postings match these filters. Select more categories, levels, or employment types.")
    # Stop running the rest of the page, since there is nothing to show.
    st.stop()


# Salary values with missing entries removed (used for the median).
salary = filtered["average_salary"].dropna()

# Create four side-by-side columns for the summary numbers.
metric1, metric2, metric3, metric4 = st.columns(4)

# Show the number of job postings.
metric1.metric("Job postings", f"{len(filtered):,}")
# Show the number of different categories.
metric2.metric("Categories", f"{filtered['category'].nunique():,}")
# Show the median salary in S$, or "Not available" if there are no salary values.
metric3.metric("Median listed salary", f"S${salary.median():,.0f}" if not salary.empty else "Not available")
# Show the share of postings that have a salary value.
metric4.metric("Salary coverage", f"{filtered['average_salary'].notna().mean():.0%}")


# Create seven tabs and unpack them into seven variables, one per tab.
overview, salary_tab, trends_tab, demand_tab, skills_tab, career_tab, quality_tab = st.tabs(
    # Tab titles, in the same order as the variables above.
    ["Overview", "Salary", "Trends", "Demand vs competition", "Skills", "Career recommender", "Data quality"]
)

# Views below use only postings with a title; the source file has 3,988 blank rows.
# Keep only postings that have a job title.
complete = filtered.dropna(subset=["title"])


# Put everything in this block inside the "Overview" tab.
with overview:
    # Create two side-by-side columns.
    left, right = st.columns(2)

    # Count postings per cleaned job-title key, keeping the first title as the display name.
    titles = filtered.dropna(subset=["title_key"]).groupby("title_key", as_index=False).agg(Role=("title", "first"), Postings=("title", "size"))
    # Take the 12 most-posted job titles.
    role_counts = titles.sort_values("Postings", ascending=False).head(12)
    # Count postings per category, keeping the top 10 and naming the columns.
    category_counts = filtered["category"].fillna("Unspecified").value_counts().head(10).rename_axis("Category").reset_index(name="Postings")

    # Heading above the left chart.
    left.subheader("Most-posted job titles")
    # Horizontal bar chart of the most-posted job titles, in the left column.
    left.plotly_chart(px.bar(role_counts.sort_values("Postings"), x="Postings", y="Role", orientation="h", color_discrete_sequence=["#2F6B5F"]), use_container_width=True)

    # Heading above the right chart.
    right.subheader("Posting volume by category")
    # Horizontal bar chart of postings per category, in the right column.
    right.plotly_chart(px.bar(category_counts.sort_values("Postings"), x="Postings", y="Category", orientation="h", color_discrete_sequence=["#D18B47"]), use_container_width=True)

    # Note explaining that these numbers are postings, not employers or hires.
    st.caption("These charts describe posting volume, not the number of unique employers or actual hires.")


# Put everything in this block inside the "Salary" tab.
with salary_tab:
    # Keep only postings that have a salary value.
    salary_rows = filtered.dropna(subset=["average_salary"])

    # If no salary values are left...
    if salary_rows.empty:
        # ...show a warning instead of a chart.
        st.warning("No valid salary values are available for the current selection.")

    # Otherwise, draw the salary chart.
    else:
        # Median salary per category, sorted from highest to lowest, top 12 only.
        salary_by_category = salary_rows.groupby("category", as_index=False)["average_salary"].median().sort_values("average_salary", ascending=False).head(12)

        # Heading for the salary chart.
        st.subheader("Median listed salary by category")
        # Horizontal bar chart of median salary per category, with readable axis labels.
        st.plotly_chart(px.bar(salary_by_category.sort_values("average_salary"), x="average_salary", y="category", orientation="h", labels={"average_salary": "Median salary (S$)", "category": "Category"}, color_discrete_sequence=["#2F6B5F"]), use_container_width=True)

        # Note explaining how the salary values were calculated.
        st.caption("Salary values are posting-level midpoints where both bounds exist, unless the source provides `average_salary`.")


# Put everything in this block inside the "Trends" tab.
with trends_tab:
    # Keep only postings that have a posted date.
    dated = filtered.dropna(subset=["posted_date"])

    # If no dates could be read...
    if dated.empty:
        # ...show a warning.
        st.warning("No dates could be parsed from the current file.")

    # Otherwise, draw the trend charts.
    else:
        # Checkbox that lets the user show months before May 2023; off by default.
        show_early = st.checkbox("Include months before May 2023 (data collection changed; not comparable)", value=False)

        # Count postings per month.
        monthly = monthly_postings(dated)
        # If the user did not tick the box...
        if not show_early:
            # ...hide months before the cutoff date.
            monthly = monthly[monthly["month"] >= TREND_CUTOFF]

        # Heading for the monthly chart.
        st.subheader("Postings by month")
        # Line chart of monthly postings, with a dot on each month.
        st.plotly_chart(px.line(monthly, x="month", y="Postings", markers=True, color_discrete_sequence=["#2F6B5F"]), use_container_width=True)

        # Heading for the category comparison chart.
        st.subheader("Compare categories over time")
        # The five categories with the most postings, used as the default selection.
        top_categories = dated["category"].value_counts().head(5).index.tolist()
        # Dropdown to choose which categories to compare; starts with the top five.
        chosen = st.multiselect("Categories", sorted(dated["category"].dropna().unique()), default=top_categories)

        # Only draw the comparison if at least one category is chosen.
        if chosen:
            # Count postings per month for each chosen category.
            by_category = monthly_postings(dated[dated["category"].isin(chosen)], by_category=True)
            # If the user did not tick the early-months box...
            if not show_early:
                # ...hide months before the cutoff date.
                by_category = by_category[by_category["month"] >= TREND_CUTOFF]
            # Multi-line chart with one line per chosen category.
            st.plotly_chart(px.line(by_category, x="month", y="Postings", color="category", markers=True), use_container_width=True)

        # Note explaining how the trend data was built.
        st.caption("Trends use the posting date and the first category listed for each job. Read them from May 2023 onward.")


# Put everything in this block inside the "Demand vs competition" tab.
with demand_tab:
    # Build the per-category table (postings, median salary, applications per vacancy).
    market = category_market(complete)

    # If the table is empty or the application column is missing...
    if market.empty or "metadata_totalNumberJobApplication" not in complete:
        # ...explain that this chart needs those columns.
        st.info("Demand and competition need the application and vacancy columns, which are missing from this file.")

    # Otherwise, draw the chart.
    else:
        # Slider for the minimum number of postings a category needs to be shown.
        min_postings = st.slider("Minimum postings per category", 500, 20_000, 2_000, step=500)

        # Keep categories with enough postings and with salary and competition values.
        view = market[market["postings"] >= min_postings].dropna(subset=["median_salary", "apps_per_vacancy"]).copy()

        # If no category passes the minimum...
        if view.empty:
            # ...ask the user to lower the slider.
            st.warning("No categories meet this minimum. Lower the slider.")

        # Otherwise, draw the scatter chart.
        else:
            # Median competition, used as the vertical split line.
            x_split = view["apps_per_vacancy"].median()
            # Median number of postings, used as the horizontal split line.
            y_split = view["postings"].median()

            # Label each category by which quadrant it falls in.
            view["Quadrant"] = np.select(
                [
                    # Less competition and more postings than the median.
                    (view["apps_per_vacancy"] < x_split) & (view["postings"] >= y_split),
                    # Less competition and fewer postings than the median.
                    (view["apps_per_vacancy"] < x_split) & (view["postings"] < y_split),
                    # More competition and more postings than the median.
                    (view["apps_per_vacancy"] >= x_split) & (view["postings"] >= y_split),
                ],
                # Names for the three quadrants above, in the same order.
                ["Big and open", "Small and open", "Big and crowded"],
                # Any category that matches none of the rules is "Small and crowded".
                default="Small and crowded",
            )

            # Heading for the scatter chart.
            st.subheader("Demand (postings) against competition (applications per vacancy)")
            # Scatter chart: each dot is a category, colored by quadrant, sized by median salary.
            fig = px.scatter(
                view, x="apps_per_vacancy", y="postings", color="Quadrant", size="median_salary",
                # Show the category name when hovering over a dot; use a log scale on postings.
                hover_name="category", log_y=True,
                # Friendly axis titles.
                labels={"apps_per_vacancy": "Applications per vacancy", "postings": "Postings (log scale)"},
                # Fixed colors for each quadrant.
                color_discrete_map={"Big and open": "#2F6B5F", "Small and open": "#8FB8A8", "Big and crowded": "#D18B47", "Small and crowded": "#B8C4CC"},
            )
            # Draw the scatter chart, stretched to the full width.
            st.plotly_chart(fig, use_container_width=True)

            # Explanation of the split lines and the formula used.
            st.caption(
                f"Splits are the median of the categories shown: {x_split:.1f} applications per vacancy and {y_split:,.0f} postings. "
                "A posting counts in every category it belongs to. Applications per vacancy = total applications ÷ total vacancies."
            )

            # Keep only the columns to show in the table, sorted by competition.
            table = view.sort_values("apps_per_vacancy")[["category", "postings", "median_salary", "apps_per_vacancy", "entry_friendly_share", "Quadrant"]]
            # Show the table with friendlier column names and rounded numbers.
            st.dataframe(
                table.rename(columns={
                    # Rename the columns to readable labels.
                    "category": "Category", "postings": "Postings", "median_salary": "Median salary (S$)",
                    "apps_per_vacancy": "Applications per vacancy", "entry_friendly_share": "Entry-friendly share",
                # Round the numbers to a sensible number of decimal places.
                }).round({"Median salary (S$)": 0, "Applications per vacancy": 2, "Entry-friendly share": 2}),
                # Hide the row numbers and stretch the table to full width.
                hide_index=True, use_container_width=True,
            )


# Put everything in this block inside the "Skills" tab.
with skills_tab:
    # Slider for the minimum number of postings a keyword needs to be shown.
    min_skill_postings = st.slider("Minimum postings per keyword", 100, 5_000, 500, step=100)

    # Calculate the salary premium for each keyword found in job titles.
    skills = skill_premiums(complete, min_skill_postings)

    # If no keyword has enough postings...
    if skills.empty:
        # ...ask the user to lower the slider.
        st.warning("No keyword has enough postings. Lower the slider.")

    # Otherwise, draw the chart.
    else:
        # Heading for the keyword premium chart.
        st.subheader("Salary premium for job titles mentioning each keyword")
        # Horizontal bar chart of premiums, sorted by value.
        fig = px.bar(
            skills.sort_values("premium_pct"), x="premium_pct", y="skill", orientation="h",
            # Friendly axis titles.
            labels={"premium_pct": "Premium vs all postings (%)", "skill": "Keyword in job title"},
            # Color bars green if the premium is 0 or higher, red if lower.
            color=np.where(skills.sort_values("premium_pct")["premium_pct"] >= 0, "Above overall median", "Below overall median"),
            # Fixed colors for the two groups.
            color_discrete_map={"Above overall median": "#2F6B5F", "Below overall median": "#C0392B"},
        )
        # Draw the chart, stretched to the full width.
        st.plotly_chart(fig, use_container_width=True)

        # Explanation of how skills and premiums are defined.
        st.caption(
            "Skills are detected from job titles only, using the keyword list in data_utils.py. "
            "Premium = median salary of postings with the keyword ÷ median salary of all postings − 1. "
            "It shows association, not the effect of learning the skill."
        )

        # Show the keyword table with friendlier names and rounded numbers.
        st.dataframe(
            skills.rename(columns={"skill": "Keyword", "postings": "Postings", "median_salary": "Median salary (S$)", "premium_pct": "Premium (%)"})
            # Round the salary and premium columns.
            .round({"Median salary (S$)": 0, "Premium (%)": 1}),
            # Hide the row numbers and stretch the table to full width.
            hide_index=True, use_container_width=True,
        )


# Put everything in this block inside the "Career recommender" tab.
with career_tab:
    # Heading for the recommender.
    st.subheader("Find career tracks that fit what matters to you")
    # Short explanation of how the score works.
    st.caption("A track is one category and one seniority band. Each factor is scored 0–100 across all tracks, then combined using your weights.")

    # Create four side-by-side columns, one per weight slider.
    w_demand, w_pay, w_competition, w_access = st.columns(4)
    # Store the user's weight for each factor (0 to 5).
    weights = {
        # How much job demand matters.
        "demand": w_demand.slider("Demand", 0, 5, 3),
        # How much pay matters.
        "pay": w_pay.slider("Pay", 0, 5, 3),
        # How much low competition matters.
        "competition": w_competition.slider("Low competition", 0, 5, 2),
        # How much an easy entry (low years of experience needed) matters.
        "access": w_access.slider("Easy to enter", 0, 5, 2),
    }

    # Slider for the minimum number of postings a track needs to be included.
    min_track_postings = st.slider("Minimum postings per track", 200, 5_000, 1_000, step=100)
    # Build the career-track table, keeping only tracks with enough postings.
    tracks = career_tracks(complete, min_track_postings)

    # If no track passes the minimum...
    if tracks.empty:
        # ...ask the user to lower the slider.
        st.warning("No career tracks meet this minimum. Lower the slider.")

    # Otherwise, score and show the tracks.
    else:
        # Add a fit score to each track, sort best first, and keep the top 15.
        tracks = tracks.assign(fit=fit_score(tracks, weights)).sort_values("fit", ascending=False).head(15)

        # Show the ranked tracks as a table.
        st.dataframe(
            # Add a percentage column for jobs that need 3 years or less of experience.
            tracks.assign(**{"Needs ≤3 years (%)": tracks["accessible_share"] * 100})[
                # Keep and order the columns to show.
                ["track", "fit", "postings", "median_salary", "apps_per_vacancy", "Needs ≤3 years (%)"]
            # Rename the columns to readable labels.
            ].rename(columns={
                "track": "Career track", "fit": "Fit score", "postings": "Postings",
                "median_salary": "Median salary (S$)", "apps_per_vacancy": "Applications per vacancy",
            # Round the numbers to whole numbers or two decimals.
            }).round({"Fit score": 0, "Median salary (S$)": 0, "Applications per vacancy": 2, "Needs ≤3 years (%)": 0}),
            # Hide the row numbers and stretch the table to full width.
            hide_index=True, use_container_width=True,
        )

        # Disclaimer that this is a guide, not a prediction.
        st.caption("This ranks tracks by the weights you set. It is a guide for exploration, not a prediction of hiring or success.")


# Put everything in this block inside the "Data quality" tab.
with quality_tab:
    # Heading for the data checks.
    st.subheader("Checks on the selected data")
    # Calculate data-quality counts for the filtered data.
    quality = quality_summary(filtered)
    # Show the counts as a table, turning each key into a readable title (e.g. "missing_salary" -> "Missing Salary").
    st.dataframe(pd.DataFrame([{"Check": key.replace("_", " ").title(), "Count": value} for key, value in quality.items()]), hide_index=True, use_container_width=True)

    # Notes on how missing values and dates are handled.
    st.write("Missing salary values remain missing. Dates that cannot be parsed are excluded from the time trend. Review these counts before using the charts in a decision.")

    # Heading for the raw data preview.
    st.subheader("Preview")
    # Show the first 100 rows of the filtered data.
    st.dataframe(filtered.head(100), use_container_width=True)

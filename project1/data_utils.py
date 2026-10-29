"""Loading and cleaning helpers for the Singapore Jobs Explorer."""

from __future__ import annotations

import json
from collections.abc import Iterable

import pandas as pd


DATE_CANDIDATES = (
    "metadata_newPostingDate",
    "metadata_originalPostingDate",
    "posted_date",
    "date_posted",
)


def read_jobs(source, nrows: int | None = None) -> pd.DataFrame:
    """Read a path or Streamlit UploadedFile as CSV."""
    return pd.read_csv(source, low_memory=False, nrows=nrows)


def _first_existing(columns: Iterable[str], candidates: Iterable[str]) -> str | None:
    return next((name for name in candidates if name in columns), None)


def _category_names(value) -> list[str]:
    """Every category a posting belongs to, in source order."""
    if pd.isna(value):
        return []
    if isinstance(value, list):
        items = value
    else:
        try:
            items = json.loads(str(value))
        except (json.JSONDecodeError, TypeError):
            text = str(value).strip()
            return [text] if text else []
    names = []
    for item in items or []:
        name = item.get("category") or item.get("name") if isinstance(item, dict) else str(item)
        if name:
            names.append(str(name).strip())
    return names


def _category_name(value) -> str | None:
    names = _category_names(value)
    return names[0] if names else None


def clean_jobs(raw: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy while preserving unrecognised source columns."""
    df = raw.copy()
    df.columns = [str(column).strip() for column in df.columns]

    if "title" not in df and "job_title" in df:
        df["title"] = df["job_title"]
    if "categories" in df:
        df["category"] = df["categories"].map(_category_name)
    elif "category" not in df:
        df["category"] = "Unspecified"

    new_date = (
        pd.to_datetime(df["metadata_newPostingDate"], format="mixed", errors="coerce", dayfirst=True)
        if "metadata_newPostingDate" in df
        else pd.Series(pd.NaT, index=df.index)
    )
    original_date = (
        pd.to_datetime(df["metadata_originalPostingDate"], format="mixed", errors="coerce", dayfirst=True)
        if "metadata_originalPostingDate" in df
        else pd.Series(pd.NaT, index=df.index)
    )
    fallback_date = _first_existing(df.columns, ("posted_date", "date_posted"))
    extra_date = (
        pd.to_datetime(df[fallback_date], format="mixed", errors="coerce", dayfirst=True)
        if fallback_date
        else pd.Series(pd.NaT, index=df.index)
    )
    df["posted_date"] = new_date.fillna(original_date).fillna(extra_date)

    for column in ("salary_minimum", "salary_maximum", "average_salary", "numberOfVacancies", "minimumYearsExperience"):
        if column in df:
            df[column] = pd.to_numeric(df[column], errors="coerce")
            if column in {"salary_minimum", "salary_maximum", "average_salary"}:
                # This export encodes its 3,988 otherwise-empty rows with zero salary.
                df[column] = df[column].mask(df[column] <= 0)

    if "average_salary" not in df:
        if {"salary_minimum", "salary_maximum"}.issubset(df.columns):
            valid_bounds = df["salary_minimum"].notna() & df["salary_maximum"].notna()
            df["average_salary"] = ((df["salary_minimum"] + df["salary_maximum"]) / 2).where(valid_bounds)
        else:
            df["average_salary"] = float("nan")

    for column in ("title", "employmentTypes", "positionLevels", "postedCompany_name", "category"):
        if column in df:
            df[column] = df[column].astype("string").str.strip()
            df[column] = df[column].replace({"": pd.NA, "nan": pd.NA})

    if "title" not in df:
        df["title"] = "Untitled role"
    df["title_key"] = df["title"].astype("string").str.strip().str.casefold()
    for column in ("employmentTypes", "positionLevels", "category"):
        if column not in df:
            df[column] = "Unspecified"

    return df


def quality_summary(df: pd.DataFrame) -> dict[str, int]:
    """Small set of transparent data-quality counts for the dashboard."""
    return {
        "rows": len(df),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_titles": int(df["title"].isna().sum()),
        "missing_salaries": int(df["average_salary"].isna().sum()),
        "unparsed_dates": int(df["posted_date"].isna().sum()),
    }



SENIORITY_BANDS = {
    "Fresh/entry level": "Entry",
    "Non-executive": "Entry",
    "Junior Executive": "Junior",
    "Executive": "Mid",
    "Professional": "Mid",
    "Senior Executive": "Senior",
    "Manager": "Management",
    "Middle Management": "Management",
    "Senior Management": "Management",
}

TREND_CUTOFF = pd.Timestamp("2023-05-01")  # posting trends before this month are not comparable

SKILL_KEYWORDS = {
    "Python": r"\bpython\b",
    "SQL": r"\bsql\b",
    "Java": r"\bjava\b",
    ".NET": r"\.net\b",
    "AWS": r"\baws\b",
    "Azure": r"\bazure\b",
    "SAP": r"\bsap\b",
    "Excel": r"\bexcel\b",
    "Cloud": r"\bcloud\b",
    "Data": r"\bdata\b",
    "Cybersecurity": r"cyber|security",
    "Machine learning / AI": r"machine learning|\bai\b|\bml\b",
    "Salesforce": r"salesforce",
    "React": r"\breact\b",
    "Project management": r"project manag",
    "Accounting": r"account",
    "Digital marketing": r"digital market",
    "Nursing": r"\bnurs",
}


def _numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame:
        return pd.Series(float("nan"), index=frame.index)
    return pd.to_numeric(frame[column], errors="coerce")


def _one_row_per_category(df: pd.DataFrame) -> pd.DataFrame:
    """A posting appears once for every category it belongs to."""
    if "categories" in df:
        names = df["categories"].map(_category_names)
    else:
        names = df["category"].map(lambda value: [value] if pd.notna(value) else [])
    return df.assign(category_all=names).explode("category_all").dropna(subset=["category_all"])


def category_market(df: pd.DataFrame) -> pd.DataFrame:
    """One row per category. Applications per vacancy = total applications / total vacancies."""
    long = _one_row_per_category(df)
    if long.empty:
        return pd.DataFrame()
    long = long.assign(
        applications=_numeric(long, "metadata_totalNumberJobApplication"),
        vacancies=_numeric(long, "numberOfVacancies").where(lambda s: s > 0, 1),
        years=_numeric(long, "minimumYearsExperience"),
    )
    grouped = long.groupby("category_all").agg(
        postings=("title_key", "size"),
        median_salary=("average_salary", "median"),
        applications=("applications", "sum"),
        vacancies=("vacancies", "sum"),
        entry_friendly_share=("years", lambda s: (s <= 1).mean()),
    ).reset_index().rename(columns={"category_all": "category"})
    grouped["apps_per_vacancy"] = grouped["applications"] / grouped["vacancies"]
    return grouped.drop(columns=["applications", "vacancies"])


def skill_premiums(df: pd.DataFrame, min_postings: int = 500) -> pd.DataFrame:
    """Median salary of postings whose title mentions a keyword, against all postings."""
    overall = df["average_salary"].median()
    rows = []
    for skill, pattern in SKILL_KEYWORDS.items():
        mask = df["title_key"].str.contains(pattern, regex=True, na=False)
        salaries = df.loc[mask, "average_salary"].dropna()
        if mask.sum() < min_postings or salaries.empty:
            continue
        median = salaries.median()
        rows.append({
            "skill": skill,
            "postings": int(mask.sum()),
            "median_salary": median,
            "premium_pct": (median / overall - 1) * 100,
        })
    return pd.DataFrame(rows).sort_values("premium_pct", ascending=False) if rows else pd.DataFrame()


def career_tracks(df: pd.DataFrame, min_postings: int = 500) -> pd.DataFrame:
    """Track = category + seniority band. Scores are percentile ranks (0-100)."""
    frame = _one_row_per_category(df).assign(
        seniority=lambda d: d["positionLevels"].map(SENIORITY_BANDS),
        years=lambda d: _numeric(d, "minimumYearsExperience"),
        applications=lambda d: _numeric(d, "metadata_totalNumberJobApplication"),
        vacancies=lambda d: _numeric(d, "numberOfVacancies").where(lambda s: s > 0, 1),
    ).dropna(subset=["seniority"])
    if frame.empty:
        return pd.DataFrame()
    frame = frame.assign(track=frame["category_all"] + " · " + frame["seniority"])
    grouped = frame.groupby("track").agg(
        postings=("title_key", "size"),
        median_salary=("average_salary", "median"),
        applications=("applications", "sum"),
        vacancies=("vacancies", "sum"),
        accessible_share=("years", lambda s: (s <= 3).mean()),
    ).reset_index()
    grouped = grouped[grouped["postings"] >= min_postings].copy()
    if grouped.empty:
        return grouped
    grouped["apps_per_vacancy"] = grouped["applications"] / grouped["vacancies"]
    grouped["demand_score"] = grouped["postings"].rank(pct=True) * 100
    grouped["pay_score"] = grouped["median_salary"].rank(pct=True) * 100
    grouped["low_competition_score"] = (-grouped["apps_per_vacancy"]).rank(pct=True) * 100
    grouped["access_score"] = grouped["accessible_share"].rank(pct=True) * 100
    return grouped.drop(columns=["applications", "vacancies"])


def fit_score(tracks: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """Weighted average of the four percentile scores, using slider weights."""
    total = sum(weights.values()) or 1.0
    return (
        tracks["demand_score"] * weights["demand"]
        + tracks["pay_score"] * weights["pay"]
        + tracks["low_competition_score"] * weights["competition"]
        + tracks["access_score"] * weights["access"]
    ) / total


def monthly_postings(df: pd.DataFrame, by_category: bool = False) -> pd.DataFrame:
    """Postings per month from the selected posting date."""
    dated = df.dropna(subset=["posted_date"]).copy()
    dated["month"] = dated["posted_date"].dt.to_period("M").dt.to_timestamp()
    keys = ["month", "category"] if by_category else ["month"]
    return dated.groupby(keys).size().rename("Postings").reset_index()

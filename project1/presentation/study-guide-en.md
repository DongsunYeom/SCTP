# Study Guide — Module 1 (Data Foundations) · Based on Singapore Jobs Explorer

This guide condenses the core ideas from Lessons 1.2–1.10, explains each function and keyword in detail, and shows where it is used in our project. Each section ends with **check questions**. If you can answer them, you can explain the project and its code during the presentation.

---

## 1. Database Basics (Lesson 1.2)

**Core concepts**
- **Table:** a set of rows and columns. Think of it as one spreadsheet sheet.
- **Row (record):** one entity, for example one job posting.
- **Column (attribute):** one property of the entity, for example the salary.
- **Primary key:** a column (or set of columns) that uniquely identifies each row.
- **ERD (Entity-Relationship Diagram):** a drawing of tables and how they relate, such as one-to-many.
- **Normalization:** splitting data so each fact is stored once.
  - **1NF:** each cell holds one value, and rows are unique. A list stored in one cell breaks 1NF.
  - **2NF:** every non-key column depends on the whole key, not just part of a composite key.
  - **3NF:** no column depends on another non-key column (no chains such as `job → category → category_group`).

**Link to our project**
- The `categories` column is a JSON array, so one cell holds several values, which breaks 1NF. `_category_names()` in `data_utils.py` unpacks it into one row per category.

**Check questions**
1. Give a 1NF, 2NF, and 3NF example from a job-posting table.
2. When one job belongs to several categories, how should the rows be split?

---

## 2. SQL Basics — DDL (Lesson 1.3)

DDL (Data Definition Language) defines the structure of data. It does not change the rows.

| Statement | Purpose | Example |
|---|---|---|
| `CREATE TABLE` | Create a table and its columns | `CREATE TABLE jobs (id VARCHAR PRIMARY KEY, title VARCHAR);` |
| `PRIMARY KEY` | Unique, not-null identifier | `id` above |
| `NOT NULL` | Column cannot be empty | `title VARCHAR NOT NULL` |
| `UNIQUE` | No two rows may share the value | `UNIQUE (email)` |
| `INDEX` | Speeds up lookups on a column | `CREATE INDEX idx_title ON jobs(title);` |
| `VIEW` | A saved query that behaves like a table | `CREATE VIEW senior_jobs AS SELECT * FROM jobs WHERE level = 'Senior';` |
| `DROP` | Deletes a table or view | `DROP TABLE jobs;` |

**Key difference:** a `TABLE` stores data. A `VIEW` stores only the query, and recalculates from the table each time it is read.

**Link to our project:** `metadata_jobPostId` is unique per row, so it works as a primary key. The project checked this and found no repeated IDs.

**Check questions**
1. What happens if you insert a second row with the same primary key?
2. Does a `VIEW` store the data? Why or why not?

---

## 3. SQL Basics — DML (Lesson 1.4)

DML (Data Manipulation Language) reads and changes rows. `SELECT` is the most common.

**Clauses, in the order they are written**

| Clause | Purpose |
|---|---|
| `SELECT` | Which columns to return |
| `FROM` | Which table |
| `WHERE` | Filter **rows before** grouping |
| `GROUP BY` | Combine rows that share a value |
| `HAVING` | Filter **groups after** aggregation |
| `ORDER BY` | Sort the result |
| `LIMIT` | Keep only the first N rows |

**Aggregate functions:** `COUNT(*)` counts rows, `COUNT(col)` skips NULLs, `AVG`, `SUM`, `MIN`, `MAX`.

**`WHERE` vs `HAVING`**
- `WHERE salary > 3000` removes rows before grouping.
- `HAVING COUNT(*) > 1000` removes groups after grouping.
- You cannot use an aggregate such as `COUNT(*)` in `WHERE`.

**`CASE WHEN`:** an if/else inside a query.
```sql
SELECT title,
       CASE WHEN positionLevels IN ('Manager', 'Senior Management') THEN 'Management'
            WHEN positionLevels = 'Senior Executive' THEN 'Senior'
            ELSE 'Other'
       END AS band
FROM jobs;
```

**`CAST`:** converts a type. `CAST(salary AS DOUBLE)` turns text into a number.

**Link to our project:** grouping nine position levels into five bands uses the same idea as `CASE`. See `SENIORITY_BANDS` in `data_utils.py`.

**Check questions**
1. Why is `WHERE` used before `GROUP BY` and `HAVING` after it?
2. Why can the number of postings differ from the number of postings per category?

---

## 4. Advanced SQL — Joins, Unions, Window Functions, CTEs (Lesson 1.5)

### 4.1 Joins: combining two tables on a key

A **JOIN** matches rows from two tables where a key column is equal. Use this sample:

```
employees                  departments
id | name    | dept_id     dept_id | dept_name
1  | Alice   | 10          10      | Engineering
2  | Bob     | 20          20      | Sales
3  | Chen    | NULL        30      | HR
```

| JOIN type | Rows returned | Result for the sample |
|---|---|---|
| **INNER JOIN** | Only rows that match in **both** tables | Alice (Engineering), Bob (Sales). Chen has no dept, and HR has no employees, so both are dropped. |
| **LEFT JOIN** | **All** left rows, plus matches from the right. Unmatched right columns are NULL. | Alice, Bob, and Chen (Chen's `dept_name` is NULL). |
| **RIGHT JOIN** | **All** right rows, plus matches from the left. Unmatched left columns are NULL. | Alice, Bob, and HR (HR's `name` is NULL). |
| **FULL OUTER JOIN** | **All** rows from both tables. NULL wherever there is no match on either side. | Alice, Bob, Chen, and HR. |

**Rules of thumb**
- Use `INNER JOIN` when you only want complete matches.
- Use `LEFT JOIN` when the left table is the "main" list and you want to keep it whole, even with missing matches.
- `RIGHT JOIN` is the mirror of `LEFT JOIN`; in practice, swap the table order and use `LEFT JOIN`.
- Use `FULL OUTER JOIN` to see everything from both sides, including the gaps.

**Common mistake:** filtering on a right-table column in `WHERE` after a `LEFT JOIN` turns it back into an `INNER JOIN`, because NULL rows fail the filter.

```sql
-- Keeps Chen only if the filter allows NULL:
SELECT e.name, d.dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.dept_id
WHERE d.dept_name IS NULL OR d.dept_name = 'Engineering';
```

### 4.2 UNION: stacking results vertically

`UNION` combines the rows of two queries with the same number and type of columns.

| Operator | Behaviour |
|---|---|
| `UNION` | Stacks the rows and **removes duplicates** |
| `UNION ALL` | Stacks the rows and **keeps duplicates** (faster) |

```sql
SELECT category FROM jobs_2023
UNION ALL
SELECT category FROM jobs_2024;
```

**Difference from JOIN:** a JOIN adds columns side by side by matching keys. A UNION adds rows underneath each other.

### 4.3 Window functions: calculations across related rows

A window function computes a value for each row using a group of related rows, **without collapsing them** (unlike `GROUP BY`).

- `OVER (...)` defines the window.
- `PARTITION BY` splits the rows into separate groups.
- `ORDER BY` sets the order inside each group.

```sql
SELECT month,
       postings,
       SUM(postings) OVER (ORDER BY month) AS running_total   -- cumulative sum
FROM monthly;

SELECT category, title, median_salary,
       RANK() OVER (PARTITION BY category ORDER BY median_salary DESC) AS rnk
FROM titles;                                                  -- rank within each category
```

| Function | Meaning |
|---|---|
| `ROW_NUMBER()` | 1, 2, 3, … with no ties handling |
| `RANK()` | Same rank for ties, then skips (1, 1, 3) |
| `SUM() OVER` | Running or group total |

**`QUALIFY`:** filters on window results. Think of it as `WHERE` for window functions (supported in DuckDB and some other engines).
```sql
SELECT category, title, RANK() OVER (PARTITION BY category ORDER BY postings DESC) AS rnk
FROM titles
QUALIFY rnk <= 3;     -- top 3 titles in each category
```

### 4.4 CTEs and subqueries: breaking a query into steps

A **CTE** (Common Table Expression) names an intermediate result with `WITH`.
```sql
WITH cleaned AS (
    SELECT * FROM jobs WHERE salary_min > 0
),
by_category AS (
    SELECT category, COUNT(*) AS postings FROM cleaned GROUP BY category
)
SELECT * FROM by_category WHERE postings > 1000;
```

A **subquery** is a query inside another query. It works, but it is harder to read than a CTE for several steps.

**Check questions**
1. Why does `LEFT JOIN` followed by a `WHERE` on the right table act like an `INNER JOIN`?
2. What is the difference between `UNION` and `UNION ALL`, and when would you choose `UNION ALL`?
3. How does `RANK() OVER (PARTITION BY ...)` differ from `GROUP BY`?

---

## 5. NumPy Basics (Lesson 1.6)

**`ndarray`:** a fixed-type, multi-dimensional array stored in one memory block. Operations on it run in compiled code, which is much faster than Python loops.

**Creation and casting**
```python
import numpy as np
a = np.ones((3, 4))              # 3×4 array of 1.0
b = a.astype(np.float32)         # half the memory of float64
c = np.array(["1.5", "2"]).astype(float)   # text → numbers
```

**Broadcasting:** NumPy's rules for operating on arrays of different shapes. It compares shapes from the right; each pair of dimensions must be equal, or one must be 1.
```python
prices = np.array([10, 20, 30])        # shape (3,)
factor = np.array([[1], [2]])          # shape (2, 1)
prices * factor                        # shape (2, 3): each row of prices × 1 or 2
```

**Boolean indexing:** select elements with a True/False array.
```python
scores = np.array([72, 85, 90, 60])
scores[scores >= 80]                   # [85 90]
scores[scores < 80] = 0                # changes the original array in place
```

**`ufunc` (universal function):** a fast element-by-element operation such as `np.sqrt`, `np.log`, `np.add`. Use these instead of loops.

**Statistics:** `mean`, `median`, `std`, `min`, `max`, `sum`, and `axis=` to choose rows (`axis=0`) or columns (`axis=1`).

**Linear algebra basics:** `np.dot` and `@` for matrix multiplication, `.T` for transpose, `np.linalg` for inverses and solving equations.

**Check questions**
1. Why is `a * b` on NumPy arrays faster than a Python `for` loop?
2. In `scores[scores < 80] = 0`, is the original array changed? Why?
3. What shape do you get when you multiply shape `(3,)` by shape `(2, 1)`?

---

## 6. Pandas Basics (Lesson 1.7)

**Data structures**
- **`Series`:** one labelled column of values. `df["salary"]` returns a Series.
- **`DataFrame`:** a table of Series sharing one index. `df` is the whole table.

### 6.1 Selecting: `loc` vs `iloc`

| Tool | Selects by | Slice end | Example |
|---|---|---|---|
| `loc` | **Label** (row index name, column name) | **Included** | `df.loc[0:2, "title"]` returns rows labelled 0, 1, 2 |
| `iloc` | **Integer position** (0 is the first row) | **Excluded** | `df.iloc[0:2, 0]` returns the first two rows, first column |

```python
df.loc[df["salary"] > 3000, ["title", "salary"]]   # rows where salary > 3000
df.iloc[:5]                                        # first 5 rows by position
df.iloc[-1]                                        # last row
```

**Rule:** use `loc` when you know the label or a condition; use `iloc` when you know the position. If the index is the default `0, 1, 2, …`, the two often look the same, but they are different tools.

### 6.2 Other selection and filtering

- `df["col"]` returns a column; `df[["a", "b"]]` returns several columns.
- `df[df["col"] > 0]` filters rows with a boolean condition.
- `df.query("salary > 3000")` filters with a string expression.

### 6.3 Modifying

- `df["new"] = df["a"] * 2` adds a column.
- `df["col"].astype(float)` changes the type.
- `df.dropna(subset=["title"])` removes rows where the title is missing.
- `df["col"].fillna(0)` replaces missing values.
- `df["col"].mask(cond)` sets values to NaN where `cond` is True. `where(cond)` is the opposite: it keeps values where `cond` is True and sets the rest to NaN.
- `pd.to_datetime(col, errors="coerce")` converts text to dates. Values that cannot be read become NaT (missing date).

### 6.4 Analysis

| Function | What it does | Example |
|---|---|---|
| `groupby(key).agg(...)` | Groups rows and computes summaries per group | `df.groupby("category").agg(n=("title","size"))` |
| `value_counts()` | Counts how often each value appears | `df["category"].value_counts().head(5)` |
| `sort_values(by, ascending)` | Sorts rows | `df.sort_values("postings", ascending=False)` |
| `apply(func)` | Runs a function on each element or row | `df["title"].apply(str.strip)` |
| `explode(col)` | Turns a list in one cell into one row per item | a row with `["IT","Engineering"]` becomes two rows |
| `merge(other, on=...)` | Pandas version of a SQL JOIN (see Section 4.1) | `df.merge(depts, on="dept_id", how="left")` |
| `pivot_table` | Cross-tabulates values, like a spreadsheet pivot | `df.pivot_table(index="category", columns="level", values="salary", aggfunc="median")` |

**Link to our project**
- `clean_jobs()` renames columns, converts dates with `pd.to_datetime`, and masks zero salaries with `mask`.
- `category_market()` combines `explode()` with `groupby().agg()`.
- `monthly_postings()` uses `dt.to_period("M")` to group dates by month.

**Check questions**
1. What is the difference between `df.loc[2:4]` and `df.iloc[2:4]`?
2. Why does `loc` include the end of a slice but `iloc` does not?
3. When would you use `explode()`, and what does it do to the row count?
4. What is the difference between `mask` and `where`?

---

## 7. Exploratory Data Analysis — Basic (Lesson 1.8)

**Descriptive statistics**
- **Mean:** the sum of values divided by the count. Sensitive to very large or very small values.
- **Median:** the middle value when sorted. Half the values are above, half below.
- **Quartiles:** the 25th percentile (Q1), median (Q2), and 75th percentile (Q3). The middle 50% lies between Q1 and Q3.
- **Min / max:** the extremes. Check these first, because impossible values show up there.
- **Standard deviation:** how spread out the values are around the mean.
- **Skew:** a long tail on one side. Salary data is usually right-skewed (a long tail of high salaries), so the mean is larger than the median.

**Data quality checks**
- **Missing values:** the share of blank cells per column.
- **Duplicates:** the same row, or the same ID, appearing more than once.
- **Impossible values:** a monthly salary of 0, a negative count, or a maximum far above the rest of the data.
- **Zero vs missing:** zero means "a value of zero". A missing value means "no value was recorded". Many datasets use 0 to mean "not disclosed", which must be treated as missing.

**Data transformation:** creating the columns you need (for example, a salary midpoint) and grouping continuous values into bands.

**Link to our project**
- Median is used because a few very high salaries pull the mean up. In the notebook, the mean is S$824 higher than the median.
- A monthly salary of 0 is treated as "not disclosed" and set to missing. The presentation has to explain this decision.

**Check questions**
1. Why use the median instead of the mean? Give a salary example.
2. Is "the value is zero" the same as "the value is missing"? What does this project decide?
3. What does a right-skewed distribution look like, and which summary statistic describes it better?

---

## 8. Exploratory Data Analysis — Advanced (Lesson 1.9)

**Time series:** data indexed by date. Typical steps: convert the text to dates, group by month (`dt.to_period("M")`), then count or average per month.

**Data integration:** combining several tables on a shared key. This is the same logic as JOINs (Section 4.1); in pandas, use `merge`.

**Aggregation and reporting:** always state what you count (postings, vacancies, or people) and at what level (row, category, or month). Unclear units cause wrong conclusions.

**From table to decision:** a result is useful only when you can say what action it supports, for example "shortlist categories with many postings and few applicants per seat".

**Link to our project**
- Views and application counts before May 2023 were collected differently, so they cannot be compared. Trends start in May 2023.
- Postings fall sharply after June 2024. The cause is unconfirmed, so the presentation does not call it a market slowdown.

**Check questions**
1. What should you check before reading a monthly trend?
2. What problems appear when the way data is collected changes partway through?
3. Why must you say what unit you are counting?

---

## 9. Data Visualisation and Storytelling (Lesson 1.10)

**Choosing a chart**

| Goal | Chart |
|---|---|
| Compare values across categories | Bar chart (horizontal if labels are long) |
| Show change over time | Line chart |
| Show the spread of values | Histogram or box plot |
| Show the relationship between two numbers | Scatter plot |
| Show parts of a whole | Stacked bar (few parts only), not pie charts with many slices |

**Storytelling rules**
- One chart, one message. Put the conclusion in the title (for example, "Pay rises with seniority").
- Highlight one bar or point in colour and grey out the rest.
- Label axes with units, and include value labels when readers need exact numbers.

**Log axis:** spaces values by orders of magnitude (1, 10, 100, 1000). Use it when values range over several powers of ten, such as posting counts from 500 to 140,000. Always label it as log, or readers will misread the distances.

**Link to our project**
- The "Demand vs competition" scatter plot uses a log scale for postings on the y-axis, and the axis is labelled.
- Presentation bar charts carry value labels so they are easy to read.

**Check questions**
1. Which chart would you use to show monthly change?
2. What must you always do when you use a log axis?
3. Why should the chart title state the conclusion?

---

## 10. Function and Keyword Quick Reference

| Term | Lesson | One-line meaning |
|---|---|---|
| `PRIMARY KEY` | 1.2 / 1.3 | Unique identifier for each row |
| `INNER JOIN` | 1.5 | Rows that match in both tables |
| `LEFT JOIN` | 1.5 | All left rows, matched right rows, NULL where no match |
| `RIGHT JOIN` | 1.5 | All right rows, matched left rows, NULL where no match |
| `FULL OUTER JOIN` | 1.5 | All rows from both sides, NULL where no match |
| `UNION` / `UNION ALL` | 1.5 | Stack rows; `UNION` removes duplicates |
| `RANK() OVER` | 1.5 | Rank within a partition, with ties sharing a rank |
| `QUALIFY` | 1.5 | Filter on window function results |
| `WITH` (CTE) | 1.5 | Name an intermediate result |
| `ndarray` | 1.6 | Fast, fixed-type NumPy array |
| Broadcasting | 1.6 | Operating on arrays of different shapes |
| `loc` | 1.7 | Select by label; end included |
| `iloc` | 1.7 | Select by position; end excluded |
| `groupby().agg()` | 1.7 | Summaries per group |
| `explode()` | 1.7 | One row per list item |
| `merge()` | 1.7 / 1.9 | Pandas JOIN |
| Median | 1.8 | Middle value; resistant to outliers |
| Log axis | 1.10 | Axis spaced by powers of ten |

---

## References

- Course material: `lesson.md` in each lesson repository (1.2 to 1.10)
- Project analysis: `notebooks/01_eda.ipynb`, the app code in `app.py`, and `data_utils.py`
- Presentation material: the `presentation/` folder and `Singapore_Jobs_Explorer.pptx`

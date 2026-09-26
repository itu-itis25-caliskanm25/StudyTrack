import pandas as pd
import numpy as np

DATA_PATH = "oulad_studytrack_dataset_v2.csv"

GROUP_COLS = [
    "student_id",
    "code_module",
    "code_presentation",
]

print("=" * 70)
print("STUDYTRACK OULAD V2 - FAST LEAKAGE CHECK")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

print("\nDataset:")
print(df.shape)

# ---------------------------------------------------------
# 1. BASIC CHECKS
# ---------------------------------------------------------

print("\n[1] BASIC CHECKS")
print("-" * 70)

print("Missing values:", df.isna().sum().sum())
print("Duplicate rows:", df.duplicated().sum())
print(
    "Duplicate student + assessment:",
    df.duplicated(
        subset=["student_id", "assessment_id"]
    ).sum()
)

# ---------------------------------------------------------
# 2. SAME-DAY ASSESSMENTS
# ---------------------------------------------------------

print("\n[2] SAME-DAY ASSESSMENTS")
print("-" * 70)

same_day = (
    df.groupby(GROUP_COLS + ["assessment_day"])
      .size()
)

print(
    "Groups containing multiple assessments:",
    (same_day > 1).sum()
)

print(
    "Rows belonging to those groups:",
    same_day[same_day > 1].sum()
)

# ---------------------------------------------------------
# 3. PREVIOUS SCORE CHECK
# ---------------------------------------------------------

print("\n[3] PREVIOUS SCORE CHECK")
print("-" * 70)

df = df.sort_values(
    GROUP_COLS + ["assessment_day", "assessment_id"]
).reset_index(drop=True)

# Previous assessment day
previous_day = (
    df.groupby(GROUP_COLS)["assessment_day"]
      .shift(1)
)

# IMPORTANT:
# Same-day assessments are NOT valid previous assessments.
same_day_previous = (
    previous_day.notna()
    & (previous_day >= df["assessment_day"])
)

print(
    "Rows where previous row is same/later day:",
    same_day_previous.sum()
)

# ---------------------------------------------------------
# 4. DAYS CHECK
# ---------------------------------------------------------

print("\n[4] DAYS SINCE PREVIOUS ASSESSMENT")
print("-" * 70)

print(
    "Negative:",
    (df["days_since_previous_assessment"] < 0).sum()
)

print(
    "Zero:",
    (df["days_since_previous_assessment"] == 0).sum()
)

print(
    "Minimum:",
    df["days_since_previous_assessment"].min()
)

# ---------------------------------------------------------
# 5. SCORE RANGE
# ---------------------------------------------------------

print("\n[5] SCORE RANGE")
print("-" * 70)

print(
    "Previous score:",
    df["previous_score"].min(),
    "-",
    df["previous_score"].max()
)

print(
    "Target:",
    df["target"].min(),
    "-",
    df["target"].max()
)

# ---------------------------------------------------------
# 6. CORRELATIONS
# ---------------------------------------------------------

print("\n[6] CORRELATIONS")
print("-" * 70)

numeric_columns = [
    "target",
    "previous_average_score",
    "previous_score",
    "active_days_30d",
    "vle_clicks_30d",
    "active_days_7d",
    "unique_materials_30d",
    "score_trend",
    "unique_materials_7d",
    "vle_clicks_7d",
    "days_since_previous_assessment",
    "previous_score_count",
    "assessment_weight",
]

print(
    df[numeric_columns]
      .corr()["target"]
      .sort_values(ascending=False)
)

# ---------------------------------------------------------
# FINAL
# ---------------------------------------------------------

print("\n" + "=" * 70)

negative_days = (
    df["days_since_previous_assessment"] < 0
).sum()

zero_days = (
    df["days_since_previous_assessment"] == 0
).sum()

if negative_days == 0 and zero_days == 0:
    print("TEMPORAL CHECK PASSED")
    print("=" * 70)
else:
    print("TEMPORAL CHECK FOUND ISSUES")
    print("=" * 70)
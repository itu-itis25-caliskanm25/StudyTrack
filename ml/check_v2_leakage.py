import pandas as pd
import numpy as np


FILE = "oulad_studytrack_dataset_v2.csv"


print("=" * 70)
print("STUDYTRACK OULAD V2 - LEAKAGE CHECK")
print("=" * 70)


# ============================================================
# 1. LOAD
# ============================================================

df = pd.read_csv(FILE)

print("\nDataset:")
print(df.shape)


# ============================================================
# 2. BASIC CHECKS
# ============================================================

print("\n[1] BASIC CHECKS")
print("-" * 70)

print(
    "Missing values:",
    df.isna().sum().sum()
)

print(
    "Duplicate rows:",
    df.duplicated().sum()
)

print(
    "Duplicate student + assessment:",
    df.duplicated(
        subset=[
            "student_id",
            "assessment_id"
        ]
    ).sum()
)


# ============================================================
# 3. SAME-DAY ASSESSMENTS
# ============================================================

print("\n[2] SAME-DAY ASSESSMENTS")
print("-" * 70)

same_day = (
    df
    .groupby(
        [
            "student_id",
            "code_module",
            "code_presentation",
            "assessment_day",
        ]
    )
    .size()
)

print(
    "Groups containing multiple "
    "assessments:",
    (same_day > 1).sum()
)

print(
    "Rows belonging to those groups:",
    same_day[
        same_day > 1
    ].sum()
)


# ============================================================
# 4. PREVIOUS SCORE CONSISTENCY
# ============================================================

print("\n[3] PREVIOUS SCORE CONSISTENCY")
print("-" * 70)

# Sort chronologically

df = df.sort_values(
    [
        "student_id",
        "code_module",
        "code_presentation",
        "assessment_day",
        "assessment_id",
    ]
)


# For each student/presentation,
# calculate the immediately previous
# assessment date.

df["previous_date_check"] = (
    df
    .groupby(
        [
            "student_id",
            "code_module",
            "code_presentation"
        ]
    )["assessment_day"]
    .shift(1)
)


# We only want previous_score to exist
# when there is an assessment on an
# EARLIER day.

invalid_previous = (
    df["previous_score"].notna()
    &
    df["previous_date_check"].notna()
    &
    (
        df["previous_date_check"]
        >= df["assessment_day"]
    )
)


print(
    "Potential same-day leakage rows:",
    invalid_previous.sum()
)


if invalid_previous.sum() > 0:

    print("\nExamples:")

    print(
        df.loc[
            invalid_previous,
            [
                "student_id",
                "code_module",
                "code_presentation",
                "assessment_id",
                "assessment_day",
                "previous_score",
                "target",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )


# ============================================================
# 5. DAYS SINCE PREVIOUS ASSESSMENT
# ============================================================

print("\n[4] DAYS SINCE PREVIOUS ASSESSMENT")
print("-" * 70)

invalid_days = (
    df["days_since_previous_assessment"].notna()
    &
    (
        df["days_since_previous_assessment"] < 0
    )
)

print(
    "Negative day differences:",
    invalid_days.sum()
)

print(
    "Zero day differences:",
    (
        df["days_since_previous_assessment"]
        == 0
    ).sum()
)


# ============================================================
# 6. SCORE RANGE
# ============================================================

print("\n[5] SCORE RANGE")
print("-" * 70)

print(
    "Previous score min:",
    df["previous_score"].min()
)

print(
    "Previous score max:",
    df["previous_score"].max()
)

print(
    "Target min:",
    df["target"].min()
)

print(
    "Target max:",
    df["target"].max()
)


# ============================================================
# 7. VLE RANGE
# ============================================================

print("\n[6] VLE FEATURES")
print("-" * 70)

vle_features = [
    "vle_clicks_7d",
    "vle_clicks_30d",
    "active_days_7d",
    "active_days_30d",
    "unique_materials_7d",
    "unique_materials_30d",
]

for feature in vle_features:

    print(
        f"{feature:30s}",
        f"min={df[feature].min():.0f}",
        f"max={df[feature].max():.0f}",
    )


# ============================================================
# 8. TEMPORAL SANITY
# ============================================================

print("\n[7] TEMPORAL SANITY")
print("-" * 70)

print(
    "Assessment day min:",
    df["assessment_day"].min()
)

print(
    "Assessment day max:",
    df["assessment_day"].max()
)

print(
    "Days since previous min:",
    df["days_since_previous_assessment"].min()
)

print(
    "Days since previous max:",
    df["days_since_previous_assessment"].max()
)


# ============================================================
# 9. FEATURE / TARGET CORRELATION
# ============================================================

print("\n[8] CORRELATIONS")
print("-" * 70)

numeric_features = [
    "vle_clicks_7d",
    "vle_clicks_30d",
    "active_days_7d",
    "active_days_30d",
    "unique_materials_7d",
    "unique_materials_30d",
    "previous_score",
    "previous_average_score",
    "previous_score_count",
    "score_trend",
    "days_since_previous_assessment",
    "assessment_weight",
    "target",
]

correlations = (
    df[numeric_features]
    .corr()["target"]
    .sort_values(
        ascending=False
    )
)

print(
    correlations.round(4)
)


# ============================================================
# 10. FINAL RESULT
# ============================================================

print("\n" + "=" * 70)

if (
    df.isna().sum().sum() == 0
    and
    df.duplicated().sum() == 0
    and
    df.duplicated(
        subset=[
            "student_id",
            "assessment_id"
        ]
    ).sum() == 0
    and
    invalid_previous.sum() == 0
    and
    invalid_days.sum() == 0
):

    print("LEAKAGE CHECK PASSED")

else:

    print("LEAKAGE CHECK FOUND POTENTIAL ISSUES")

print("=" * 70)
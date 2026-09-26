import pandas as pd
import numpy as np


FILE = "oulad_studytrack_dataset.csv"

df = pd.read_csv(FILE)


print("=" * 70)
print("OULAD DEEP VALIDATION")
print("=" * 70)


# ============================================================
# 1. BASIC INFORMATION
# ============================================================

print("\n[1] BASIC INFORMATION")
print("-" * 70)

print("Shape:")
print(df.shape)

print("\nData types:")
print(df.dtypes)

print("\nUnique students:")
print(df["student_id"].nunique())

print("Unique assessments:")
print(df["assessment_id"].nunique())

print("Unique modules:")
print(df["code_module"].nunique())

print("Unique presentations:")
print(df["code_presentation"].nunique())


# ============================================================
# 2. ASSESSMENT TYPES
# ============================================================

print("\n[2] ASSESSMENT TYPES")
print("-" * 70)

print(
    df["assessment_type"]
    .value_counts()
)

print("\nPercentages:")
print(
    df["assessment_type"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ============================================================
# 3. TARGET DISTRIBUTION
# ============================================================

print("\n[3] TARGET DISTRIBUTION")
print("-" * 70)

print(
    df["target"]
    .describe()
    .round(2)
)

print("\nTarget by assessment type:")

target_by_type = (
    df
    .groupby("assessment_type")["target"]
    .agg(
        count="count",
        mean="mean",
        std="std",
        min="min",
        median="median",
        max="max",
    )
    .round(2)
)

print(target_by_type)


# ============================================================
# 4. ZERO SCORES
# ============================================================

print("\n[4] ZERO SCORES")
print("-" * 70)

zero_scores = df["target"] == 0

print(
    f"Total zero scores: {zero_scores.sum():,}"
)

print(
    f"Percentage: {zero_scores.mean() * 100:.3f}%"
)

print("\nZero scores by assessment type:")

print(
    df.loc[
        zero_scores,
        "assessment_type"
    ].value_counts()
)


# ============================================================
# 5. MISSING VALUES
# ============================================================

print("\n[5] MISSING VALUES")
print("-" * 70)

missing = (
    df
    .isna()
    .sum()
    .sort_values(ascending=False)
)

missing = missing[missing > 0]

if len(missing) == 0:
    print("No missing values.")
else:
    print(missing)

print("\nRows with missing assessment_day:")

missing_day = df["assessment_day"].isna()

print(
    f"Count: {missing_day.sum():,}"
)

if missing_day.sum() > 0:

    print("\nBy assessment type:")

    print(
        df.loc[
            missing_day,
            "assessment_type"
        ].value_counts()
    )

    print("\nTarget statistics:")

    print(
        df.loc[
            missing_day,
            "target"
        ].describe()
        .round(2)
    )


# ============================================================
# 6. DUPLICATES
# ============================================================

print("\n[6] DUPLICATES")
print("-" * 70)

duplicate_student_assessment = df.duplicated(
    subset=[
        "student_id",
        "assessment_id"
    ]
).sum()

print(
    "Duplicate student + assessment:",
    duplicate_student_assessment
)

duplicate_student_day = df.duplicated(
    subset=[
        "student_id",
        "code_module",
        "code_presentation",
        "assessment_day"
    ],
    keep=False
)

print(
    "Rows sharing same student + presentation + day:",
    duplicate_student_day.sum()
)


# ============================================================
# 7. SAME-DAY ASSESSMENTS
# ============================================================

print("\n[7] SAME-DAY ASSESSMENTS")
print("-" * 70)

same_day = (
    df
    .dropna(subset=["assessment_day"])
    .groupby(
        [
            "student_id",
            "code_module",
            "code_presentation",
            "assessment_day"
        ]
    )
    .size()
)

same_day_multiple = same_day[same_day > 1]

print(
    "Student/presentation/day groups:",
    len(same_day)
)

print(
    "Groups with multiple assessments:",
    len(same_day_multiple)
)

if len(same_day_multiple) > 0:

    print("\nNumber of assessments in those groups:")

    print(
        same_day_multiple
        .value_counts()
        .sort_index()
    )


# ============================================================
# 8. ASSESSMENTS PER STUDENT
# ============================================================

print("\n[8] ASSESSMENTS PER STUDENT")
print("-" * 70)

student_counts = (
    df
    .groupby("student_id")
    .size()
)

print(
    student_counts
    .describe()
    .round(2)
)

print("\nDistribution:")

print(
    student_counts
    .value_counts()
    .sort_index()
    .head(30)
)


# ============================================================
# 9. ASSESSMENTS PER STUDENT + PRESENTATION
# ============================================================

print("\n[9] ASSESSMENTS PER STUDENT/PRESENTATION")
print("-" * 70)

student_presentation_counts = (
    df
    .groupby(
        [
            "student_id",
            "code_module",
            "code_presentation"
        ]
    )
    .size()
)

print(
    student_presentation_counts
    .describe()
    .round(2)
)


# ============================================================
# 10. ASSESSMENT WEIGHT
# ============================================================

print("\n[10] ASSESSMENT WEIGHT")
print("-" * 70)

print(
    df["assessment_weight"]
    .describe()
    .round(2)
)

print("\nWeight by assessment type:")

print(
    df
    .groupby("assessment_type")["assessment_weight"]
    .agg(
        count="count",
        mean="mean",
        min="min",
        median="median",
        max="max",
    )
    .round(2)
)


# ============================================================
# 11. VLE FEATURES
# ============================================================

print("\n[11] VLE FEATURES")
print("-" * 70)

vle_features = [
    "vle_clicks_7d",
    "vle_clicks_30d",
    "active_days_7d",
    "active_days_30d",
    "unique_materials_7d",
    "unique_materials_30d",
]

print(
    df[vle_features]
    .describe()
    .round(2)
)


# ============================================================
# 12. OUTLIERS / EXTREME VALUES
# ============================================================

print("\n[12] EXTREME VALUES")
print("-" * 70)

for feature in vle_features:

    print(f"\n{feature}")

    print("Top 10 values:")

    print(
        df[feature]
        .nlargest(10)
        .tolist()
    )


# ============================================================
# 13. CORRELATIONS
# ============================================================

print("\n[13] CORRELATIONS WITH TARGET")
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
    correlations
    .round(4)
)


# ============================================================
# 14. CORRELATIONS BY ASSESSMENT TYPE
# ============================================================

print("\n[14] CORRELATIONS BY ASSESSMENT TYPE")
print("-" * 70)

for assessment_type in sorted(
    df["assessment_type"].dropna().unique()
):

    print(
        f"\n--- {assessment_type} ---"
    )

    subset = df[
        df["assessment_type"]
        == assessment_type
    ]

    correlations = (
        subset[numeric_features]
        .corr()["target"]
        .sort_values(
            ascending=False
        )
    )

    print(
        correlations
        .round(4)
    )


# ============================================================
# 15. PREVIOUS SCORE RELATIONSHIP
# ============================================================

print("\n[15] PREVIOUS SCORE RELATIONSHIP")
print("-" * 70)

print(
    df[
        [
            "previous_score",
            "previous_average_score",
            "target"
        ]
    ]
    .describe()
    .round(2)
)

print("\nPrevious score buckets:")

score_bins = [
    -1,
    40,
    50,
    60,
    70,
    80,
    90,
    100
]

score_labels = [
    "0-40",
    "41-50",
    "51-60",
    "61-70",
    "71-80",
    "81-90",
    "91-100"
]

df["previous_score_bucket"] = pd.cut(
    df["previous_score"],
    bins=score_bins,
    labels=score_labels
)

print(
    df
    .groupby(
        "previous_score_bucket",
        observed=True
    )["target"]
    .agg(
        count="count",
        mean="mean",
        median="median"
    )
    .round(2)
)


# ============================================================
# 16. STUDY ACTIVITY BUCKETS
# ============================================================

print("\n[16] STUDY ACTIVITY BUCKETS")
print("-" * 70)

df["activity_30d_bucket"] = pd.cut(
    df["active_days_30d"],
    bins=[
        -1,
        0,
        3,
        7,
        14,
        21,
        30
    ],
    labels=[
        "0",
        "1-3",
        "4-7",
        "8-14",
        "15-21",
        "22-30"
    ]
)

print(
    df
    .groupby(
        "activity_30d_bucket",
        observed=True
    )["target"]
    .agg(
        count="count",
        mean="mean",
        median="median"
    )
    .round(2)
)


# ============================================================
# 17. DAYS SINCE PREVIOUS ASSESSMENT
# ============================================================

print("\n[17] DAYS SINCE PREVIOUS ASSESSMENT")
print("-" * 70)

print(
    df["days_since_previous_assessment"]
    .describe()
    .round(2)
)

print("\nLargest gaps:")

print(
    df["days_since_previous_assessment"]
    .nlargest(20)
    .tolist()
)


# ============================================================
# 18. ASSESSMENT DAY DISTRIBUTION
# ============================================================

print("\n[18] ASSESSMENT DAY")
print("-" * 70)

print(
    df["assessment_day"]
    .describe()
    .round(2)
)

print("\nAssessment day by type:")

print(
    df
    .groupby("assessment_type")["assessment_day"]
    .agg(
        min="min",
        median="median",
        max="max"
    )
    .round(2)
)


# ============================================================
# 19. PRESENTATION DISTRIBUTION
# ============================================================

print("\n[19] COURSE PRESENTATIONS")
print("-" * 70)

presentation_counts = (
    df
    .groupby(
        [
            "code_module",
            "code_presentation"
        ]
    )
    .size()
    .sort_values(
        ascending=False
    )
)

print(
    presentation_counts
)


# ============================================================
# 20. TEMPORAL ORDER CHECK
# ============================================================

print("\n[20] TEMPORAL ORDER CHECK")
print("-" * 70)

ordered = (
    df
    .dropna(
        subset=[
            "assessment_day"
        ]
    )
    .sort_values(
        [
            "student_id",
            "code_module",
            "code_presentation",
            "assessment_day"
        ]
    )
)

ordered["previous_day_check"] = (
    ordered
    .groupby(
        [
            "student_id",
            "code_module",
            "code_presentation"
        ]
    )["assessment_day"]
    .shift(1)
)

same_or_backwards = (
    ordered["assessment_day"]
    <= ordered["previous_day_check"]
)

same_or_backwards = (
    same_or_backwards
    .fillna(False)
)

print(
    "Rows where assessment_day does not increase:",
    same_or_backwards.sum()
)

if same_or_backwards.sum() > 0:

    print("\nExamples:")

    print(
        ordered.loc[
            same_or_backwards,
            [
                "student_id",
                "code_module",
                "code_presentation",
                "assessment_id",
                "assessment_day",
                "target"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )


# ============================================================
# 21. FEATURE RANGE CHECK
# ============================================================

print("\n[21] FEATURE RANGE CHECK")
print("-" * 70)

for feature in numeric_features:

    print(
        f"{feature:35s}",
        f"min={df[feature].min():.2f}",
        f"max={df[feature].max():.2f}"
    )


# ============================================================
# 22. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("DEEP VALIDATION COMPLETE")
print("=" * 70)

print("\nImportant numbers:")

print(
    f"Rows                  : {len(df):,}"
)

print(
    f"Students              : {df['student_id'].nunique():,}"
)

print(
    f"Assessments           : {df['assessment_id'].nunique():,}"
)

print(
    f"Zero scores           : {zero_scores.sum():,}"
)

print(
    f"Missing assessment day: {missing_day.sum():,}"
)

print(
    f"Same-day groups       : {len(same_day_multiple):,}"
)

print(
    f"Duplicate rows        : {duplicate_student_assessment:,}"
)

print("\nDone.")
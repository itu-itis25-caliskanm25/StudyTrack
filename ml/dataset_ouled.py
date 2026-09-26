import pandas as pd
import numpy as np
from pathlib import Path


DATA_DIR = Path("data/oulad")
OUTPUT_FILE = Path("oulad_studytrack_dataset_v2.csv")


print("=" * 70)
print("BUILDING OULAD STUDYTRACK DATASET V2")
print("=" * 70)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\nLoading OULAD data...")

assessments = pd.read_csv(
    DATA_DIR / "assessments.csv"
)

student_assessment = pd.read_csv(
    DATA_DIR / "studentAssessment.csv"
)

student_vle = pd.read_csv(
    DATA_DIR / "studentVle.csv"
)

print(
    f"Assessments       : {len(assessments):,}"
)

print(
    f"StudentAssessment : {len(student_assessment):,}"
)

print(
    f"StudentVle        : {len(student_vle):,}"
)


# ============================================================
# 2. PREPARE ASSESSMENT DATA
# ============================================================

print("\nPreparing assessment data...")

assessment_results = student_assessment.merge(
    assessments,
    on="id_assessment",
    how="inner"
)


assessment_results = assessment_results.dropna(
    subset=["score"]
)


assessment_results["date"] = pd.to_numeric(
    assessment_results["date"],
    errors="coerce"
)


assessment_results["date_submitted"] = pd.to_numeric(
    assessment_results["date_submitted"],
    errors="coerce"
)


# Keep latest submission for each student/assessment
assessment_results = (
    assessment_results
    .sort_values(
        [
            "id_student",
            "id_assessment",
            "date_submitted"
        ]
    )
    .drop_duplicates(
        subset=[
            "id_student",
            "id_assessment"
        ],
        keep="last"
    )
)


print(
    f"Valid assessment results: "
    f"{len(assessment_results):,}"
)


# ============================================================
# 3. REMOVE ASSESSMENTS WITHOUT A KNOWN DATE
# ============================================================

missing_assessment_date = (
    assessment_results["date"].isna()
)

print(
    "\nAssessment results without "
    "assessment date:"
)

print(
    f"{missing_assessment_date.sum():,}"
)

print("\nBy assessment type:")

print(
    assessment_results.loc[
        missing_assessment_date,
        "assessment_type"
    ].value_counts()
)


# We need a known assessment day because
# all temporal features depend on it.

assessment_results = assessment_results[
    ~missing_assessment_date
].copy()


print(
    "\nAssessment results after removing "
    "unknown-date assessments:"
)

print(
    f"{len(assessment_results):,}"
)


# ============================================================
# 4. PREPARE VLE DATA
# ============================================================

print("\nPreparing VLE data...")

vle = student_vle[
    [
        "code_module",
        "code_presentation",
        "id_student",
        "id_site",
        "date",
        "sum_click",
    ]
].copy()


vle["date"] = pd.to_numeric(
    vle["date"],
    errors="coerce"
)


vle["sum_click"] = pd.to_numeric(
    vle["sum_click"],
    errors="coerce"
)


vle = vle.dropna(
    subset=[
        "code_module",
        "code_presentation",
        "id_student",
        "id_site",
        "date",
        "sum_click",
    ]
)


print(
    f"Valid VLE rows: {len(vle):,}"
)


# ============================================================
# 5. DAILY VLE AGGREGATION
# ============================================================

print("\nAggregating VLE activity by student/day...")

daily_vle = (
    vle
    .groupby(
        [
            "code_module",
            "code_presentation",
            "id_student",
            "date",
        ],
        as_index=False
    )
    .agg(
        daily_clicks=(
            "sum_click",
            "sum"
        ),

        daily_unique_materials=(
            "id_site",
            "nunique"
        ),
    )
)


print(
    f"Daily VLE rows: {len(daily_vle):,}"
)


# ============================================================
# 6. GROUP VLE DATA
# ============================================================

print("\nGrouping VLE data...")

vle_groups = {
    key: group.sort_values("date")
    for key, group in daily_vle.groupby(
        [
            "id_student",
            "code_module",
            "code_presentation",
        ]
    )
}


# ============================================================
# 7. VLE FEATURE CALCULATION
# ============================================================

def calculate_vle_features(
    student_vle_data,
    assessment_day
):

    previous = student_vle_data[
        student_vle_data["date"] < assessment_day
    ]

    if previous.empty:

        return {
            "vle_clicks_7d": 0,
            "vle_clicks_30d": 0,
            "active_days_7d": 0,
            "active_days_30d": 0,
            "unique_materials_7d": 0,
            "unique_materials_30d": 0,
        }


    last_7 = previous[
        previous["date"] >= assessment_day - 7
    ]

    last_30 = previous[
        previous["date"] >= assessment_day - 30
    ]


    # --------------------------------------------------------
    # Click features
    # --------------------------------------------------------

    vle_clicks_7d = last_7[
        "daily_clicks"
    ].sum()

    vle_clicks_30d = last_30[
        "daily_clicks"
    ].sum()


    # --------------------------------------------------------
    # Active day features
    # --------------------------------------------------------

    active_days_7d = last_7[
        "date"
    ].nunique()

    active_days_30d = last_30[
        "date"
    ].nunique()


    # --------------------------------------------------------
    # True unique material counts
    # --------------------------------------------------------
    #
    # We go back to the original VLE rows for these.
    #
    # This function will receive the original student
    # VLE records separately.
    #

    return {
        "vle_clicks_7d": vle_clicks_7d,
        "vle_clicks_30d": vle_clicks_30d,
        "active_days_7d": active_days_7d,
        "active_days_30d": active_days_30d,
    }


# ============================================================
# 8. ORIGINAL VLE GROUPS FOR UNIQUE MATERIALS
# ============================================================

print("\nPreparing original VLE groups...")

original_vle_groups = {
    key: group.sort_values("date")
    for key, group in vle.groupby(
        [
            "id_student",
            "code_module",
            "code_presentation",
        ]
    )
}


def calculate_unique_materials(
    student_vle_data,
    assessment_day
):

    previous = student_vle_data[
        student_vle_data["date"] < assessment_day
    ]

    if previous.empty:
        return 0, 0


    last_7 = previous[
        previous["date"] >= assessment_day - 7
    ]

    last_30 = previous[
        previous["date"] >= assessment_day - 30
    ]


    unique_7d = last_7[
        "id_site"
    ].nunique()

    unique_30d = last_30[
        "id_site"
    ].nunique()


    return unique_7d, unique_30d


# ============================================================
# 9. SORT ASSESSMENTS
# ============================================================

print("\nSorting assessments chronologically...")

assessment_results = assessment_results.sort_values(
    [
        "id_student",
        "code_module",
        "code_presentation",
        "date",
        "id_assessment",
    ]
)


# ============================================================
# 10. BUILD DATASET
# ============================================================

print("\nBuilding StudyTrack dataset...")

rows = []


grouped_assessments = assessment_results.groupby(
    [
        "id_student",
        "code_module",
        "code_presentation",
    ]
)


for student_key, group in grouped_assessments:

    student_id, module, presentation = student_key

    group = group.sort_values(
        [
            "date",
            "id_assessment"
        ]
    )


    student_vle_data = vle_groups.get(
        student_key
    )

    original_student_vle_data = (
        original_vle_groups.get(
            student_key
        )
    )


    # --------------------------------------------------------
    # Process each assessment
    # --------------------------------------------------------

    for _, row in group.iterrows():

        assessment_day = row["date"]

        target = row["score"]


        # ----------------------------------------------------
        # VLE features
        # ----------------------------------------------------

        if student_vle_data is not None:

            vle_features = calculate_vle_features(
                student_vle_data,
                assessment_day
            )

        else:

            vle_features = {
                "vle_clicks_7d": 0,
                "vle_clicks_30d": 0,
                "active_days_7d": 0,
                "active_days_30d": 0,
            }


        # ----------------------------------------------------
        # True unique materials
        # ----------------------------------------------------

        if original_student_vle_data is not None:

            (
                unique_materials_7d,
                unique_materials_30d
            ) = calculate_unique_materials(
                original_student_vle_data,
                assessment_day
            )

        else:

            unique_materials_7d = 0
            unique_materials_30d = 0


        # ----------------------------------------------------
        # Previous assessment history
        #
        # IMPORTANT:
        #
        # Only assessments with
        #
        # previous_date < assessment_day
        #
        # are allowed.
        #
        # Same-day assessment scores are NOT included.
        # ----------------------------------------------------

        previous = group[
            group["date"] < assessment_day
        ]


        if previous.empty:

            previous_score = np.nan

            previous_average_score = np.nan

            previous_score_count = 0

            score_trend = 0.0

            days_since_previous_assessment = np.nan

        else:

            previous_scores = (
                previous["score"]
                .astype(float)
                .tolist()
            )


            previous_score = (
                previous_scores[-1]
            )


            previous_average_score = (
                np.mean(
                    previous_scores
                )
            )


            previous_score_count = (
                len(previous_scores)
            )


            recent_scores = (
                previous_scores[-5:]
            )


            if len(recent_scores) >= 2:

                x = np.arange(
                    len(recent_scores)
                )

                y = np.array(
                    recent_scores
                )


                score_trend = np.polyfit(
                    x,
                    y,
                    1
                )[0]

            else:

                score_trend = 0.0


            previous_date = (
                previous["date"]
                .iloc[-1]
            )


            days_since_previous_assessment = (
                assessment_day
                - previous_date
            )


        # ----------------------------------------------------
        # Add row
        # ----------------------------------------------------

        rows.append(
            {
                "student_id": student_id,

                "code_module": module,

                "code_presentation": presentation,

                "assessment_id": row[
                    "id_assessment"
                ],

                "assessment_type": row[
                    "assessment_type"
                ],

                "assessment_day": assessment_day,

                "assessment_weight": row[
                    "weight"
                ],

                "vle_clicks_7d":
                    vle_features[
                        "vle_clicks_7d"
                    ],

                "vle_clicks_30d":
                    vle_features[
                        "vle_clicks_30d"
                    ],

                "active_days_7d":
                    vle_features[
                        "active_days_7d"
                    ],

                "active_days_30d":
                    vle_features[
                        "active_days_30d"
                    ],

                "unique_materials_7d":
                    unique_materials_7d,

                "unique_materials_30d":
                    unique_materials_30d,

                "previous_score":
                    previous_score,

                "previous_average_score":
                    previous_average_score,

                "previous_score_count":
                    previous_score_count,

                "score_trend":
                    score_trend,

                "days_since_previous_assessment":
                    days_since_previous_assessment,

                "target":
                    target,
            }
        )


# ============================================================
# 11. CREATE DATAFRAME
# ============================================================

print("\nCreating final dataframe...")

dataset = pd.DataFrame(rows)


# ============================================================
# 12. CLEAN DATA
# ============================================================

dataset = dataset.replace(
    [
        np.inf,
        -np.inf
    ],
    np.nan
)


dataset = dataset[
    (dataset["target"] >= 0)
    &
    (dataset["target"] <= 100)
]


# We need previous performance for the
# first version of our prediction model.

dataset = dataset.dropna(
    subset=[
        "previous_score",
        "previous_average_score",
    ]
)


# ============================================================
# 13. SORT FINAL DATASET
# ============================================================

dataset = dataset.sort_values(
    [
        "code_module",
        "code_presentation",
        "student_id",
        "assessment_day",
        "assessment_id",
    ]
)


# ============================================================
# 14. SAVE
# ============================================================

dataset.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 15. SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("STUDYTRACK OULAD DATASET V2")
print("=" * 70)

print(
    f"Rows    : {len(dataset):,}"
)

print(
    f"Columns : {len(dataset.columns)}"
)


print("\nAssessment types:")

print(
    dataset[
        "assessment_type"
    ].value_counts()
)


print("\nTarget statistics:")

print(
    dataset[
        "target"
    ]
    .describe()
    .round(2)
)


print("\nMissing values:")

missing = (
    dataset
    .isna()
    .sum()
)

print(
    missing[
        missing > 0
    ]
)


print("\nSame-day assessment check:")

same_day = (
    dataset
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
    f"Groups with multiple "
    f"assessments: "
    f"{(same_day > 1).sum():,}"
)


print("\nOutput:")

print(
    OUTPUT_FILE
)


print("\nDone!")
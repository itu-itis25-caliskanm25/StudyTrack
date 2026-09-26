import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

from sklearn.linear_model import Ridge
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


# ============================================================
# CONFIG
# ============================================================

DATA_PATH = "oulad_studytrack_dataset_v2.csv"

RANDOM_STATE = 42


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("STUDYTRACK - DAY BASED TEMPORAL VALIDATION")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

print(f"\nDataset: {df.shape}")


# ============================================================
# FEATURES
# ============================================================

performance_features = [
    "previous_score",
    "previous_average_score",
    "score_trend",
    "previous_score_count",
]

behavior_features = [
    "vle_clicks_7d",
    "vle_clicks_30d",
    "active_days_7d",
    "active_days_30d",
    "unique_materials_7d",
    "unique_materials_30d",
]

assessment_features = [
    "assessment_weight",
    "assessment_day",
    "days_since_previous_assessment",
]

categorical_features = [
    "assessment_type",
    "code_module",
]

features = (
    performance_features
    + behavior_features
    + assessment_features
    + categorical_features
)

target = "target"


# ============================================================
# SORT
# ============================================================

df = df.sort_values(
    [
        "student_id",
        "code_module",
        "code_presentation",
        "assessment_day",
        "assessment_id",
    ]
).reset_index(drop=True)


# ============================================================
# DAY-BASED TEMPORAL SPLIT
# ============================================================

train_parts = []
test_parts = []

group_columns = [
    "student_id",
    "code_module",
    "code_presentation",
]


for _, group in df.groupby(
    group_columns,
    sort=False
):

    unique_days = (
        group["assessment_day"]
        .dropna()
        .sort_values()
        .unique()
    )

    n_days = len(unique_days)

    if n_days < 2:
        train_parts.append(group)
        continue

    split_index = int(
        np.ceil(n_days * 0.8)
    )

    train_days = unique_days[:split_index]
    test_days = unique_days[split_index:]

    train_group = group[
        group["assessment_day"].isin(train_days)
    ]

    test_group = group[
        group["assessment_day"].isin(test_days)
    ]

    if len(train_group) > 0:
        train_parts.append(train_group)

    if len(test_group) > 0:
        test_parts.append(test_group)


train_df = pd.concat(
    train_parts
).reset_index(drop=True)

test_df = pd.concat(
    test_parts
).reset_index(drop=True)


# ============================================================
# SPLIT SUMMARY
# ============================================================

print("\nTemporal split:")
print(f"Train rows: {train_df.shape}")
print(f"Test rows : {test_df.shape}")

print(
    f"Train students: "
    f"{train_df['student_id'].nunique()}"
)

print(
    f"Test students : "
    f"{test_df['student_id'].nunique()}"
)


# ============================================================
# SAME-DAY LEAKAGE CHECK
# ============================================================

train_keys = set(
    zip(
        train_df["student_id"],
        train_df["code_module"],
        train_df["code_presentation"],
        train_df["assessment_day"],
    )
)

test_keys = set(
    zip(
        test_df["student_id"],
        test_df["code_module"],
        test_df["code_presentation"],
        test_df["assessment_day"],
    )
)

day_overlap = train_keys.intersection(
    test_keys
)

print(
    f"\nTrain/Test same-day groups: "
    f"{len(day_overlap)}"
)

if len(day_overlap) != 0:
    raise ValueError(
        "ERROR: Same assessment day exists in both train and test!"
    )

print("Same-day temporal check passed.")


# ============================================================
# DATA
# ============================================================

X_train = train_df[features]
y_train = train_df[target]

X_test = test_df[features]
y_test = test_df[target]


# ============================================================
# PREPROCESSOR
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False,
            ),
            categorical_features,
        ),
    ],
    remainder="passthrough",
)


# ============================================================
# MODELS
# ============================================================

models = {

    "Ridge": Ridge(
        alpha=10
    ),

    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=5,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        min_samples_leaf=5,
        random_state=RANDOM_STATE,
    ),
}


# ============================================================
# BASELINE
# ============================================================

baseline_predictions = test_df[
    "previous_average_score"
].values

baseline_predictions = np.clip(
    baseline_predictions,
    0,
    100
)

baseline_mae = mean_absolute_error(
    y_test,
    baseline_predictions
)

baseline_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        baseline_predictions
    )
)

baseline_r2 = r2_score(
    y_test,
    baseline_predictions
)


results = [
    {
        "model": "Previous Average",
        "mae": baseline_mae,
        "rmse": baseline_rmse,
        "r2": baseline_r2,
    }
]


print("\n" + "=" * 70)
print("BASELINE")
print("=" * 70)

print(
    f"MAE  = {baseline_mae:.3f}"
)

print(
    f"RMSE = {baseline_rmse:.3f}"
)

print(
    f"R2   = {baseline_r2:.3f}"
)


# ============================================================
# TRAIN MODELS
# ============================================================

print("\n" + "=" * 70)
print("MODEL RESULTS")
print("=" * 70)


for name, model in models.items():

    print(
        f"\nTraining {name}..."
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                model
            ),
        ]
    )

    pipeline.fit(
        X_train,
        y_train
    )

    predictions = pipeline.predict(
        X_test
    )

    predictions = np.clip(
        predictions,
        0,
        100
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    results.append(
        {
            "model": name,
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
        }
    )

    print(
        f"{name:<20}"
        f"MAE={mae:.3f}  "
        f"RMSE={rmse:.3f}  "
        f"R2={r2:.3f}"
    )


# ============================================================
# RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(
    results
)

print("\n" + "=" * 70)
print("FINAL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# BEST MODEL BY MAE
# ============================================================

best_model = results_df.loc[
    results_df["mae"].idxmin()
]

print("\n" + "=" * 70)
print("LOWEST MAE")
print("=" * 70)

print(
    f"Model : {best_model['model']}"
)

print(
    f"MAE   : {best_model['mae']:.3f}"
)

print(
    f"RMSE  : {best_model['rmse']:.3f}"
)

print(
    f"R2    : {best_model['r2']:.3f}"
)


# ============================================================
# SAVE
# ============================================================

results_df.to_csv(
    "oulad_day_temporal_results.csv",
    index=False
)

print(
    "\nSaved:"
)

print(
    "  oulad_day_temporal_results.csv"
)

print("\n" + "=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)
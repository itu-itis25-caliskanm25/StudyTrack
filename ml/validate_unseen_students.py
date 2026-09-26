import pandas as pd
import numpy as np

from sklearn.model_selection import GroupShuffleSplit
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# CONFIG
# ============================================================

DATA_PATH = "oulad_studytrack_dataset_v2.csv"

RANDOM_STATE = 42


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("STUDYTRACK - UNSEEN STUDENT VALIDATION")
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
# GROUP SPLIT BY STUDENT
# ============================================================

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=RANDOM_STATE,
)

train_idx, test_idx = next(
    splitter.split(
        df,
        groups=df["student_id"]
    )
)

train_df = df.iloc[train_idx].copy()
test_df = df.iloc[test_idx].copy()


print("\nStudent split:")
print(f"Train rows: {train_df.shape}")
print(f"Test rows : {test_df.shape}")

print(
    f"Train students: {train_df['student_id'].nunique()}"
)

print(
    f"Test students : {test_df['student_id'].nunique()}"
)


# ============================================================
# VERIFY NO STUDENT OVERLAP
# ============================================================

train_students = set(train_df["student_id"])
test_students = set(test_df["student_id"])

overlap = train_students.intersection(test_students)

print(
    f"\nStudent overlap: {len(overlap)}"
)

if len(overlap) > 0:
    raise ValueError(
        "ERROR: Some students exist in both train and test!"
    )

print("No student overlap.")


# ============================================================
# PREPARE DATA
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
# MODEL
# ============================================================

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=12,
    min_samples_leaf=5,
    random_state=RANDOM_STATE,
    n_jobs=-1,
)


pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model),
    ]
)


# ============================================================
# TRAIN
# ============================================================

print("\nTraining Random Forest...")

pipeline.fit(
    X_train,
    y_train
)

print("Training complete.")


# ============================================================
# PREDICTION
# ============================================================

predictions = pipeline.predict(X_test)

predictions = np.clip(
    predictions,
    0,
    100
)


# ============================================================
# METRICS
# ============================================================

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


# ============================================================
# BASELINES
# ============================================================

previous_score_pred = test_df[
    "previous_score"
].values

previous_average_pred = test_df[
    "previous_average_score"
].values


previous_score_mae = mean_absolute_error(
    y_test,
    previous_score_pred
)

previous_average_mae = mean_absolute_error(
    y_test,
    previous_average_pred
)


# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 70)
print("UNSEEN STUDENT RESULTS")
print("=" * 70)

print(
    f"\nRandom Forest"
)

print(
    f"MAE  = {mae:.3f}"
)

print(
    f"RMSE = {rmse:.3f}"
)

print(
    f"R2   = {r2:.3f}"
)


print("\nBaselines")

print(
    f"Previous Score       MAE = "
    f"{previous_score_mae:.3f}"
)

print(
    f"Previous Average     MAE = "
    f"{previous_average_mae:.3f}"
)


# ============================================================
# TARGET / PREDICTION DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("PREDICTION DISTRIBUTION")
print("=" * 70)

print(
    f"\nActual mean : {y_test.mean():.2f}"
)

print(
    f"Pred mean   : {predictions.mean():.2f}"
)

print(
    f"Actual min  : {y_test.min():.2f}"
)

print(
    f"Actual max  : {y_test.max():.2f}"
)

print(
    f"Pred min    : {predictions.min():.2f}"
)

print(
    f"Pred max    : {predictions.max():.2f}"
)


# ============================================================
# ERROR BY SCORE RANGE
# ============================================================

results_df = pd.DataFrame(
    {
        "actual": y_test.values,
        "predicted": predictions,
    }
)

results_df["error"] = (
    results_df["predicted"]
    - results_df["actual"]
)

results_df["absolute_error"] = (
    results_df["error"].abs()
)


results_df["score_range"] = pd.cut(
    results_df["actual"],
    bins=[-1, 40, 60, 80, 100],
    labels=[
        "0-40",
        "41-60",
        "61-80",
        "81-100",
    ],
)


print("\n" + "=" * 70)
print("ERROR BY ACTUAL SCORE RANGE")
print("=" * 70)

bucket_results = (
    results_df
    .groupby(
        "score_range",
        observed=False
    )
    .agg(
        count=("actual", "size"),
        actual_mean=("actual", "mean"),
        predicted_mean=("predicted", "mean"),
        mae=("absolute_error", "mean"),
        bias=("error", "mean"),
    )
)

print(
    bucket_results.to_string()
)


# ============================================================
# SAVE RESULTS
# ============================================================

results_df.to_csv(
    "oulad_unseen_student_predictions.csv",
    index=False
)

print(
    "\nSaved:"
)

print(
    "  oulad_unseen_student_predictions.csv"
)


print("\n" + "=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)
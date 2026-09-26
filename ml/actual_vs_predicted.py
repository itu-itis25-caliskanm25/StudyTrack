import pandas as pd
import numpy as np

from sklearn.model_selection import GroupShuffleSplit
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import matplotlib.pyplot as plt


# ============================================================
# CONFIG
# ============================================================

DATA_PATH = "oulad_studytrack_dataset_v2.csv"

RANDOM_STATE = 42


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("STUDYTRACK - ACTUAL VS PREDICTED ANALYSIS")
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
# UNSEEN STUDENT SPLIT
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
print(f"Train rows: {len(train_df)}")
print(f"Test rows : {len(test_df)}")

print(
    f"Train students: "
    f"{train_df['student_id'].nunique()}"
)

print(
    f"Test students : "
    f"{test_df['student_id'].nunique()}"
)


# ============================================================
# PREPARE DATA
# ============================================================

X_train = train_df[features]
y_train = train_df[target]

X_test = test_df[features]
y_test = test_df[target]


# ============================================================
# PREPROCESSING
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
# RESULTS DATAFRAME
# ============================================================

results = test_df[
    [
        "student_id",
        "code_module",
        "code_presentation",
        "assessment_id",
        "assessment_type",
        "target",
        "previous_score",
        "previous_average_score",
        "vle_clicks_30d",
        "active_days_30d",
    ]
].copy()

results["predicted"] = predictions

results["error"] = (
    results["predicted"]
    - results["target"]
)

results["absolute_error"] = (
    results["error"].abs()
)


# ============================================================
# METRICS
# ============================================================

mae = mean_absolute_error(
    results["target"],
    results["predicted"]
)

rmse = np.sqrt(
    mean_squared_error(
        results["target"],
        results["predicted"]
    )
)

r2 = r2_score(
    results["target"],
    results["predicted"]
)


print("\n" + "=" * 70)
print("OVERALL PERFORMANCE")
print("=" * 70)

print(f"MAE  : {mae:.3f}")
print(f"RMSE : {rmse:.3f}")
print(f"R2   : {r2:.3f}")


# ============================================================
# ERROR BY SCORE RANGE
# ============================================================

results["score_range"] = pd.cut(
    results["target"],
    bins=[-1, 40, 60, 80, 100],
    labels=[
        "0-40",
        "41-60",
        "61-80",
        "81-100",
    ],
)


print("\n" + "=" * 70)
print("ERROR BY SCORE RANGE")
print("=" * 70)

bucket_results = (
    results
    .groupby(
        "score_range",
        observed=False
    )
    .agg(
        count=("target", "size"),
        actual_mean=("target", "mean"),
        predicted_mean=("predicted", "mean"),
        mae=("absolute_error", "mean"),
        bias=("error", "mean"),
    )
)

print(
    bucket_results.to_string()
)


# ============================================================
# ASSESSMENT TYPE
# ============================================================

print("\n" + "=" * 70)
print("PERFORMANCE BY ASSESSMENT TYPE")
print("=" * 70)

type_results = (
    results
    .groupby("assessment_type")
    .agg(
        count=("target", "size"),
        actual_mean=("target", "mean"),
        predicted_mean=("predicted", "mean"),
        mae=("absolute_error", "mean"),
        bias=("error", "mean"),
    )
)

print(
    type_results.to_string()
)


# ============================================================
# WORST PREDICTIONS
# ============================================================

print("\n" + "=" * 70)
print("20 WORST PREDICTIONS")
print("=" * 70)

worst = (
    results
    .sort_values(
        "absolute_error",
        ascending=False
    )
    .head(20)
)

print(
    worst[
        [
            "student_id",
            "assessment_type",
            "target",
            "predicted",
            "error",
            "previous_score",
            "previous_average_score",
            "vle_clicks_30d",
            "active_days_30d",
        ]
    ].to_string(index=False)
)


# ============================================================
# RESIDUAL STATISTICS
# ============================================================

print("\n" + "=" * 70)
print("RESIDUAL STATISTICS")
print("=" * 70)

print(
    results["error"].describe()
)


# ============================================================
# SAVE RESULTS
# ============================================================

results.to_csv(
    "oulad_actual_vs_predicted.csv",
    index=False
)

print(
    "\nSaved:"
)

print(
    "  oulad_actual_vs_predicted.csv"
)


# ============================================================
# PLOT 1 - ACTUAL VS PREDICTED
# ============================================================

plt.figure(figsize=(8, 8))

plt.scatter(
    results["target"],
    results["predicted"],
    alpha=0.25,
)

plt.plot(
    [0, 100],
    [0, 100],
    linestyle="--",
)

plt.xlabel("Actual Score")
plt.ylabel("Predicted Score")
plt.title("OULAD - Actual vs Predicted")

plt.xlim(0, 100)
plt.ylim(0, 100)

plt.tight_layout()

plt.savefig(
    "oulad_actual_vs_predicted.png",
    dpi=150,
)

plt.show()


# ============================================================
# PLOT 2 - RESIDUALS
# ============================================================

plt.figure(figsize=(9, 6))

plt.scatter(
    results["target"],
    results["error"],
    alpha=0.25,
)

plt.axhline(
    0,
    linestyle="--",
)

plt.xlabel("Actual Score")
plt.ylabel("Prediction Error")
plt.title("OULAD - Prediction Residuals")

plt.xlim(0, 100)

plt.tight_layout()

plt.savefig(
    "oulad_prediction_residuals.png",
    dpi=150,
)

plt.show()


print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
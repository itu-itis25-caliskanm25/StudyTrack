import pandas as pd
import numpy as np

from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# CONFIG
# ============================================================

DATA_PATH = "oulad_studytrack_dataset_v2.csv"

GROUP_COLS = [
    "student_id",
    "code_module",
    "code_presentation",
]


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("STUDYTRACK - OULAD MODEL TRAINING")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

print("\nDataset:", df.shape)


# ============================================================
# SORT TEMPORALLY
# ============================================================

df = df.sort_values(
    GROUP_COLS + ["assessment_day", "assessment_id"]
).reset_index(drop=True)


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


# ============================================================
# CATEGORICAL FEATURES
# ============================================================

categorical_features = [
    "assessment_type",
    "code_module",
]


# ============================================================
# TEMPORAL TRAIN / TEST SPLIT
# ============================================================
#
# For each student/module/presentation:
# - earliest 80% -> train
# - latest 20% -> test
#
# This prevents future assessments from entering training.
#
# ============================================================

df["row_number"] = (
    df.groupby(GROUP_COLS).cumcount()
)

df["group_size"] = (
    df.groupby(GROUP_COLS)["target"]
      .transform("size")
)

df["is_test"] = (
    df["row_number"]
    >=
    np.ceil(df["group_size"] * 0.8)
)

train_df = df[~df["is_test"]].copy()
test_df = df[df["is_test"]].copy()

print("\nTemporal split:")
print("Train:", train_df.shape)
print("Test :", test_df.shape)

print(
    "Train target mean:",
    round(train_df["target"].mean(), 2)
)

print(
    "Test target mean :",
    round(test_df["target"].mean(), 2)
)


# ============================================================
# ONE-HOT ENCODING
# ============================================================

def prepare_features(data, features):
    X = data[features].copy()

    X = pd.get_dummies(
        X,
        columns=[
            col
            for col in categorical_features
            if col in features
        ],
        dtype=float,
    )

    return X


# ============================================================
# ALIGN TRAIN / TEST COLUMNS
# ============================================================

def align_features(X_train, X_test):

    X_train, X_test = X_train.align(
        X_test,
        join="left",
        axis=1,
        fill_value=0,
    )

    X_test = X_test.fillna(0)
    X_train = X_train.fillna(0)

    return X_train, X_test


# ============================================================
# EVALUATION
# ============================================================

def evaluate_model(name, model, X_train, y_train, X_test, y_test):

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    # Scores cannot be outside 0-100.
    predictions = np.clip(
        predictions,
        0,
        100,
    )

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions,
        )
    )

    r2 = r2_score(
        y_test,
        predictions,
    )

    print(
        f"{name:25s}"
        f" MAE={mae:6.2f}"
        f" RMSE={rmse:6.2f}"
        f" R2={r2:6.3f}"
    )

    return {
        "model": name,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
    }


# ============================================================
# BASELINES
# ============================================================

print("\n" + "=" * 70)
print("BASELINES")
print("=" * 70)

y_train = train_df["target"]
y_test = test_df["target"]


# Previous score baseline
previous_score_predictions = test_df["previous_score"]

previous_score_mae = mean_absolute_error(
    y_test,
    previous_score_predictions,
)

previous_score_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        previous_score_predictions,
    )
)

previous_score_r2 = r2_score(
    y_test,
    previous_score_predictions,
)

print(
    f"{'Previous Score':25s}"
    f" MAE={previous_score_mae:6.2f}"
    f" RMSE={previous_score_rmse:6.2f}"
    f" R2={previous_score_r2:6.3f}"
)


# Previous average baseline
previous_average_predictions = (
    test_df["previous_average_score"]
)

previous_average_mae = mean_absolute_error(
    y_test,
    previous_average_predictions,
)

previous_average_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        previous_average_predictions,
    )
)

previous_average_r2 = r2_score(
    y_test,
    previous_average_predictions,
)

print(
    f"{'Previous Average':25s}"
    f" MAE={previous_average_mae:6.2f}"
    f" RMSE={previous_average_rmse:6.2f}"
    f" R2={previous_average_r2:6.3f}"
)


# Dummy mean
dummy_features = ["previous_score"]

X_train_dummy = train_df[dummy_features]
X_test_dummy = test_df[dummy_features]

dummy = DummyRegressor(
    strategy="mean"
)

evaluate_model(
    "Dummy Mean",
    dummy,
    X_train_dummy,
    y_train,
    X_test_dummy,
    y_test,
)


# ============================================================
# EXPERIMENTS
# ============================================================

experiments = {

    "Performance Only": (
        performance_features
    ),

    "Behavior Only": (
        behavior_features
        + categorical_features
    ),

    "Full Model": (
        performance_features
        + behavior_features
        + assessment_features
        + categorical_features
    ),
}


results = []


# ============================================================
# MODELS
# ============================================================

models = {

    "Ridge": Ridge(
        alpha=10.0
    ),

    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        min_samples_leaf=5,
        random_state=42,
    ),
}


# ============================================================
# TRAIN
# ============================================================

for experiment_name, features in experiments.items():

    print("\n" + "=" * 70)
    print(experiment_name.upper())
    print("=" * 70)

    print("Features:")
    print(", ".join(features))

    X_train = prepare_features(
        train_df,
        features,
    )

    X_test = prepare_features(
        test_df,
        features,
    )

    X_train, X_test = align_features(
        X_train,
        X_test,
    )

    print(
        "\nFeature count:",
        X_train.shape[1]
    )

    for model_name, model in models.items():

        result = evaluate_model(
            model_name,
            model,
            X_train,
            y_train,
            X_test,
            y_test,
        )

        result["experiment"] = (
            experiment_name
        )

        results.append(result)


# ============================================================
# RESULTS TABLE
# ============================================================

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

results_df = pd.DataFrame(results)

results_df = results_df[
    [
        "experiment",
        "model",
        "mae",
        "rmse",
        "r2",
    ]
]

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# ASSESSMENT TYPE PERFORMANCE
# ============================================================

print("\n" + "=" * 70)
print("FULL MODEL PERFORMANCE BY ASSESSMENT TYPE")
print("=" * 70)

full_features = (
    performance_features
    + behavior_features
    + assessment_features
    + categorical_features
)

X_train = prepare_features(
    train_df,
    full_features,
)

X_test = prepare_features(
    test_df,
    full_features,
)

X_train, X_test = align_features(
    X_train,
    X_test,
)

final_model = GradientBoostingRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    min_samples_leaf=5,
    random_state=42,
)

final_model.fit(
    X_train,
    y_train,
)

test_predictions = np.clip(
    final_model.predict(X_test),
    0,
    100,
)

evaluation_df = test_df[
    [
        "assessment_type",
        "target",
    ]
].copy()

evaluation_df["prediction"] = test_predictions

for assessment_type, group in evaluation_df.groupby(
    "assessment_type"
):

    mae = mean_absolute_error(
        group["target"],
        group["prediction"],
    )

    rmse = np.sqrt(
        mean_squared_error(
            group["target"],
            group["prediction"],
        )
    )

    r2 = r2_score(
        group["target"],
        group["prediction"],
    )

    print(
        f"{assessment_type:10s}"
        f" n={len(group):6d}"
        f" MAE={mae:6.2f}"
        f" RMSE={rmse:6.2f}"
        f" R2={r2:6.3f}"
    )


print("\n" + "=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)
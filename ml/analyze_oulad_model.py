import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


# ============================================================
# CONFIG
# ============================================================

DATA_PATH = "oulad_studytrack_dataset_v2.csv"

RANDOM_STATE = 42


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("STUDYTRACK - OULAD FEATURE IMPORTANCE")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

print(f"\nDataset: {df.shape}")


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
# TEMPORAL SPLIT
# ============================================================

train_parts = []
test_parts = []

group_columns = [
    "student_id",
    "code_module",
    "code_presentation",
]

for _, group in df.groupby(group_columns, sort=False):

    n = len(group)

    if n < 2:
        train_parts.append(group)
        continue

    split_index = int(np.ceil(n * 0.8))

    train_parts.append(group.iloc[:split_index])
    test_parts.append(group.iloc[split_index:])


train_df = pd.concat(train_parts).reset_index(drop=True)
test_df = pd.concat(test_parts).reset_index(drop=True)

print("\nTemporal split:")
print(f"Train: {train_df.shape}")
print(f"Test : {test_df.shape}")


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
                sparse_output=False
            ),
            categorical_features,
        ),
    ],
    remainder="passthrough",
)


# ============================================================
# RANDOM FOREST
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


print("\nTraining Random Forest...")

pipeline.fit(X_train, y_train)

print("Training complete.")


# ============================================================
# FEATURE NAMES
# ============================================================

feature_names = pipeline.named_steps[
    "preprocessor"
].get_feature_names_out()


importances = pipeline.named_steps[
    "model"
].feature_importances_


importance_df = pd.DataFrame(
    {
        "feature": feature_names,
        "importance": importances,
    }
)


importance_df = importance_df.sort_values(
    "importance",
    ascending=False
).reset_index(drop=True)


# ============================================================
# PRINT FEATURE IMPORTANCE
# ============================================================

print("\n" + "=" * 70)
print("FEATURE IMPORTANCE")
print("=" * 70)

print(
    importance_df.head(20).to_string(index=False)
)


# ============================================================
# GROUP IMPORTANCE
# ============================================================

def get_original_feature(feature_name):

    feature_name = feature_name.replace(
        "categorical__",
        ""
    )

    feature_name = feature_name.replace(
        "remainder__",
        ""
    )

    for feature in features:

        if feature_name == feature:
            return feature

        if feature_name.startswith(feature + "_"):
            return feature

    return feature_name


importance_df["original_feature"] = (
    importance_df["feature"]
    .apply(get_original_feature)
)


group_importance = (
    importance_df
    .groupby("original_feature")["importance"]
    .sum()
    .sort_values(ascending=False)
)


print("\n" + "=" * 70)
print("GROUPED FEATURE IMPORTANCE")
print("=" * 70)

print(group_importance.to_string())


# ============================================================
# FEATURE GROUP TOTALS
# ============================================================

performance_total = group_importance[
    group_importance.index.isin(performance_features)
].sum()

behavior_total = group_importance[
    group_importance.index.isin(behavior_features)
].sum()

assessment_total = group_importance[
    group_importance.index.isin(assessment_features)
].sum()

categorical_total = group_importance[
    group_importance.index.isin(categorical_features)
].sum()


group_totals = pd.Series(
    {
        "Performance": performance_total,
        "Behavior": behavior_total,
        "Assessment": assessment_total,
        "Categorical": categorical_total,
    }
).sort_values(ascending=False)


print("\n" + "=" * 70)
print("FEATURE GROUP IMPORTANCE")
print("=" * 70)

print(group_totals.to_string())


# ============================================================
# SAVE RESULTS
# ============================================================

importance_df.to_csv(
    "oulad_feature_importance.csv",
    index=False
)

group_importance.to_csv(
    "oulad_feature_importance_grouped.csv"
)

print("\nResults saved:")
print("  oulad_feature_importance.csv")
print("  oulad_feature_importance_grouped.csv")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
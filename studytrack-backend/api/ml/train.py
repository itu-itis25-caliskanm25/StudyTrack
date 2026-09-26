import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

import django

django.setup()

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from api.ml.dataset import build_training_dataset


def train_model():

    # --------------------------------------------------
    # Dataset
    # --------------------------------------------------

    df = build_training_dataset()

    print(f"Dataset shape: {df.shape}")

    # --------------------------------------------------
    # Features / Target
    # --------------------------------------------------

    feature_columns = [
        "previous_score",
        "previous_average_score",
        "previous_score_count",
        "score_trend",
        "study_minutes_7d",
        "study_minutes_30d",
        "study_sessions_7d",
        "study_sessions_30d",
        "active_days_7d",
        "active_days_30d",
        "days_since_previous_quiz",
        "days_until_exam",
        "topic_difficulty",
    ]

    X = df[feature_columns]
    y = df["target_score"]

    # Eksik değerleri kontrol et
    if X.isnull().any().any():
        print("Warning: Missing values found in features.")

        X = X.fillna(0)

    # --------------------------------------------------
    # Train / Test
    # --------------------------------------------------

    split_index = int(len(df) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")

    # --------------------------------------------------
    # Random Forest
    # --------------------------------------------------

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )

    # --------------------------------------------------
    # Evaluation
    # --------------------------------------------------

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    print()
    print("--------------------------------")
    print("Model Evaluation")
    print("--------------------------------")
    print(f"MAE  : {mae:.3f}")
    print(f"RMSE : {rmse:.3f}")
    print(f"R²   : {r2:.3f}")
    print("--------------------------------")

    # --------------------------------------------------
    # Feature importance
    # --------------------------------------------------

    print()
    print("Feature Importance")
    print("--------------------------------")

    importance = pd.Series(
        model.feature_importances_,
        index=feature_columns
    ).sort_values(ascending=False)

    print(importance)

    # --------------------------------------------------
    # Save model
    # --------------------------------------------------

    model_path = "api/ml/model.joblib"

    joblib.dump(
        {
            "model": model,
            "features": feature_columns,
        },
        model_path
    )

    print()
    print(f"Model saved: {model_path}")


if __name__ == "__main__":
    train_model()
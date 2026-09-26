import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

df = pd.read_csv("studytrack_dataset.csv")

# Tarihe göre sırala
df["quiz_date"] = pd.to_datetime(df["quiz_date"])
df = df.sort_values("quiz_date").reset_index(drop=True)

features = [
    "study_minutes_7d",
    "study_minutes_30d",
    "study_sessions_7d",
    "study_sessions_30d",
    "average_session_duration",
    "previous_quiz_count",
    "previous_quiz_average",
    "last_quiz_score",
    "best_quiz_score",
    "worst_quiz_score",
    "quiz_trend",
    "days_until_exam",
    "topic_difficulty",
]

target = "target"

X = df[features]
y = df[target]

split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print("--------------------------------")
print("Dataset")
print("--------------------------------")
print(f"Total samples : {len(df)}")
print(f"Train samples : {len(X_train)}")
print(f"Test samples  : {len(X_test)}")

models = {
    "Linear Regression": LinearRegression(),
    
    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        random_state=42,
    ),
    
    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=200,
        random_state=42,
        learning_rate=0.05,
        max_depth=2,
    ),
}

print("\n--------------------------------")
print("Model Results")
print("--------------------------------")

for name, model in models.items():

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(y_test, predictions)

    print(f"\n{name}")
    print(f"MAE  : {mae:.2f}")
    print(f"RMSE : {rmse:.2f}")
    print(f"R²   : {r2:.2f}")


best_model = models["Gradient Boosting"]

predictions = best_model.predict(X_test)

results = pd.DataFrame({
    "actual": y_test.values,
    "predicted": predictions.round(2),
})

results["error"] = (
    results["actual"] - results["predicted"]
).round(2)

print("\n--------------------------------")
print("Gradient Boosting Predictions")
print("--------------------------------")

print(results.to_string(index=False))



importances = best_model.feature_importances_

feature_importance = pd.DataFrame({
    "feature": features,
    "importance": importances
})

feature_importance = feature_importance.sort_values(
    "importance",
    ascending=False
)

print("\n--------------------------------")
print("Feature Importance")
print("--------------------------------")

print(feature_importance.to_string(index=False))
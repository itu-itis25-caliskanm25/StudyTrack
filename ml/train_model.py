import pandas as pd
import zipfile
import io

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

# ========================================
# 1. Veriyi yükle
# ========================================

ZIP_FILE = "data/student+performance.zip"


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

with zipfile.ZipFile(ZIP_FILE, "r") as outer_zip:

    student_zip_data = outer_zip.read("student.zip")


with zipfile.ZipFile(io.BytesIO(student_zip_data), "r") as student_zip:

    math_df = pd.read_csv(
        student_zip.open("student-mat.csv"),
        sep=";"
    )

# ========================================
# 2. Hedef değişken
# ========================================

target = "G3"


# ========================================
# MODEL A
# G1 + G2 + çalışma/davranış özellikleri
# ========================================

features_a = [
    "G1",
    "G2",
    "studytime",
    "failures",
    "absences"
]

X_a = math_df[features_a]
y = math_df[target]


X_train_a, X_test_a, y_train_a, y_test_a = train_test_split(
    X_a,
    y,
    test_size=0.2,
    random_state=42
)


model_a = LinearRegression()

model_a.fit(
    X_train_a,
    y_train_a
)

y_pred_a = model_a.predict(X_test_a)


mae_a = mean_absolute_error(
    y_test_a,
    y_pred_a
)

rmse_a = mean_squared_error(
    y_test_a,
    y_pred_a
) ** 0.5

r2_a = r2_score(
    y_test_a,
    y_pred_a
)


# ========================================
# MODEL B
# Sadece çalışma/davranış özellikleri
# ========================================

features_b = [
    "studytime",
    "failures",
    "absences",
    "freetime",
    "goout",
    "health",
    "famrel",
    "traveltime"
]

X_b = math_df[features_b]


X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(
    X_b,
    y,
    test_size=0.2,
    random_state=42
)


model_b = LinearRegression()

model_b.fit(
    X_train_b,
    y_train_b
)

y_pred_b = model_b.predict(X_test_b)


mae_b = mean_absolute_error(
    y_test_b,
    y_pred_b
)

rmse_b = mean_squared_error(
    y_test_b,
    y_pred_b
) ** 0.5

r2_b = r2_score(
    y_test_b,
    y_pred_b
)


# ========================================
# SONUÇLAR
# ========================================

print("\n==============================")
print("MODEL A - Linear Regression")
print("==============================")

print("Features:")
print(features_a)

print(f"\nMAE:  {mae_a:.2f}")
print(f"RMSE: {rmse_a:.2f}")
print(f"R²:   {r2_a:.2f}")


print("\n==============================")
print("MODEL B - Linear Regression")
print("==============================")

print("Features:")
print(features_b)

print(f"\nMAE:  {mae_b:.2f}")
print(f"RMSE: {rmse_b:.2f}")
print(f"R²:   {r2_b:.2f}")


# ========================================
# MODEL B - Random Forest Regression
# ========================================

model_b_rf = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)


model_b_rf.fit(
    X_train_b,
    y_train_b
)


y_pred_b_rf = model_b_rf.predict(
    X_test_b
)


mae_b_rf = mean_absolute_error(
    y_test_b,
    y_pred_b_rf
)

rmse_b_rf = mean_squared_error(
    y_test_b,
    y_pred_b_rf
) ** 0.5

r2_b_rf = r2_score(
    y_test_b,
    y_pred_b_rf
)


print("\n==============================")
print("MODEL B - Random Forest")
print("==============================")

print("Features:")
print(features_b)

print(f"\nMAE:  {mae_b_rf:.2f}")
print(f"RMSE: {rmse_b_rf:.2f}")
print(f"R²:   {r2_b_rf:.2f}")

# ========================================
# MODEL B - Gradient Boosting Regression
# ========================================


model_b_gb = GradientBoostingRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=2,
    random_state=42
)


model_b_gb.fit(
    X_train_b,
    y_train_b
)


y_pred_b_gb = model_b_gb.predict(
    X_test_b
)


mae_b_gb = mean_absolute_error(
    y_test_b,
    y_pred_b_gb
)

rmse_b_gb = mean_squared_error(
    y_test_b,
    y_pred_b_gb
) ** 0.5

r2_b_gb = r2_score(
    y_test_b,
    y_pred_b_gb
)


print("\n==============================")
print("MODEL B - Gradient Boosting")
print("==============================")

print("Features:")
print(features_b)

print(f"\nMAE:  {mae_b_gb:.2f}")
print(f"RMSE: {rmse_b_gb:.2f}")
print(f"R²:   {r2_b_gb:.2f}")


# ========================================
# MODEL C
# Genişletilmiş davranış özellikleri
# ========================================

features_c = [
    "studytime",
    "failures",
    "absences",
    "freetime",
    "goout",
    "health",
    "famrel",
    "traveltime",
    "schoolsup",
    "famsup",
    "paid",
    "activities",
    "higher",
    "internet"
]

X_c = math_df[features_c]


# ----------------------------------------
# Sayısal ve kategorik özellikleri ayır
# ----------------------------------------

numeric_features_c = [
    "studytime",
    "failures",
    "absences",
    "freetime",
    "goout",
    "health",
    "famrel",
    "traveltime"
]

categorical_features_c = [
    "schoolsup",
    "famsup",
    "paid",
    "activities",
    "higher",
    "internet"
]


# ----------------------------------------
# Preprocessing
# ----------------------------------------

preprocessor_c = ColumnTransformer(
    transformers=[
        (
            "num",
            "passthrough",
            numeric_features_c
        ),
        (
            "cat",
            OneHotEncoder(
                drop="first",
                handle_unknown="ignore"
            ),
            categorical_features_c
        )
    ]
)


# ----------------------------------------
# Train / Test
# ----------------------------------------

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
    X_c,
    y,
    test_size=0.2,
    random_state=42
)


# ----------------------------------------
# Model
# ----------------------------------------

model_c = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor_c
        ),
        (
            "regressor",
            LinearRegression()
        )
    ]
)


# ----------------------------------------
# Eğitim
# ----------------------------------------

model_c.fit(
    X_train_c,
    y_train_c
)


# ----------------------------------------
# Tahmin
# ----------------------------------------

y_pred_c = model_c.predict(
    X_test_c
)


# ----------------------------------------
# Değerlendirme
# ----------------------------------------

mae_c = mean_absolute_error(
    y_test_c,
    y_pred_c
)

rmse_c = mean_squared_error(
    y_test_c,
    y_pred_c
) ** 0.5

r2_c = r2_score(
    y_test_c,
    y_pred_c
)


# ----------------------------------------
# Sonuç
# ----------------------------------------

print("\n==============================")
print("MODEL C - Linear Regression")
print("==============================")

print("Features:")
print(features_c)

print(f"\nMAE:  {mae_c:.2f}")
print(f"RMSE: {rmse_c:.2f}")
print(f"R²:   {r2_c:.2f}")
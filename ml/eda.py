import io
import zipfile

import pandas as pd


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

    portuguese_df = pd.read_csv(
        student_zip.open("student-por.csv"),
        sep=";"
    )


# --------------------------------------------------
# Basic information
# --------------------------------------------------

print("=" * 60)
print("MATHEMATICS")
print("=" * 60)

print("Shape:", math_df.shape)

print("\nMissing values:")
print(math_df.isnull().sum())

print("\nData types:")
print(math_df.dtypes)

print("\nStatistics:")
print(math_df.describe())


print("\n" + "=" * 60)
print("PORTUGUESE")
print("=" * 60)

print("Shape:", portuguese_df.shape)

print("\nMissing values:")
print(portuguese_df.isnull().sum())

print("\nData types:")
print(portuguese_df.dtypes)

print("\nStatistics:")
print(portuguese_df.describe())


# --------------------------------------------------
# Important ML variables
# --------------------------------------------------

important_columns = [
    "studytime",
    "failures",
    "absences",
    "G1",
    "G2",
    "G3"
]


print("\n" + "=" * 60)
print("IMPORTANT VARIABLES - MATHEMATICS")
print("=" * 60)

print(math_df[important_columns].describe())


print("\n" + "=" * 60)
print("IMPORTANT VARIABLES - PORTUGUESE")
print("=" * 60)

print(portuguese_df[important_columns].describe())


# --------------------------------------------------
# Correlations
# --------------------------------------------------

print("\n" + "=" * 60)
print("CORRELATIONS - MATHEMATICS")
print("=" * 60)

print(
    math_df[important_columns].corr()["G3"]
    .sort_values(ascending=False)
)


print("\n" + "=" * 60)
print("CORRELATIONS - PORTUGUESE")
print("=" * 60)

print(
    portuguese_df[important_columns].corr()["G3"]
    .sort_values(ascending=False)
)
import io
import zipfile

import pandas as pd


ZIP_FILE = "data/student+performance.zip"


with zipfile.ZipFile(ZIP_FILE, "r") as outer_zip:

    print("Ana ZIP içindeki dosyalar:")
    print(outer_zip.namelist())

    # İç ZIP dosyasını oku
    student_zip_data = outer_zip.read("student.zip")


with zipfile.ZipFile(io.BytesIO(student_zip_data), "r") as student_zip:

    print("\nStudent ZIP içindeki dosyalar:")
    print(student_zip.namelist())

    math_df = pd.read_csv(
        student_zip.open("student-mat.csv"),
        sep=";"
    )

    portuguese_df = pd.read_csv(
        student_zip.open("student-por.csv"),
        sep=";"
    )


print("\n" + "=" * 60)
print("MATHEMATICS DATASET")
print("=" * 60)

print("Shape:", math_df.shape)

print("\nColumns:")
print(math_df.columns.tolist())

print("\nFirst 5 rows:")
print(math_df.head())


print("\n" + "=" * 60)
print("PORTUGUESE DATASET")
print("=" * 60)

print("Shape:", portuguese_df.shape)

print("\nColumns:")
print(portuguese_df.columns.tolist())

print("\nFirst 5 rows:")
print(portuguese_df.head())
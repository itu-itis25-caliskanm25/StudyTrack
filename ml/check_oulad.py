import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/oulad")

files = [
    "assessments.csv",
    "courses.csv",
    "studentAssessment.csv",
    "studentInfo.csv",
    "studentRegistration.csv",
    "studentVle.csv",
    "vle.csv",
]

for file in files:
    path = DATA_DIR / file

    print("\n" + "=" * 70)
    print(file)
    print("=" * 70)

    if not path.exists():
        print("DOSYA BULUNAMADI!")
        continue

    df = pd.read_csv(path)

    print("Shape:", df.shape)
    print("Columns:")
    print(df.columns.tolist())

    print("\nFirst 3 rows:")
    print(df.head(3).to_string(index=False))
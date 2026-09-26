import os
import sys
from datetime import timedelta

import django
import numpy as np
import pandas as pd


# --------------------------------------------------
# Django setup
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "studytrack-backend")

sys.path.append(BACKEND_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from api.models import StudySession, QuizResult, Exam


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def calculate_quiz_trend(previous_quizzes):
    """
    Önceki quiz skorlarının basit doğrusal trendini hesaplar.

    Pozitif değer  -> performans artıyor
    Negatif değer  -> performans düşüyor
    0              -> belirgin trend yok
    """

    if len(previous_quizzes) < 2:
        return 0.0

    scores = np.array([quiz.score for quiz in previous_quizzes], dtype=float)
    x = np.arange(len(scores))

    slope = np.polyfit(x, scores, 1)[0]

    return float(slope)


# --------------------------------------------------
# Main dataset builder
# --------------------------------------------------

def build_dataset():
    quizzes = list(
        QuizResult.objects
        .select_related("topic", "course")
        .order_by("date")
    )

    sessions = list(
        StudySession.objects
        .select_related("topic", "course")
        .order_by("date")
    )

    exams = list(
        Exam.objects
        .select_related("course")
        .order_by("date")
    )

    rows = []

    for quiz in quizzes:

        quiz_date = quiz.date

        # ------------------------------------------
        # Previous quizzes for the same topic
        # ------------------------------------------

        previous_quizzes = [
            q for q in quizzes
            if q.topic_id == quiz.topic_id
            and q.date < quiz_date
        ]

        # İlk quiz için geçmiş performans bilgisi yok.
        # Bu yüzden bu satırı şimdilik dataset'e almıyoruz.
        if not previous_quizzes:
            continue

        # ------------------------------------------
        # Study sessions before this quiz
        # ------------------------------------------

        sessions_before_quiz = [
            s for s in sessions
            if s.topic_id == quiz.topic_id
            and s.date < quiz_date
        ]

        last_7_days = [
            s for s in sessions_before_quiz
            if s.date >= quiz_date - timedelta(days=7)
        ]

        last_30_days = [
            s for s in sessions_before_quiz
            if s.date >= quiz_date - timedelta(days=30)
        ]

        study_minutes_7d = sum(
            s.duration for s in last_7_days
        )

        study_minutes_30d = sum(
            s.duration for s in last_30_days
        )

        study_sessions_7d = len(last_7_days)
        study_sessions_30d = len(last_30_days)

        average_session_duration = (
            sum(s.duration for s in sessions_before_quiz)
            / len(sessions_before_quiz)
            if sessions_before_quiz
            else 0
        )

        # ------------------------------------------
        # Previous quiz statistics
        # ------------------------------------------

        previous_scores = [
            q.score for q in previous_quizzes
        ]

        previous_quiz_count = len(previous_scores)

        previous_quiz_average = (
            sum(previous_scores) / len(previous_scores)
        )

        last_quiz_score = previous_scores[-1]
        best_quiz_score = max(previous_scores)
        worst_quiz_score = min(previous_scores)

        quiz_trend = calculate_quiz_trend(previous_quizzes)

        # ------------------------------------------
        # Days since previous quiz
        # ------------------------------------------

        previous_quiz = previous_quizzes[-1]

        days_since_last_quiz = (
            quiz_date - previous_quiz.date
        ).days

        # ------------------------------------------
        # Nearest future exam
        # ------------------------------------------

        future_exams = [
            exam for exam in exams
            if exam.course_id == quiz.course_id
            and exam.date >= quiz_date
        ]

        if future_exams:
            nearest_exam = min(
                future_exams,
                key=lambda exam: exam.date
            )

            days_until_exam = (
                nearest_exam.date - quiz_date
            ).days

        else:
            days_until_exam = -1

        # ------------------------------------------
        # Topic difficulty
        # ------------------------------------------

        difficulty_map = {
            "easy": 1,
            "medium": 2,
            "hard": 3,
        }

        topic_difficulty = difficulty_map.get(
            quiz.topic.difficulty,
            2
        )

        # ------------------------------------------
        # Build row
        # ------------------------------------------

        row = {
            "topic_id": quiz.topic_id,
            "course_id": quiz.course_id,
            
            "quiz_date": quiz_date,

            "study_minutes_7d": study_minutes_7d,
            "study_minutes_30d": study_minutes_30d,

            "study_sessions_7d": study_sessions_7d,
            "study_sessions_30d": study_sessions_30d,

            "average_session_duration": average_session_duration,

            "previous_quiz_count": previous_quiz_count,
            "previous_quiz_average": previous_quiz_average,
            "last_quiz_score": last_quiz_score,
            "best_quiz_score": best_quiz_score,
            "worst_quiz_score": worst_quiz_score,

            "quiz_trend": quiz_trend,

            "days_since_last_quiz": days_since_last_quiz,
            "days_until_exam": days_until_exam,

            "topic_difficulty": topic_difficulty,

            # --------------------------------------
            # Target
            # --------------------------------------

            "target": quiz.score,
        }

        rows.append(row)

    df = pd.DataFrame(rows)

    return df


# --------------------------------------------------
# Run directly
# --------------------------------------------------

if __name__ == "__main__":

    df = build_dataset()

    print("\nDataset shape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nDataset:")
    print(df)

    output_path = os.path.join(
        os.path.dirname(__file__),
        "studytrack_dataset.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(f"\nDataset saved to:")
    print(output_path)


import os
import sys
import random
import math

from datetime import timedelta

import django
from django.utils import timezone


# --------------------------------------------------
# Django setup
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(BASE_DIR)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()


from api.models import Course, Topic, Exam, StudySession, QuizResult


# --------------------------------------------------
# Configuration
# --------------------------------------------------

random.seed(42)

QUIZZES_PER_TOPIC = 40
STUDY_SESSIONS_PER_TOPIC = 100

DAYS_OF_HISTORY = 180


# --------------------------------------------------
# Courses
# --------------------------------------------------

courses_data = [
    {
        "name": "Mathematics",
        "description": "Mathematics course"
    },
    {
        "name": "Physics",
        "description": "Physics course"
    },
    {
        "name": "Computer Science",
        "description": "Computer Science course"
    },
]


# --------------------------------------------------
# Topics
# --------------------------------------------------

topics_data = [
    ("Mathematics", "Derivatives", "hard"),
    ("Mathematics", "Integrals", "hard"),

    ("Physics", "Newton Laws", "medium"),
    ("Physics", "Energy", "medium"),

    ("Computer Science", "Sorting Algorithms", "medium"),
]


# --------------------------------------------------
# Create courses
# --------------------------------------------------

courses = {}

for data in courses_data:

    course, _ = Course.objects.get_or_create(
        name=data["name"],
        defaults={
            "description": data["description"]
        }
    )

    courses[course.name] = course


# --------------------------------------------------
# Create topics
# --------------------------------------------------

topics = []

for course_name, topic_name, difficulty in topics_data:

    course = courses[course_name]

    topic, _ = Topic.objects.get_or_create(
        course=course,
        name=topic_name,
        defaults={
            "difficulty": difficulty
        }
    )

    topics.append(topic)


# --------------------------------------------------
# Create exams
# --------------------------------------------------

print("Clearing previous demo data...")

QuizResult.objects.all().delete()
StudySession.objects.all().delete()
Exam.objects.all().delete()

now = timezone.now()

for course in courses.values():

    Exam.objects.create(
        course=course,
        name=f"{course.name} Final Exam",
        date=now + timedelta(days=45),
        description=f"{course.name} final examination"
    )


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def difficulty_effect(difficulty):

    if difficulty == "easy":
        return 5

    if difficulty == "medium":
        return 0

    return -5


# --------------------------------------------------
# Generate study sessions
# --------------------------------------------------

print("Creating study sessions...")

for topic in topics:

    for _ in range(STUDY_SESSIONS_PER_TOPIC):

        days_ago = random.randint(
            1,
            DAYS_OF_HISTORY
        )

        session_date = now - timedelta(
            days=days_ago,
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        # Most sessions are moderate length.
        duration = int(
            random.gauss(
                65,
                25
            )
        )

        duration = clamp(
            duration,
            20,
            150
        )

        StudySession.objects.create(
            course=topic.course,
            topic=topic,
            duration=duration,
            date=session_date
        )


# --------------------------------------------------
# Generate quizzes chronologically
# --------------------------------------------------

print("Creating quiz results...")

for topic in topics:

    # Start around a reasonable baseline.
    current_score = random.uniform(
        45,
        65
    )

    # Quiz dates are spaced approximately every 4-6 days.
    quiz_dates = []

    first_quiz_date = (
        now
        - timedelta(days=200)
    )

    for i in range(QUIZZES_PER_TOPIC):

        spacing = random.randint(
            4,
            6
        )

        if i == 0:
            quiz_date = first_quiz_date
        else:
            quiz_date = (
                quiz_dates[-1]
                + timedelta(days=spacing)
            )

        quiz_dates.append(quiz_date)

    # Never allow quiz dates to go beyond today.
    if quiz_dates[-1] > now:
        shift_days = (
            quiz_dates[-1] - now
        ).days

        quiz_dates = [
            quiz_date - timedelta(days=shift_days)
            for quiz_date in quiz_dates
        ]
    # --------------------------------------------------
    # Create each quiz
    # --------------------------------------------------

    for i, quiz_date in enumerate(quiz_dates):

        # --------------------------------------------------
        # Previous quizzes
        # --------------------------------------------------

        previous_quizzes = QuizResult.objects.filter(
            topic=topic,
            date__lt=quiz_date
        ).order_by("date")

        previous_scores = list(
            previous_quizzes.values_list(
                "score",
                flat=True
            )
        )


        # --------------------------------------------------
        # Previous performance
        # --------------------------------------------------

        if previous_scores:

            last_score = previous_scores[-1]

            average_score = sum(
                previous_scores
            ) / len(previous_scores)

            recent_scores = previous_scores[-3:]

            recent_average = sum(
                recent_scores
            ) / len(recent_scores)

            trend = (
                recent_average
                - average_score
            )

        else:

            last_score = current_score
            average_score = current_score
            trend = 0


        # --------------------------------------------------
        # Study activity BEFORE this quiz
        # --------------------------------------------------

        seven_days_ago = (
            quiz_date
            - timedelta(days=7)
        )

        thirty_days_ago = (
            quiz_date
            - timedelta(days=30)
        )

        sessions_7d = StudySession.objects.filter(
            topic=topic,
            date__lt=quiz_date,
            date__gte=seven_days_ago
        )

        sessions_30d = StudySession.objects.filter(
            topic=topic,
            date__lt=quiz_date,
            date__gte=thirty_days_ago
        )

        study_minutes_7d = sum(
            sessions_7d.values_list(
                "duration",
                flat=True
            )
        )

        study_minutes_30d = sum(
            sessions_30d.values_list(
                "duration",
                flat=True
            )
        )


        # --------------------------------------------------
        # Study effect
        # --------------------------------------------------

        # Recent study matters more.
        recent_study_effect = (
            7
            * math.log1p(
                study_minutes_7d
                / 30
            )
        )

        monthly_study_effect = (
            4
            * math.log1p(
                study_minutes_30d
                / 120
            )
        )


        # --------------------------------------------------
        # Consistency effect
        # --------------------------------------------------

        session_count_30d = sessions_30d.count()

        consistency_effect = min(
            session_count_30d * 0.8,
            6
        )


        # --------------------------------------------------
        # Previous performance effect
        # --------------------------------------------------

        performance_effect = (
            last_score * 0.35
            + average_score * 0.25
        )


        # --------------------------------------------------
        # Difficulty
        # --------------------------------------------------

        difficulty = difficulty_effect(
            topic.difficulty
        )


        # --------------------------------------------------
        # Random noise
        # --------------------------------------------------

        noise = random.gauss(
            0,
            5
        )


        # --------------------------------------------------
        # Calculate new score
        # --------------------------------------------------

        new_score = (
            performance_effect
            + recent_study_effect
            + monthly_study_effect
            + consistency_effect
            + difficulty
            + noise
        )


        # Keep score in realistic range.
        new_score = clamp(
            new_score,
            20,
            95
        )


        new_score = round(
            new_score
        )


        # --------------------------------------------------
        # Create quiz
        # --------------------------------------------------

        QuizResult.objects.create(
            course=topic.course,
            topic=topic,
            score=new_score,
            date=quiz_date
        )

        current_score = new_score


# --------------------------------------------------
# Summary
# --------------------------------------------------

print()
print("--------------------------------")
print("Demo data created successfully")
print("--------------------------------")

print(
    f"Courses       : {Course.objects.count()}"
)

print(
    f"Topics        : {Topic.objects.count()}"
)

print(
    f"Study sessions: {StudySession.objects.count()}"
)

print(
    f"Quiz results  : {QuizResult.objects.count()}"
)

print(
    f"Exams         : {Exam.objects.count()}"
)

print()
print("Done!")
from datetime import timedelta

from django.utils import timezone

from api.models import QuizResult, StudySession, Exam


DIFFICULTY_MAP = {
    "easy": 1,
    "medium": 2,
    "hard": 3,
}


def calculate_score_trend(scores):
    if len(scores) < 2:
        return 0.0

    x = list(range(len(scores)))

    x_mean = sum(x) / len(x)
    y_mean = sum(scores) / len(scores)

    numerator = sum(
        (xi - x_mean) * (yi - y_mean)
        for xi, yi in zip(x, scores)
    )

    denominator = sum(
        (xi - x_mean) ** 2
        for xi in x
    )

    if denominator == 0:
        return 0.0

    return numerator / denominator

def get_topic_features_at(topic_id, as_of):
    if hasattr(as_of, "date"):
        as_of_date = as_of.date()
    else:
        as_of_date = as_of
    quiz_results = (
        QuizResult.objects
        .filter(
            topic_id=topic_id,
            date__lt=as_of
        )
        .order_by("date")
    )

    scores = list(
        quiz_results.values_list(
            "score",
            flat=True
        )
    )

    if not scores:
        return None

    previous_score = scores[-1]

    previous_average_score = (
        sum(scores) / len(scores)
    )

    previous_score_count = len(scores)

    recent_scores = scores[-5:]

    score_trend = calculate_score_trend(
        recent_scores
    )

    last_quiz = quiz_results.last()

    if last_quiz is not None:
        days_since_previous_quiz = (
            as_of_date - last_quiz.date
        ).days
    else:
        days_since_previous_quiz = None

    seven_days_ago = as_of - timedelta(days=7)
    thirty_days_ago = as_of - timedelta(days=30)

    sessions_7d = StudySession.objects.filter(
        topic_id=topic_id,
        date__gte=seven_days_ago,
        date__lt=as_of
    )

    sessions_30d = StudySession.objects.filter(
        topic_id=topic_id,
        date__gte=thirty_days_ago,
        date__lt=as_of
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

    study_sessions_7d = sessions_7d.count()
    study_sessions_30d = sessions_30d.count()

    active_days_7d = sessions_7d.dates(
        "date",
        "day"
    ).count()

    active_days_30d = sessions_30d.dates(
        "date",
        "day"
    ).count()

    last_quiz = quiz_results.last()

    days_until_exam = None

    if last_quiz is not None:
        course_id = last_quiz.course_id

        upcoming_exam = (
            Exam.objects
            .filter(
                course_id=course_id,
                date__gte=as_of_date
            )
            .order_by("date")
            .first()
        )

        if upcoming_exam:
            days_until_exam = (
                upcoming_exam.date - as_of_date
            ).days

    topic = last_quiz.topic

    topic_difficulty = DIFFICULTY_MAP.get(
        topic.difficulty,
        0
    )

    return {
        "topic_id": topic_id,
        "previous_score": float(previous_score),
        "previous_average_score": float(
            previous_average_score
        ),
        "previous_score_count":
            previous_score_count,
        "score_trend": float(score_trend),
        "study_minutes_7d":
            float(study_minutes_7d),
        "study_minutes_30d":
            float(study_minutes_30d),
        "study_sessions_7d":
            study_sessions_7d,
        "study_sessions_30d":
            study_sessions_30d,
        "active_days_7d":
            active_days_7d,
        "active_days_30d":
            active_days_30d,
        "days_since_previous_quiz":
            days_since_previous_quiz,
        "days_until_exam":
            days_until_exam,
        "topic_difficulty":
            topic_difficulty,
    }


def get_topic_features(topic_id):
    return get_topic_features_at(
        topic_id,
        timezone.now()
    )
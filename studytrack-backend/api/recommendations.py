from datetime import date

from .models import Topic, QuizResult, StudySession, Exam


def get_recommendation():
    topics = Topic.objects.all()
    quiz_results = QuizResult.objects.all()
    study_sessions = StudySession.objects.all()
    exams = Exam.objects.all()

    if not quiz_results.exists() or not topics.exists():
        return {
            "has_recommendation": False,
            "message": "Not enough data to generate a recommendation."
        }

    # En yakın sınav
    today = date.today()

    nearest_exam = None
    nearest_days = None

    for exam in exams:
        days = (exam.date - today).days

        if days >= 0:
            if nearest_days is None or days < nearest_days:
                nearest_days = days
                nearest_exam = exam

    recommendations = []

    for result in quiz_results:

        try:
            topic = topics.get(id=result.topic_id)
        except Topic.DoesNotExist:
            continue

        quiz_score = float(result.score)

        # -------------------------
        # Quiz weakness
        # -------------------------

        weakness_score = 100 - quiz_score

        # -------------------------
        # Study time
        # -------------------------

        study_minutes = 0

        sessions = study_sessions.filter(
            topic_id=topic.id
        )

        for session in sessions:
            study_minutes += int(session.duration)

        study_score = max(
            0,
            100 - min(study_minutes, 100)
        )

        # -------------------------
        # Exam proximity
        # -------------------------

        exam_score = 0

        if nearest_days is not None:

            if nearest_days <= 3:
                exam_score = 100

            elif nearest_days <= 7:
                exam_score = 80

            elif nearest_days <= 14:
                exam_score = 60

            elif nearest_days <= 30:
                exam_score = 30

            else:
                exam_score = 10

        # -------------------------
        # Priority
        # -------------------------

        priority_score = (
            weakness_score * 0.5
            + study_score * 0.3
            + exam_score * 0.2
        )

        recommendations.append({
            "topic": topic,
            "quiz_score": quiz_score,
            "study_minutes": study_minutes,
            "priority_score": priority_score,
        })

    if not recommendations:
        return {
            "has_recommendation": False,
            "message": "No recommendation available."
        }

    # En yüksek önceliği seç
    recommendations.sort(
        key=lambda item: item["priority_score"],
        reverse=True
    )

    recommendation = recommendations[0]

    priority_score = recommendation["priority_score"]

    if priority_score >= 70:
        priority = "High"

    elif priority_score >= 45:
        priority = "Medium"

    else:
        priority = "Low"

    # Önerilen çalışma süresi
    quiz_score = recommendation["quiz_score"]

    if quiz_score < 50:
        recommended_minutes = 120

    elif quiz_score < 65:
        recommended_minutes = 90

    elif quiz_score < 80:
        recommended_minutes = 60

    else:
        recommended_minutes = 30

    result = {
        "has_recommendation": True,
        "topic": {
            "id": recommendation["topic"].id,
            "name": recommendation["topic"].name,
        },
        "quiz_score": recommendation["quiz_score"],
        "study_minutes": recommendation["study_minutes"],
        "priority_score": round(
            recommendation["priority_score"]
        ),
        "priority": priority,
        "recommended_minutes": recommended_minutes,
    }

    if nearest_exam:
        result["exam"] = {
            "id": nearest_exam.id,
            "name": nearest_exam.name,
            "date": nearest_exam.date,
            "days_remaining": nearest_days,
        }
    else:
        result["exam"] = None

    return result

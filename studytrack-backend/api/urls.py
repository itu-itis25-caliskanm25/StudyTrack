from django.urls import path

from .views import (
    CourseListCreateView,
    TopicListCreateView,
    StudySessionListCreateView,
    QuizResultListCreateView,
    ExamListCreateView,
    recommendation_view,
    prediction_view
)


urlpatterns = [
    path(
        "courses/",
        CourseListCreateView.as_view(),
        name="course-list-create",
    ),

    path(
        "topics/",
        TopicListCreateView.as_view(),
        name="topic-list-create",
    ),

    path(
        "study-sessions/",
        StudySessionListCreateView.as_view(),
        name="study-session-list-create",
    ),

    path(
        "quiz-results/",
        QuizResultListCreateView.as_view(),
        name="quiz-result-list-create",
    ),

    path(
        "exams/",
        ExamListCreateView.as_view(),
        name="exam-list-create",
    ),
    
    path(
        "recommendations/",
        recommendation_view,
        name="recommendation"
    ),
    
    path(
        "predictions/",
        prediction_view,
    ),

]

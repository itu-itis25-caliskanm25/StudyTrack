from django.contrib import admin

from .models import (
    Course,
    Topic,
    Exam,
    StudySession,
    QuizResult,
)


admin.site.register(Course)
admin.site.register(Topic)
admin.site.register(Exam)
admin.site.register(StudySession)
admin.site.register(QuizResult)

from django.db import models
from django.utils import timezone

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="topics"
    )
    name = models.CharField(max_length=100)

    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("easy", "Easy"),
            ("medium", "Medium"),
            ("hard", "Hard"),
        ],
        default="medium"
    )

    def __str__(self):
        return f"{self.course.name} - {self.name}"


class StudySession(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="study_sessions"
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="study_sessions"
    )
    duration = models.PositiveIntegerField(
        help_text="Study duration in minutes"
    )
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return (
            f"{self.course.name} - "
            f"{self.topic.name} - "
            f"{self.duration} min"
        )


class QuizResult(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="quiz_results"
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="quiz_results"
    )
    score = models.PositiveIntegerField()
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return (
            f"{self.course.name} - "
            f"{self.topic.name} - "
            f"{self.score}%"
        )
        
class Exam(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="exams"
    )

    name = models.CharField(max_length=200)

    date = models.DateField()

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


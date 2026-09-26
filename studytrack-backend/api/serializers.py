from rest_framework import serializers

from .models import Course, Topic, StudySession, QuizResult, Exam


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "description",
            "created_at",
        ]


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = [
            "id",
            "course",
            "name",
            "difficulty",
        ]


class StudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySession
        fields = [
            "id",
            "course",
            "topic",
            "duration",
            "date",
        ]


class QuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResult
        fields = [
            "id",
            "course",
            "topic",
            "score",
            "date",
        ]


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            "id",
            "course",
            "name",
            "date",
            "description",
            "created_at",
        ]

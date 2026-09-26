from rest_framework import generics

from .models import Course, Topic, StudySession, QuizResult, Exam
from .serializers import CourseSerializer, TopicSerializer, StudySessionSerializer, QuizResultSerializer, ExamSerializer

from rest_framework.response import Response
from rest_framework.decorators import api_view

from .recommendations import get_recommendation

from api.ml.predictor import predict_topic



class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class TopicListCreateView(generics.ListCreateAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


class StudySessionListCreateView(generics.ListCreateAPIView):
    queryset = StudySession.objects.all()
    serializer_class = StudySessionSerializer


class QuizResultListCreateView(generics.ListCreateAPIView):
    queryset = QuizResult.objects.all()
    serializer_class = QuizResultSerializer


class ExamListCreateView(generics.ListCreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

@api_view(["GET"])
def recommendation_view(request):
    data = get_recommendation()

    return Response(data)


from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def prediction_view(request):

    predictions = []

    topics = Topic.objects.all()

    for topic in topics:

        prediction = predict_topic(
            topic.id
        )

        if prediction is not None:
            predictions.append(
                prediction
            )

    return Response(
        predictions
    )
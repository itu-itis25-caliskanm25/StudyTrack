import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

import django

django.setup()

import pandas as pd

from api.models import QuizResult
from api.ml.features import get_topic_features_at


def build_training_dataset():
    rows = []

    quiz_results = (
        QuizResult.objects
        .select_related("topic", "course")
        .order_by("date")
    )

    for quiz in quiz_results:
        features = get_topic_features_at(
            quiz.topic_id,
            quiz.date
        )

        if features is None:
            continue

        features["target_score"] = float(
            quiz.score
        )

        rows.append(features)

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)
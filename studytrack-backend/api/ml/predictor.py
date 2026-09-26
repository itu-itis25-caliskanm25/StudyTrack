import os
import joblib
import pandas as pd

from django.conf import settings

from api.models import Topic
from api.ml.features import get_topic_features


MODEL_PATH = os.path.join(
    settings.BASE_DIR,
    "api",
    "ml",
    "model.joblib"
)


def load_model():

    data = joblib.load(MODEL_PATH)

    return data["model"], data["features"]


def predict_topic(topic_id):

    topic = Topic.objects.get(
        id=topic_id
    )

    features = get_topic_features(
        topic_id
    )

    if features is None:
        return None

    model, feature_columns = load_model()

    input_data = {
        column: features.get(column, 0)
        for column in feature_columns
    }

    input_df = pd.DataFrame(
        [input_data],
        columns=feature_columns
    )

    prediction = model.predict(
        input_df
    )[0]

    # Skoru 0-100 arasında tut
    prediction = max(
        0,
        min(100, prediction)
    )

    return {
        "topic_id": topic.id,
        "topic_name": topic.name,
        "predicted_score": round(
            float(prediction),
            2
        ),
        "previous_score": features[
            "previous_score"
        ],
        "previous_average_score": round(
            features["previous_average_score"],
            2
        ),
        "study_minutes_7d": features[
            "study_minutes_7d"
        ],
        "study_minutes_30d": features[
            "study_minutes_30d"
        ],
        "days_until_exam": features[
            "days_until_exam"
        ],
    }
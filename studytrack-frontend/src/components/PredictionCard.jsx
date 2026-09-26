import "./PredictionCard.css";

function PredictionCard({ prediction }) {
    if (!prediction) {
        return null;
    }

    const currentScore = prediction.previous_score;
    const predictedScore = prediction.predicted_score;

    const difference = predictedScore - currentScore;

    const differenceText =
        difference > 0
            ? `+${difference.toFixed(1)}`
            : difference.toFixed(1);

    const differenceClass =
        difference > 0
            ? "positive"
            : difference < 0
            ? "negative"
            : "neutral";

    const differenceIcon =
        difference > 0
            ? "↑"
            : difference < 0
            ? "↓"
            : "→";

    return (
        <div className="prediction-card">

            <div className="prediction-header">
                <div>
                    <p className="prediction-label">
                        AI Performance Prediction
                    </p>

                    <h3>
                        {prediction.topic_name}
                    </h3>
                </div>
            </div>

            <div className="prediction-score">
                <span className="prediction-score-value">
                    {predictedScore}
                </span>

                <span className="prediction-score-label">
                    predicted score
                </span>
            </div>

            <div className="prediction-stats">

                <div className="prediction-stat">
                    <span>
                        Current Score
                    </span>

                    <strong>
                        {currentScore}
                    </strong>
                </div>

                <div className="prediction-stat">
                    <span>
                        Expected Change
                    </span>

                    <strong className={`prediction-change ${differenceClass}`}>
                        {differenceIcon} {differenceText}
                    </strong>
                </div>

                <div className="prediction-stat">
                    <span>
                        Average Score
                    </span>

                    <strong>
                        {prediction.previous_average_score}
                    </strong>
                </div>

            </div>

            <div className="prediction-details">

                <p>
                    <span>Study last 7 days</span>
                    <strong>
                        {prediction.study_minutes_7d} min
                    </strong>
                </p>

                <p>
                    <span>Study last 30 days</span>
                    <strong>
                        {prediction.study_minutes_30d} min
                    </strong>
                </p>

                <p>
                    <span>Days until exam</span>
                    <strong>
                        {prediction.days_until_exam ?? "N/A"}
                    </strong>
                </p>

            </div>

        </div>
    );
}

export default PredictionCard;
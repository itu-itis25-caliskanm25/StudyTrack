function AIRecommendation({
    recommendation,
}) {

    if (!recommendation || !recommendation.has_recommendation) {

        return (
            <div className="ai-recommendation">

                <div className="ai-header">

                    <div>
                        <span className="ai-icon">
                            🤖
                        </span>

                        <h2>
                            AI Study Recommendation
                        </h2>
                    </div>

                </div>

                <p>
                    Not enough data to generate
                    a recommendation yet.
                </p>

            </div>
        );
    }


    const {
        topic,
        quiz_score,
        study_minutes,
        priority_score,
        priority,
        recommended_minutes,
        exam,
    } = recommendation;


    let priorityColor = "#16a34a";

    if (priority === "High") {
        priorityColor = "#dc2626";
    }

    if (priority === "Medium") {
        priorityColor = "#f59e0b";
    }


    return (

        <div className="ai-recommendation">

            <div className="ai-header">

                <div>

                    <span className="ai-icon">
                        🤖
                    </span>

                    <h2>
                        AI Study Recommendation
                    </h2>

                </div>


                <span
                    className="priority-badge"
                    style={{
                        backgroundColor:
                            priorityColor,
                    }}
                >
                    {priority} Priority
                </span>

            </div>


            <div className="ai-content">

                <p className="ai-label">
                    Recommended focus
                </p>


                <h3>
                    📚 Focus on {topic.name}
                </h3>


                <div className="ai-metrics">

                    <div className="ai-metric">

                        <span>
                            Quiz Score
                        </span>

                        <strong>
                            {quiz_score}%
                        </strong>

                    </div>


                    <div className="ai-metric">

                        <span>
                            Study Time
                        </span>

                        <strong>
                            {study_minutes} min
                        </strong>

                    </div>


                    <div className="ai-metric">

                        <span>
                            Priority
                        </span>

                        <strong>
                            {priority_score}/100
                        </strong>

                    </div>

                </div>


                {exam && (

                    <div className="exam-warning">

                        📅

                        <span>

                            <strong>
                                {exam.name}
                            </strong>

                            {" "}is in{" "}

                            <strong>
                                {exam.days_remaining} days
                            </strong>

                        </span>

                    </div>

                )}


                <p className="ai-reason">

                    Your quiz performance in{" "}

                    <strong>
                        {topic.name}
                    </strong>

                    {" "}is {quiz_score}%.

                    Your current study time for this
                    topic is {study_minutes} minutes.

                    {exam && (
                        <>
                            {" "}Since your exam is approaching,
                            this topic should receive more attention.
                        </>
                    )}

                </p>


                <div className="ai-action">

                    💡

                    <span>

                        Recommended study time:

                        <strong>
                            {" "}{recommended_minutes} minutes
                        </strong>

                    </span>

                </div>

            </div>

        </div>

    );
}


export default AIRecommendation;

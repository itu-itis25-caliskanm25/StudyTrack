function PerformanceChart({
    quizResults = [],
    topics = [],
}) {
    return (
        <div className="performance-chart">

            <div className="chart-header">
                <h2>Performance</h2>
                <span>Quiz Scores</span>
            </div>

            <div className="chart-bars">

                {quizResults.map((result) => {

                    const topic = topics.find(
                        (topic) => topic.id === result.topic
                    );

                    return (
                        <div
                            className="chart-item"
                            key={result.id}
                        >

                            <div className="bar-container">

                                <div
                                    className="bar"
                                    style={{
                                        height: `${result.score}%`,
                                    }}
                                />

                            </div>

                            <span>
                                {topic
                                    ? topic.name
                                    : `Topic #${result.topic}`}
                            </span>

                            <strong>
                                {result.score}%
                            </strong>

                        </div>
                    );
                })}

            </div>

        </div>
    );
}

export default PerformanceChart;

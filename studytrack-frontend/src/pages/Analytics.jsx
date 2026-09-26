import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";

import {
    getTopics,
    getStudySessions,
    getQuizResults,
} from "../services/api";


function Analytics() {

    const [topics, setTopics] = useState([]);
    const [studySessions, setStudySessions] = useState([]);
    const [quizResults, setQuizResults] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);


    useEffect(() => {

        async function loadAnalytics() {

            try {

                const [
                    topicsData,
                    studySessionsData,
                    quizResultsData,
                ] = await Promise.all([
                    getTopics(),
                    getStudySessions(),
                    getQuizResults(),
                ]);

                setTopics(topicsData);
                setStudySessions(studySessionsData);
                setQuizResults(quizResultsData);

            } catch (error) {

                console.error("Analytics loading error:", error);

                setError(error.message);

            } finally {

                setLoading(false);

            }
        }

        loadAnalytics();

    }, []);


    // -------------------------
    // Total Study Time
    // -------------------------

    const totalStudyMinutes = studySessions.reduce(
        (total, session) =>
            total + Number(session.duration),
        0
    );

    const totalStudyHours = (
        totalStudyMinutes / 60
    ).toFixed(1);


    // -------------------------
    // Average Quiz Score
    // -------------------------

    const averageScore =
        quizResults.length > 0
            ? Math.round(
                quizResults.reduce(
                    (total, result) =>
                        total + Number(result.score),
                    0
                ) / quizResults.length
            )
            : 0;


    // -------------------------
    // Find Topic Name
    // -------------------------

    function getTopicName(topicId) {

        const topic = topics.find(
            (topic) => topic.id === topicId
        );

        return topic
            ? topic.name
            : `Topic #${topicId}`;
    }


    // -------------------------
    // Weak / Strong Topics
    // -------------------------

    const sortedResults = [...quizResults].sort(
        (a, b) =>
            Number(a.score) - Number(b.score)
    );

    const weakTopics = sortedResults.slice(0, 3);

    const strongTopics = [...sortedResults]
        .reverse()
        .slice(0, 3);


    // -------------------------
    // Study Sessions by Date
    // -------------------------

    const studyByDate = {};

    studySessions.forEach((session) => {

        const date = session.date;

        if (!studyByDate[date]) {
            studyByDate[date] = 0;
        }

        studyByDate[date] += Number(session.duration);

    });


    return (
        <div className="dashboard">

            <Sidebar />

            <main className="main-content">

                <header className="topbar">

                    <h1>Analytics</h1>

                    <div className="user-profile">
                        👤 Student
                    </div>

                </header>


                <section className="welcome-section">

                    <h2>
                        Your Learning Analytics 📊
                    </h2>

                    <p>
                        Understand your study habits and performance.
                    </p>

                </section>


                {loading && (
                    <p>Loading analytics...</p>
                )}


                {error && (
                    <p style={{ color: "red" }}>
                        Error: {error}
                    </p>
                )}


                {!loading && !error && (

                    <>

                        {/* SUMMARY */}

                        <section className="stats-container">

                            <div className="stat-card">

                                <span>
                                    Total Study Time
                                </span>

                                <h3>
                                    {totalStudyHours} h
                                </h3>

                                <p style={{ color: "#16a34a" }}>
                                    {studySessions.length} sessions
                                </p>

                            </div>


                            <div className="stat-card">

                                <span>
                                    Average Quiz Score
                                </span>

                                <h3>
                                    {averageScore}%
                                </h3>

                                <p style={{ color: "#f59e0b" }}>
                                    {quizResults.length} quizzes
                                </p>

                            </div>

                        </section>


                        {/* QUIZ PERFORMANCE */}

                        <section className="analytics-section">

                            <div className="section-header">

                                <h2>
                                    Quiz Performance
                                </h2>

                                <span>
                                    Score by topic
                                </span>

                            </div>


                            <div className="performance-list">

                                {quizResults.map((result) => (

                                    <div
                                        className="performance-row"
                                        key={result.id}
                                    >

                                        <div className="performance-info">

                                            <span>
                                                {getTopicName(result.topic)}
                                            </span>

                                            <strong>
                                                {result.score}%
                                            </strong>

                                        </div>


                                        <div className="progress-background">

                                            <div
                                                className="progress-bar"
                                                style={{
                                                    width: `${result.score}%`,
                                                    backgroundColor:
                                                        result.score >= 80
                                                            ? "#16a34a"
                                                            : result.score >= 60
                                                                ? "#f59e0b"
                                                                : "#dc2626",
                                                }}
                                            />

                                        </div>

                                    </div>

                                ))}

                            </div>

                        </section>


                        {/* STUDY TIME */}

                        <section className="analytics-section">

                            <div className="section-header">

                                <h2>
                                    Study Time
                                </h2>

                                <span>
                                    Time spent studying
                                </span>

                            </div>


                            <div className="study-time-list">

                                {Object.entries(studyByDate).map(
                                    ([date, minutes]) => (

                                        <div
                                            className="study-time-row"
                                            key={date}
                                        >

                                            <span>
                                                {date}
                                            </span>

                                            <div className="study-bar-background">

                                                <div
                                                    className="study-bar"
                                                    style={{
                                                        width: `${Math.min(
                                                            minutes,
                                                            180
                                                        ) / 180 * 100}%`,
                                                    }}
                                                />

                                            </div>

                                            <strong>
                                                {minutes} min
                                            </strong>

                                        </div>

                                    )
                                )}

                            </div>

                        </section>


                        {/* WEAK / STRONG TOPICS */}

                        <section className="topic-analysis-grid">


                            <div className="topic-card">

                                <h2>
                                    ⚠️ Topics to Improve
                                </h2>

                                {weakTopics.map((result) => (

                                    <div
                                        className="topic-analysis-item"
                                        key={result.id}
                                    >

                                        <span>
                                            {getTopicName(result.topic)}
                                        </span>

                                        <strong>
                                            {result.score}%
                                        </strong>

                                    </div>

                                ))}

                            </div>


                            <div className="topic-card">

                                <h2>
                                    💪 Strong Topics
                                </h2>

                                {strongTopics.map((result) => (

                                    <div
                                        className="topic-analysis-item"
                                        key={result.id}
                                    >

                                        <span>
                                            {getTopicName(result.topic)}
                                        </span>

                                        <strong>
                                            {result.score}%
                                        </strong>

                                    </div>

                                ))}

                            </div>


                        </section>

                    </>

                )}

            </main>

        </div>
    );
}


export default Analytics;

import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";
import StatCard from "../components/StatCard";
import PerformanceChart from "../components/PerformanceChart";
import AIRecommendation from "../components/AIRecommendation";
import PredictionCard from "../components/PredictionCard";


import {
    getCourses,
    getTopics,
    getStudySessions,
    getQuizResults,
    getExams,
    getRecommendation,
    getPredictions,
} from "../services/api";


function Dashboard() {
    const [courses, setCourses] = useState([]);
    const [topics, setTopics] = useState([]);
    const [studySessions, setStudySessions] = useState([]);
    const [quizResults, setQuizResults] = useState([]);
    const [exams, setExams] = useState([]);
    const [recommendation, setRecommendation] = useState(null);
    const [predictions, setPredictions] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    

    useEffect(() => {
        async function loadDashboard() {
            try {
                const [
                    coursesData,
                    topicsData,
                    studySessionsData,
                    quizResultsData,
                    examsData,
                    recommendationData,
                    predictionsData,
                ] = await Promise.all([
                    getCourses(),
                    getTopics(),
                    getStudySessions(),
                    getQuizResults(),
                    getExams(),
                    getRecommendation(),
                    getPredictions(),
                ]);

                setCourses(coursesData);
                setTopics(topicsData);
                setStudySessions(studySessionsData);
                setQuizResults(quizResultsData);
                setExams(examsData);
                setRecommendation(recommendationData);
                setPredictions(predictionsData);

            } catch (error) {
                console.error("Dashboard loading error:", error);
                setError(error.message);

            } finally {
                setLoading(false);
            }
        }

        loadDashboard();
    }, []);


    // -------------------------
    // Study Hours
    // -------------------------

    const totalStudyMinutes = studySessions.reduce(
        (total, session) => total + Number(session.duration),
        0
    );

    const totalStudyHours = (
        totalStudyMinutes / 60
    ).toFixed(1);


    // -------------------------
    // Average Quiz Score
    // -------------------------

    const averageQuizScore =
        quizResults.length > 0
            ? Math.round(
                quizResults.reduce(
                    (total, result) =>
                        total + Number(result.score),
                    0
                ) / quizResults.length
            )
            : 0;

    console.log("AI Predictions:", predictions);

    return (
        <div className="dashboard">

            <Sidebar />


            <main className="main-content">

                {/* TOP BAR */}

                <header className="topbar">

                    <h1>Dashboard</h1>

                    <div className="user-profile">
                        👤 Student
                    </div>

                </header>


                {/* WELCOME */}

                <section className="welcome-section">

                    <h2>
                        Good afternoon! 👋
                    </h2>

                    <p>
                        Here is your study overview.
                    </p>

                </section>


                {/* LOADING */}

                {loading && (
                    <p>
                        Loading dashboard...
                    </p>
                )}


                {/* ERROR */}

                {error && (
                    <p style={{ color: "red" }}>
                        Error: {error}
                    </p>
                )}


                {/* DASHBOARD CONTENT */}

                {!loading && !error && (

                    <>

                        {/* STAT CARDS */}

                        <section className="stats-container">

                            <StatCard
                                title="Study Hours"
                                value={`${totalStudyHours} h`}
                                description={`${studySessions.length} study sessions`}
                                color="#16a34a"
                            />


                            <StatCard
                                title="Average Quiz Score"
                                value={`${averageQuizScore}%`}
                                description={`${quizResults.length} quiz results`}
                                color="#f59e0b"
                            />

                        </section>


                        <section className="upcoming-exams">

                            <h2>Upcoming Exams</h2>

                            {exams.length === 0 ? (

                                <p>No upcoming exams.</p>

                            ) : (

                                exams.map((exam) => (

                                    <div
                                        className="exam-card"
                                        key={exam.id}
                                    >

                                        <div>
                                            <h3>{exam.name}</h3>

                                            <p>
                                                {exam.description}
                                            </p>
                                        </div>

                                        <div>
                                            📅 {exam.date}
                                        </div>

                                    </div>

                                ))

                            )}

                        </section>



                        {/* PERFORMANCE + AI */}

                        <section className="dashboard-grid">


                            <PerformanceChart
                                quizResults={quizResults}
                                topics={topics}
                            />


                            <AIRecommendation
                                recommendation={recommendation}
                            />

                            {predictions.length > 0 && (
                                <div className="prediction-grid">
                                    {predictions.map((prediction) => (
                                        <PredictionCard
                                            key={prediction.topic_id}
                                            prediction={prediction}
                                        />
                                    ))}
                                </div>
                            )}

                        </section>


                        {/* COURSES */}

                        <section className="courses-overview">

                            <h2>
                                Your Courses
                            </h2>


                            {courses.length === 0 ? (

                                <p>
                                    No courses found.
                                </p>

                            ) : (

                                courses.map((course) => (

                                    <div
                                        className="course-item"
                                        key={course.id}
                                    >

                                        <h3>
                                            {course.name}
                                        </h3>

                                        <p>
                                            {course.description}
                                        </p>

                                    </div>

                                ))

                            )}

                        </section>


                    </>

                )}

            </main>

        </div>
    );
}


export default Dashboard;

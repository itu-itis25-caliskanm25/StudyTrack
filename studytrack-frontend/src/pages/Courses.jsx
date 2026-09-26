import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { getCourses } from "../services/api";


function Courses() {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);


    useEffect(() => {
        async function loadCourses() {
            try {
                const data = await getCourses();
                setCourses(data);
            } catch (error) {
                setError(error.message);
            } finally {
                setLoading(false);
            }
        }

        loadCourses();
    }, []);


    return (
        <div className="dashboard">
            <Sidebar />

            <main className="main-content">
                <header className="topbar">
                    <h1>Courses</h1>
                </header>

                {loading && <p>Loading courses...</p>}

                {error && (
                    <p style={{ color: "red" }}>
                        {error}
                    </p>
                )}

                {!loading && !error && (
                    <section className="courses-container">
                        {courses.map((course) => (
                            <div
                                className="stat-card"
                                key={course.id}
                            >
                                <h3>{course.name}</h3>

                                <p>
                                    {course.description}
                                </p>
                            </div>
                        ))}
                    </section>
                )}
            </main>
        </div>
    );
}


export default Courses;

import { useState } from "react";
import StudyTask from "./StudyTask";

function StudyPlan() {

    const [tasks, setTasks] = useState([
        {
            id: 1,
            subject: "Mathematics",
            topic: "Derivatives",
            duration: "45 min",
            completed: false,
        },
        {
            id: 2,
            subject: "Physics",
            topic: "Newton's Laws",
            duration: "30 min",
            completed: true,
        },
        {
            id: 3,
            subject: "Computer Science",
            topic: "Sorting Algorithms",
            duration: "60 min",
            completed: false,
        },
    ]);

    const toggleTask = (id) => {
        setTasks(
            tasks.map((task) =>
                task.id === id
                    ? {
                        ...task,
                        completed: !task.completed,
                    }
                    : task
            )
        );
    };

    const completedTasks = tasks.filter(
        (task) => task.completed
    ).length;

    const progress =
        tasks.length === 0
            ? 0
            : Math.round(
                (completedTasks / tasks.length) * 100
            );

    return (
        <section className="study-plan">

            <div className="study-plan-header">

                <div>
                    <span className="section-label">
                        TODAY
                    </span>

                    <h2>Today's Study Plan</h2>

                    <p>
                        {completedTasks} of {tasks.length} tasks completed
                    </p>
                </div>

                <div className="study-progress">
                    <strong>{progress}%</strong>
                </div>

            </div>

            <div className="progress-bar">
                <div
                    className="progress-fill"
                    style={{
                        width: `${progress}%`,
                    }}
                />
            </div>

            <div className="study-tasks">

                {tasks.map((task) => (
                    <StudyTask
                        key={task.id}
                        subject={task.subject}
                        topic={task.topic}
                        duration={task.duration}
                        completed={task.completed}
                        onToggle={() => toggleTask(task.id)}
                    />
                ))}

            </div>

        </section>
    );
}

export default StudyPlan;

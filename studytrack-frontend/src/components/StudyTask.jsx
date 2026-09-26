function StudyTask({ subject, topic, duration, completed, onToggle }) {
    return (
        <div className={`study-task ${completed ? "completed" : ""}`}>
            <button
                className="task-checkbox"
                onClick={onToggle}
            >
                {completed ? "✓" : ""}
            </button>

            <div className="task-info">
                <h3>{subject}</h3>
                <p>{topic}</p>
            </div>

            <span className="task-duration">
                {duration}
            </span>
        </div>
    );
}

export default StudyTask;

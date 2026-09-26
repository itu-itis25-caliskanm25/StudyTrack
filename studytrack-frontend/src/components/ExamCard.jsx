function ExamCard({ subject, examName, daysLeft, progress }) {
  return (
    <div className="exam-card">
      <div className="exam-header">
        <div>
          <h4>{subject}</h4>
          <p>{examName}</p>
        </div>

        <span className="days-left">
          {daysLeft} days
        </span>
      </div>

      <div className="progress-container">
        <div
          className="progress-bar"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="exam-footer">
        <span>Preparation</span>
        <strong>{progress}%</strong>
      </div>
    </div>
  );
}

export default ExamCard;
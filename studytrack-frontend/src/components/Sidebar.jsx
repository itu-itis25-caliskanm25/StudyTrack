function Sidebar() {
  return (
    <aside className="sidebar">

      <div className="logo">
        <span className="logo-icon">S</span>
        <span>StudyTrack</span>
      </div>


      <nav className="navigation">

        <a href="/" className="active">
          <span>📊</span>
          Dashboard
        </a>

        <a href="/courses">
          <span>📚</span>
          Courses
        </a>

        <a href="/exams">
          <span>📝</span>
          Exams
        </a>

        <a href="/analytics">
          <span>📈</span>
          Analytics
        </a>

      </nav>


      <div className="sidebar-bottom">

        <div className="sidebar-ai">
          <span>🤖</span>

          <div>
            <strong>AI Insights</strong>
            <p>View your recommendations</p>
          </div>
        </div>

      </div>

    </aside>
  );
}

export default Sidebar;

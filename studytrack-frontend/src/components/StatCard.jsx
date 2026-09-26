function StatCard({ title, value, description, color, icon }) {
  return (
    <div className="stat-card">
      <div className="stat-card-top">
        <span className="stat-title">{title}</span>
        <span className="stat-icon">{icon}</span>
      </div>

      <h3>{value}</h3>

      <p style={{ color: color }}>
        {description}
      </p>
    </div>
  );
}

export default StatCard;
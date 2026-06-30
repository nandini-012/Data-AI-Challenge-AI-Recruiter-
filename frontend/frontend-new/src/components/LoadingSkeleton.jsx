export function CardSkeleton({ count = 4 }) {
  return (
    <div className="skeleton-cards">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="card skeleton-card">
          <div className="skeleton skeleton-circle" />
          <div className="skeleton skeleton-lg" />
          <div className="skeleton skeleton-sm" />
        </div>
      ))}
    </div>
  )
}

export function TableSkeleton({ rows = 8 }) {
  return (
    <div className="skeleton-table">
      <div className="skeleton skeleton-header" />
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="skeleton skeleton-row"
          style={{ animationDelay: `${i * 0.05}s` }}
        />
      ))}
    </div>
  )
}

export function ChartSkeleton() {
  return (
    <div className="card skeleton-chart">
      <div className="skeleton skeleton-lg" style={{ width: '40%' }} />
      <div className="skeleton-bars">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="skeleton skeleton-bar"
            style={{ height: `${30 + Math.random() * 60}%` }}
          />
        ))}
      </div>
    </div>
  )
}

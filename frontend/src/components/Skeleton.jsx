export function SkeletonCard({ className = '' }) {
  return (
    <div className={`skeleton skeleton-card ${className}`} />
  );
}

export function SkeletonText({ lines = 3, className = '' }) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton skeleton-text"
          style={{ width: `${85 - i * 15}%` }}
        />
      ))}
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 5 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="flex items-center gap-4 animate-fade-in" style={{ animationDelay: `${r * 0.05}s` }}>
          {Array.from({ length: cols }).map((_, c) => (
            <div
              key={c}
              className="skeleton"
              style={{
                height: c === 0 ? 36 : 14,
                width: c === 0 ? 36 : `${60 + Math.random() * 30}%`,
                borderRadius: c === 0 ? '50%' : 4,
                flex: c === 0 ? 'none' : 1,
              }}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

export function SkeletonKPI() {
  return (
    <div className="kpi-card">
      <div className="flex items-center justify-between mb-3">
        <div className="skeleton" style={{ width: 40, height: 40, borderRadius: 10 }} />
        <div className="skeleton" style={{ width: 60, height: 14 }} />
      </div>
      <div className="skeleton" style={{ width: 80, height: 32, marginBottom: 4 }} />
      <div className="skeleton" style={{ width: 100, height: 14 }} />
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <div>
          <div className="skeleton" style={{ width: 160, height: 28, marginBottom: 8 }} />
          <div className="skeleton" style={{ width: 260, height: 16 }} />
        </div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => <SkeletonKPI key={i} />)}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card-static p-5"><SkeletonCard className="h-[280px]" /></div>
        <div className="card-static p-5"><SkeletonCard className="h-[280px]" /></div>
      </div>
    </div>
  );
}

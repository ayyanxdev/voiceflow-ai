import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Phone, PhoneIncoming, PhoneOutgoing, Loader2, Search, Download, Play } from 'lucide-react';
import api from '../services/api';
import StatusBadge from '../components/StatusBadge';
import AnimatedCounter from '../components/AnimatedCounter';
import { SkeletonTable } from '../components/Skeleton';

function formatDuration(s) {
  const m = Math.floor(s / 60);
  return `${m}:${(s % 60).toString().padStart(2, '0')}`;
}

function formatTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
}

export default function Calls() {
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [direction, setDirection] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    const params = {};
    if (search) params.search = search;
    if (direction) params.direction = direction;
    if (statusFilter) params.status = statusFilter;
    api.getCalls(params).then(setCalls).catch(console.error).finally(() => setLoading(false));
  }, [search, direction, statusFilter]);

  const handleExport = () => api.exportCalls({ direction, status: statusFilter }).catch(err => alert('Export failed: ' + err.message));

  const stats = {
    total: calls.length,
    inbound: calls.filter(c => c.direction === 'inbound').length,
    outbound: calls.filter(c => c.direction === 'outbound').length,
    avgDuration: calls.length > 0 ? Math.round(calls.reduce((a, c) => a + c.duration_seconds, 0) / calls.length) : 0,
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold gradient-text">Calls</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>View and manage all voice interactions</p>
        </div>
        <button onClick={handleExport} className="btn-primary flex items-center gap-2 text-sm">
          <Download size={14} /> Export CSV
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 animate-fade-in stagger-1" style={{ opacity: 0, animationFillMode: 'forwards' }}>
        {[
          { label: 'Total Calls', value: stats.total, color: 'text-violet-600' },
          { label: 'Inbound', value: stats.inbound, color: 'text-blue-600' },
          { label: 'Outbound', value: stats.outbound, color: 'text-purple-600' },
          { label: 'Avg Duration', value: formatDuration(stats.avgDuration), color: 'text-emerald-600' },
        ].map(s => (
          <div key={s.label} className="card-static p-4 text-center">
            <p className={`text-2xl font-bold ${s.color}`}>
              {typeof s.value === 'number' ? <AnimatedCounter value={s.value} /> : s.value}
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{s.label}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 animate-fade-in stagger-2" style={{ opacity: 0, animationFillMode: 'forwards' }}>
        <div className="relative flex-1 min-w-[200px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search calls..."
            className="input-modern pl-9 pr-4 py-2"
          />
        </div>
        <select
          value={direction}
          onChange={(e) => setDirection(e.target.value)}
          className="input-modern w-auto"
        >
          <option value="">All Directions</option>
          <option value="inbound">Inbound</option>
          <option value="outbound">Outbound</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input-modern w-auto"
        >
          <option value="">All Statuses</option>
          <option value="completed">Completed</option>
          <option value="initiated">Initiated</option>
          <option value="ringing">Ringing</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {/* Table */}
      {loading ? (
        <div className="card-static p-5"><SkeletonTable rows={6} cols={7} /></div>
      ) : calls.length === 0 ? (
        <div className="text-center py-16 animate-fade-in">
          <Phone size={48} className="mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
          <p className="text-lg font-medium" style={{ color: 'var(--text-secondary)' }}>No calls found</p>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>Calls from your AI agent will appear here</p>
        </div>
      ) : (
        <div className="card-static overflow-hidden animate-fade-in stagger-3" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b" style={{ borderColor: 'var(--border-color)', background: 'var(--bg-tertiary)' }}>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Caller</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Direction</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Duration</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Outcome</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Score</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Status</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Date</th>
                </tr>
              </thead>
              <tbody className="divide-y" style={{ borderColor: 'var(--border-color)' }}>
                {calls.map((c, i) => (
                  <tr
                    key={c.id}
                    className="cursor-pointer transition-colors"
                    style={{ animationDelay: `${i * 0.03}s` }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-tertiary)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                    onClick={() => navigate(`/calls/${c.id}`)}
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0" style={{ background: c.direction === 'inbound' ? 'rgba(59,130,246,0.1)' : 'rgba(99,102,241,0.1)' }}>
                          {c.direction === 'inbound' ? <PhoneIncoming size={14} className="text-blue-500" /> : <PhoneOutgoing size={14} className="text-violet-500" />}
                        </div>
                        <div>
                          <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Call #{c.id}</p>
                          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{c.lead_id ? `Lead #${c.lead_id}` : 'No lead'}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-semibold ${c.direction === 'inbound' ? 'text-blue-600' : 'text-violet-600'}`}>
                        {c.direction === 'inbound' ? '↗ Inbound' : '↙ Outbound'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm font-medium tabular-nums" style={{ color: 'var(--text-secondary)' }}>{formatDuration(c.duration_seconds)}</span>
                    </td>
                    <td className="px-4 py-3"><StatusBadge value={c.outcome} /></td>
                    <td className="px-4 py-3">
                      <span className={`text-sm font-bold ${c.qualification_score >= 70 ? 'text-emerald-600' : c.qualification_score >= 40 ? 'text-amber-600' : 'text-slate-500'}`}>
                        {c.qualification_score}
                      </span>
                    </td>
                    <td className="px-4 py-3"><StatusBadge value={c.status} /></td>
                    <td className="px-4 py-3 text-sm" style={{ color: 'var(--text-muted)' }}>{formatTime(c.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

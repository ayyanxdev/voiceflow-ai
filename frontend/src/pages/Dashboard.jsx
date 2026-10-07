import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Phone, PhoneIncoming, PhoneOutgoing, Users, Calendar, TrendingUp,
  Clock, Flame, Loader2, Zap, Activity, RefreshCw, Sparkles, Bot
} from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import api from '../services/api';
import StatusBadge from '../components/StatusBadge';
import AnimatedCounter from '../components/AnimatedCounter';
import { DashboardSkeleton } from '../components/Skeleton';
import { useWebSocket } from '../hooks/useWebSocket';

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function formatTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
}

function formatRelativeTime(iso) {
  if (!iso) return '';
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

const dateRanges = [
  { label: '7D', value: 7 },
  { label: '14D', value: 14 },
  { label: '30D', value: 30 },
];

const COLORS = ['#c94978', '#8a72b5', '#e7a06b', '#719bbd', '#7c9c87', '#dd7d91', '#c5a45b'];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl px-3 py-2 shadow-lg border" style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }}>
      <p className="text-xs font-medium" style={{ color: 'var(--text-muted)' }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-sm font-bold" style={{ color: p.color }}>
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  );
};

function KPICard({ icon: Icon, label, value, color, delay = 0 }) {
  return (
    <div
      className="kpi-card animate-fade-in"
      style={{ animationDelay: `${delay}s`, opacity: 0, animationFillMode: 'forwards' }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${color}`}>
          <Icon size={18} className="text-white" />
        </div>
      </div>
      <p className="kpi-value" style={{ color: 'var(--text-primary)' }}>
        {typeof value === 'number' ? <AnimatedCounter value={value} /> : value}
      </p>
      <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>{label}</p>
    </div>
  );
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [dateRange, setDateRange] = useState(30);
  const [notification, setNotification] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const navigate = useNavigate();

  const loadDashboard = async () => {
    try {
      const d = await api.getDashboard();
      setData(d);
    } catch (e) { console.error(e); }
  };

  const { connected, lastMessage } = useWebSocket();

  // Refresh dashboard when WebSocket receives call updates
  useEffect(() => {
    if (lastMessage?.type === 'call_update') {
      loadDashboard();
    }
  }, [lastMessage]);

  useEffect(() => {
    loadDashboard().finally(() => setLoading(false));
  }, []);

  const handleSeed = async () => {
    setSeeding(true);
    setNotification(null);
    try {
      const result = await api.seedDemo();
      setNotification({ type: 'success', text: result.message || 'Demo data generated!' });
      await loadDashboard();
    } catch (e) {
      setNotification({ type: 'error', text: e.message || 'Failed to generate demo data' });
    } finally {
      setSeeding(false);
    }
  };

  if (loading && !data) return <DashboardSkeleton />;
  if (!data) return <div className="text-center py-12" style={{ color: 'var(--text-muted)' }}>Failed to load dashboard</div>;

  const { overview, charts, recent_activity, recent_calls, hot_leads, upcoming_appointments } = data;
  const isEmpty = overview.total_calls === 0;
  const visibleCalls = charts.calls_over_time.slice(-dateRange);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboard();
    setRefreshing(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold gradient-text">
            Dashboard
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            Voice AI performance and today's activity
            {connected && <span className="ml-2 text-emerald-500">● Live</span>}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Date Range Picker */}
          <div className="flex rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border-color)', background: 'var(--bg-secondary)' }}>
            {dateRanges.map(r => (
              <button
                key={r.value}
                onClick={() => setDateRange(r.value)}
                aria-pressed={dateRange === r.value}
                className={`px-3 py-1.5 text-xs font-medium transition-all ${
                  dateRange === r.value
                    ? 'bg-rose-600 text-white'
                    : ''
                }`}
                style={dateRange !== r.value ? { color: 'var(--text-secondary)' } : {}}
              >
                {r.label}
              </button>
            ))}
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="btn-secondary flex items-center gap-2 text-sm"
            aria-label="Refresh dashboard"
          >
            <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} />
            Refresh
          </button>
          {isEmpty && (
            <button
              onClick={handleSeed}
              disabled={seeding}
              className="btn-primary flex items-center gap-2 text-sm"
            >
              {seeding ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
              {seeding ? 'Generating...' : 'Generate Demo Data'}
            </button>
          )}
        </div>
      </div>

      <section className="dashboard-welcome animate-fade-in" aria-label="Welcome">
        <div className="dashboard-welcome-copy">
          <span className="dashboard-welcome-label"><Sparkles size={13} /> A LITTLE MAGIC IN EVERY CONVERSATION</span>
          <p>A lovely day to make someone's day.</p>
        </div>
        <div className="dashboard-welcome-mark" aria-hidden="true">
          <Bot size={27} />
          <Sparkles size={15} />
        </div>
        <img src="/login-image.jpg" alt="" />
      </section>

      {/* Notification */}
      {notification && (
        <div
          className={`p-3 rounded-xl text-sm font-medium animate-slide-in-up ${
            notification.type === 'success'
              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-400 dark:border-emerald-800'
              : 'bg-red-50 text-red-700 border border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800'
          }`}
        >
          {notification.text}
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
        <KPICard icon={Phone} label="Total Calls" value={overview.total_calls} color="bg-rose-500" delay={0.05} />
        <KPICard icon={PhoneIncoming} label="Answered" value={overview.answered_calls} color="bg-fuchsia-500" delay={0.1} />
        <KPICard icon={Users} label="Qualified Leads" value={overview.qualified_leads} color="bg-amber-500" delay={0.15} />
        <KPICard icon={Calendar} label="Appointments" value={overview.appointments_booked} color="bg-pink-600" delay={0.2} />
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
        <KPICard icon={TrendingUp} label="Conversion Rate" value={`${overview.conversion_rate}%`} color="bg-orange-400" delay={0.25} />
        <KPICard icon={Clock} label="Avg Duration" value={formatDuration(Math.round(overview.avg_call_duration))} color="bg-violet-500" delay={0.3} />
        <KPICard icon={Users} label="Total Leads" value={overview.total_leads} color="bg-sky-500" delay={0.35} />
        <KPICard icon={Flame} label="Hot Leads" value={overview.hot_leads} color="bg-rose-700" delay={0.4} />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        {/* Calls Over Time - Sparkline Style */}
        <div className="card-static p-5 animate-fade-in stagger-3" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>Calls Over Time</h3>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>Daily volume · last {dateRange} days</p>
            </div>
            <div className={`flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium ${connected ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>
              <Activity size={12} />
              {connected ? 'Live' : 'Offline'}
            </div>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={visibleCalls}>
              <defs>
                <linearGradient id="colorCalls" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#c94978" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#c94978" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: 'var(--text-muted)' }} tickFormatter={(v) => v.slice(5)} />
              <YAxis tick={{ fontSize: 10, fill: 'var(--text-muted)' }} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="count" name="Calls" stroke="#c94978" fill="url(#colorCalls)" strokeWidth={2.5} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Call Outcomes */}
        <div className="card-static p-5 animate-fade-in stagger-4" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>Call Outcomes</h3>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>Distribution of results</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={charts.call_outcomes} barCategoryGap="20%">
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis dataKey="outcome" tick={{ fontSize: 9, fill: 'var(--text-muted)' }} />
              <YAxis tick={{ fontSize: 10, fill: 'var(--text-muted)' }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" name="Count" radius={[6, 6, 0, 0]}>
                {charts.call_outcomes.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Inbound vs Outbound + Lead Funnel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        <div className="card-static p-5 animate-fade-in stagger-5" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Inbound vs Outbound</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={charts.inbound_vs_outbound}
                dataKey="count"
                nameKey="outcome"
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={85}
                paddingAngle={4}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {charts.inbound_vs_outbound.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card-static p-5 animate-fade-in stagger-6" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Lead Funnel</h3>
          <div className="space-y-3 mt-2">
            {charts.lead_funnel.map((item, i) => (
              <div key={item.stage} className="flex items-center gap-3">
                <div className="w-28 text-xs capitalize font-medium" style={{ color: 'var(--text-secondary)' }}>
                  {item.stage.replace(/_/g, ' ')}
                </div>
                <div className="flex-1 rounded-full h-7 overflow-hidden" style={{ background: 'var(--bg-tertiary)' }}>
                  <div
                    className="h-full rounded-full transition-all duration-700 ease-out flex items-center justify-end pr-2"
                    style={{
                      width: item.count ? `${Math.max((item.count / Math.max(...charts.lead_funnel.map(f => f.count), 1)) * 100, 12)}%` : '0%',
                      background: `linear-gradient(90deg, ${COLORS[i % COLORS.length]}dd, ${COLORS[i % COLORS.length]})`,
                    }}
                  >
                    <span className="text-xs font-bold text-white drop-shadow-sm">{item.count}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Three Column: Activity, Recent Calls, Hot Leads */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
        {/* Recent Activity */}
        <div className="card-static p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>Recent Activity</h3>
            <button
              onClick={() => navigate('/activity')}
              className="text-xs font-medium text-violet-600 hover:text-violet-700"
            >
              View all
            </button>
          </div>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {recent_activity.length === 0 && (
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No activity yet</p>
            )}
            {recent_activity.slice(0, 8).map((a, i) => (
              <div key={a.id} className="flex gap-3 text-sm animate-fade-in" style={{ animationDelay: `${i * 0.05}s`, opacity: 0, animationFillMode: 'forwards' }}>
                <div className="w-2 h-2 rounded-full bg-violet-400 mt-1.5 shrink-0" />
                <div className="min-w-0">
                  <p style={{ color: 'var(--text-primary)' }} className="truncate">{a.description}</p>
                  <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{formatRelativeTime(a.created_at)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Calls */}
        <div className="card-static p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>Recent Calls</h3>
            <button
              onClick={() => navigate('/calls')}
              className="text-xs font-medium text-violet-600 hover:text-violet-700"
            >
              View all
            </button>
          </div>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {recent_calls.length === 0 && (
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No calls yet</p>
            )}
            {recent_calls.slice(0, 8).map(c => (
              <div
                key={c.id}
                className="flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all duration-200"
                style={{ background: 'var(--bg-tertiary)' }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'var(--border-color)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'var(--bg-tertiary)'}
                onClick={() => navigate(`/calls/${c.id}`)}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0" style={{ background: c.direction === 'inbound' ? 'rgba(59,130,246,0.1)' : 'rgba(99,102,241,0.1)' }}>
                    {c.direction === 'inbound' ? <PhoneIncoming size={14} className="text-blue-500" /> : <PhoneOutgoing size={14} className="text-violet-500" />}
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>{c.lead_name || 'Unknown'}</p>
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{c.direction} · {formatDuration(c.duration_seconds)}</p>
                  </div>
                </div>
                <StatusBadge value={c.outcome} />
              </div>
            ))}
          </div>
        </div>

        {/* Hot Leads */}
        <div className="card-static p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>Hot Leads</h3>
            <button
              onClick={() => navigate('/leads')}
              className="text-xs font-medium text-violet-600 hover:text-violet-700"
            >
              View all
            </button>
          </div>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {hot_leads.length === 0 && (
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No hot leads</p>
            )}
            {hot_leads.slice(0, 8).map(l => (
              <div
                key={l.id}
                className="flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all duration-200"
                style={{ background: 'var(--bg-tertiary)' }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'var(--border-color)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'var(--bg-tertiary)'}
                onClick={() => navigate(`/leads/${l.id}`)}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 bg-gradient-to-br from-violet-400 to-blue-400 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0">
                    {l.name?.[0] || '?'}
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>{l.name}</p>
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{l.phone}</p>
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <div className="flex items-center gap-1">
                    <Flame size={12} className="text-red-500" />
                    <span className="text-sm font-bold text-red-500">{l.score}</span>
                  </div>
                  <StatusBadge value={l.status} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Upcoming Appointments */}
      <div className="card-static p-5 animate-fade-in">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>Upcoming Appointments</h3>
          <button
            onClick={() => navigate('/appointments')}
            className="text-xs font-medium text-violet-600 hover:text-violet-700"
          >
            View calendar
          </button>
        </div>
        {upcoming_appointments.length === 0 ? (
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No upcoming appointments</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {upcoming_appointments.map(a => (
              <div
                key={a.id}
                className="p-4 rounded-xl border transition-all duration-200"
                style={{ background: 'var(--bg-tertiary)', borderColor: 'var(--border-color)' }}
              >
                <div className="flex items-start justify-between mb-2">
                  <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{a.title}</p>
                  <StatusBadge value={a.status} />
                </div>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>{a.customer_name}</p>
                <div className="flex items-center gap-2 mt-2">
                  <Calendar size={12} style={{ color: 'var(--text-muted)' }} />
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{formatTime(a.start_time)}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

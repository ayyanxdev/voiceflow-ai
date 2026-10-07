import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import api from '../services/api';
import AnimatedCounter from '../components/AnimatedCounter';

const dateRanges = [
  { label: '7D', value: 7 },
  { label: '14D', value: 14 },
  { label: '30D', value: 30 },
];

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

export default function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState(30);

  useEffect(() => {
    setLoading(true);
    api.getDashboard().then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex justify-center py-12"><Loader2 size={28} className="animate-spin text-violet-500" /></div>;
  if (!data) return <div className="text-center py-12" style={{ color: 'var(--text-muted)' }}>Failed to load analytics</div>;

  const { overview, charts } = data;
  const visibleCalls = charts.calls_over_time.slice(-dateRange);
  const COLORS = ['#c94978', '#8a72b5', '#e7a06b', '#719bbd', '#7c9c87', '#dd7d91', '#c5a45b'];

  const funnelData = charts.lead_funnel.map(f => ({
    name: f.stage.replace(/_/g, ' '),
    value: f.count,
  }));

  const rateMetrics = [
    { name: 'Answer Rate', value: overview.total_calls > 0 ? ((overview.answered_calls / overview.total_calls) * 100).toFixed(1) : 0, color: 'text-blue-600', bg: 'rgba(59, 130, 246, 0.1)' },
    { name: 'Qualification Rate', value: overview.total_leads > 0 ? ((overview.qualified_leads / overview.total_leads) * 100).toFixed(1) : 0, color: 'text-rose-600', bg: 'rgba(201, 73, 120, 0.1)' },
    { name: 'Appointment Rate', value: overview.total_calls > 0 ? ((overview.appointments_booked / overview.total_calls) * 100).toFixed(1) : 0, color: 'text-violet-600', bg: 'rgba(99, 102, 241, 0.1)' },
    { name: 'Conversion Rate', value: overview.conversion_rate, color: 'text-amber-600', bg: 'rgba(245, 158, 11, 0.1)' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold gradient-text">Analytics</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>Performance metrics and insights</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border-color)', background: 'var(--bg-secondary)' }}>
            {dateRanges.map(r => (
              <button
                key={r.value}
                onClick={() => setDateRange(r.value)}
                aria-pressed={dateRange === r.value}
                className={`px-3 py-1.5 text-xs font-medium transition-all ${
                  dateRange === r.value ? 'bg-rose-600 text-white' : ''
                }`}
                style={dateRange !== r.value ? { color: 'var(--text-secondary)' } : {}}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 animate-fade-in stagger-1" style={{ opacity: 0, animationFillMode: 'forwards' }}>
        {rateMetrics.map(m => (
          <div key={m.name} className="card-static p-5 text-center">
            <p className={`text-3xl font-bold ${m.color}`}><AnimatedCounter value={parseFloat(m.value)} suffix="%" /></p>
            <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>{m.name}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 animate-fade-in stagger-2" style={{ opacity: 0, animationFillMode: 'forwards' }}>
        {[
          { label: 'Total Calls', value: overview.total_calls, color: 'text-violet-600' },
          { label: 'Total Leads', value: overview.total_leads, color: 'text-blue-600' },
          { label: 'Hot Leads', value: overview.hot_leads, color: 'text-red-500' },
          { label: 'Avg Duration', value: `${Math.round(overview.avg_call_duration)}s`, color: 'text-emerald-600' },
        ].map(s => (
          <div key={s.label} className="card-static p-4 text-center">
            <p className={`text-2xl font-bold ${s.color}`}>
              {typeof s.value === 'number' ? <AnimatedCounter value={s.value} /> : s.value}
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{s.label}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        <div className="card-static p-5 animate-fade-in stagger-3" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Calls Over Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={visibleCalls}>
              <defs>
                <linearGradient id="analyticsColor" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#c94978" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#c94978" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: 'var(--text-muted)' }} tickFormatter={v => v.slice(5)} />
              <YAxis tick={{ fontSize: 10, fill: 'var(--text-muted)' }} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="count" name="Calls" stroke="#c94978" fill="url(#analyticsColor)" strokeWidth={2} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card-static p-5 animate-fade-in stagger-4" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Call Outcomes</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={charts.call_outcomes} barCategoryGap="20%">
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis dataKey="outcome" tick={{ fontSize: 9, fill: 'var(--text-muted)' }} />
              <YAxis tick={{ fontSize: 10, fill: 'var(--text-muted)' }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" name="Count" radius={[6, 6, 0, 0]}>
                {charts.call_outcomes.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card-static p-5 animate-fade-in stagger-5" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Inbound vs Outbound</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={charts.inbound_vs_outbound}
                dataKey="count"
                nameKey="outcome"
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={100}
                paddingAngle={4}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {charts.inbound_vs_outbound.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card-static p-5 animate-fade-in stagger-6" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Lead Funnel</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={funnelData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis type="number" tick={{ fontSize: 10, fill: 'var(--text-muted)' }} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: 'var(--text-muted)' }} width={100} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" name="Count" radius={[0, 6, 6, 0]}>
                {funnelData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

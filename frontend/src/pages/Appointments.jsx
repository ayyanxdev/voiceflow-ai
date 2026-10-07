import { useState, useEffect } from 'react';
import { Calendar, Loader2, Search, LayoutGrid, List, Download } from 'lucide-react';
import api from '../services/api';
import StatusBadge from '../components/StatusBadge';
import CalendarView from '../components/CalendarView';

function formatTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
}

export default function Appointments() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [viewMode, setViewMode] = useState('calendar');

  useEffect(() => {
    setLoading(true);
    const params = {};
    if (statusFilter) params.status = statusFilter;
    if (search) params.search = search;
    api.getAppointments(params).then(setAppointments).catch(console.error).finally(() => setLoading(false));
  }, [statusFilter, search]);

  const handleStatus = async (id, status) => {
    try {
      await api.updateAppointment(id, { status });
      setAppointments(prev => prev.map(a => a.id === id ? { ...a, status } : a));
    } catch (err) { alert(err.message); }
  };

  const handleAppointmentClick = (appointment) => {
    // Could open a detail modal here
    console.log('Clicked appointment:', appointment);
  };

  const handleExport = () => api.exportAppointments({ status: statusFilter }).catch(err => alert('Export failed: ' + err.message));

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold gradient-text">Appointments</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>Manage upcoming and past appointments</p>
        </div>
        <button onClick={handleExport} className="btn-secondary flex items-center gap-2 text-sm">
          <Download size={14} /> Export
        </button>
      </div>

      {/* Filters & View Toggle */}
      <div className="flex flex-wrap items-center gap-3 animate-fade-in stagger-1" style={{ opacity: 0, animationFillMode: 'forwards' }}>
        <div className="relative flex-1 min-w-[200px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search appointments..."
            className="input-modern pl-9 pr-4 py-2"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input-modern w-auto"
        >
          <option value="">All Statuses</option>
          {['scheduled', 'confirmed', 'completed', 'cancelled', 'rescheduled', 'no_show'].map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <div className="flex rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border-color)' }}>
          <button
            onClick={() => setViewMode('calendar')}
            className={`p-2 transition-all ${viewMode === 'calendar' ? 'bg-violet-600 text-white' : ''}`}
            style={viewMode !== 'calendar' ? { color: 'var(--text-secondary)' } : {}}
            title="Calendar view"
          >
            <LayoutGrid size={16} />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 transition-all ${viewMode === 'list' ? 'bg-violet-600 text-white' : ''}`}
            style={viewMode !== 'list' ? { color: 'var(--text-secondary)' } : {}}
            title="List view"
          >
            <List size={16} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 size={28} className="animate-spin text-violet-500" /></div>
      ) : appointments.length === 0 ? (
        <div className="text-center py-16 animate-fade-in">
          <Calendar size={48} className="mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
          <p className="text-lg font-medium" style={{ color: 'var(--text-secondary)' }}>No appointments found</p>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>Appointments booked via the AI agent will appear here</p>
        </div>
      ) : viewMode === 'calendar' ? (
        <CalendarView appointments={appointments} onAppointmentClick={handleAppointmentClick} />
      ) : (
        /* List View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {appointments.map((a, i) => (
            <div
              key={a.id}
              className="card p-5 animate-fade-in"
              style={{ animationDelay: `${i * 0.05}s`, opacity: 0, animationFillMode: 'forwards' }}
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{a.title}</h3>
                <StatusBadge value={a.status} />
              </div>
              <div className="space-y-2 text-sm">
                <p style={{ color: 'var(--text-secondary)' }}>{a.customer_name || '—'}</p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{a.customer_phone || ''}</p>
                <div className="pt-2 border-t" style={{ borderColor: 'var(--border-color)' }}>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{formatTime(a.start_time)}</p>
                  {a.end_time && <p className="text-xs" style={{ color: 'var(--text-muted)' }}>to {formatTime(a.end_time)}</p>}
                </div>
              </div>
              {a.status === 'scheduled' && (
                <div className="mt-3 flex gap-2">
                  <button onClick={() => handleStatus(a.id, 'confirmed')} className="px-3 py-1 text-xs bg-emerald-50 text-emerald-700 rounded-lg hover:bg-emerald-100 transition-colors font-medium">
                    Confirm
                  </button>
                  <button onClick={() => handleStatus(a.id, 'cancelled')} className="px-3 py-1 text-xs bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors font-medium">
                    Cancel
                  </button>
                </div>
              )}
              {a.status === 'confirmed' && (
                <div className="mt-3">
                  <button onClick={() => handleStatus(a.id, 'completed')} className="px-3 py-1 text-xs bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors font-medium">
                    Mark Completed
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Loader2, Search, Plus, X, Download, Flame, LayoutGrid, List } from 'lucide-react';
import api from '../services/api';
import StatusBadge from '../components/StatusBadge';
import AnimatedCounter from '../components/AnimatedCounter';
import { SkeletonTable } from '../components/Skeleton';
import KanbanBoard from '../components/KanbanBoard';

function formatTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function Leads() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [tempFilter, setTempFilter] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ first_name: '', last_name: '', phone: '', email: '', company: '', source: 'manual', notes: '' });
  const [saving, setSaving] = useState(false);
  const [viewMode, setViewMode] = useState('kanban');
  const navigate = useNavigate();

  const fetchLeads = () => {
    setLoading(true);
    const params = {};
    if (search) params.search = search;
    if (statusFilter) params.status = statusFilter;
    if (tempFilter) params.temperature = tempFilter;
    api.getLeads(params).then(setLeads).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetchLeads(); }, [search, statusFilter, tempFilter]);

  const handleAdd = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.createLead(form);
      setShowAdd(false);
      setForm({ first_name: '', last_name: '', phone: '', email: '', company: '', source: 'manual', notes: '' });
      fetchLeads();
    } catch (err) { alert(err.message); }
    setSaving(false);
  };

  const handleLeadUpdate = async (leadId, updates) => {
    try {
      await api.updateLead(leadId, updates);
      setLeads(prev => prev.map(l => l.id === leadId ? { ...l, ...updates } : l));
    } catch (err) {
      console.error('Failed to update lead:', err);
    }
  };

  const stats = {
    total: leads.length,
    hot: leads.filter(l => l.temperature === 'hot').length,
    qualified: leads.filter(l => l.status === 'qualified' || l.status === 'appointment_booked').length,
    avgScore: leads.length > 0 ? Math.round(leads.reduce((a, l) => a + l.qualification_score, 0) / leads.length) : 0,
  };

  const handleExport = () => api.exportLeads({ status: statusFilter, temperature: tempFilter }).catch(err => alert('Export failed: ' + err.message));

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold gradient-text">Leads</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>Manage your lead pipeline</p>
        </div>
        <div className="flex gap-2">
          <button onClick={handleExport} className="btn-secondary flex items-center gap-2 text-sm">
            <Download size={14} /> Export
          </button>
          <button onClick={() => setShowAdd(true)} className="btn-primary flex items-center gap-2 text-sm">
            <Plus size={14} /> Add Lead
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 animate-fade-in stagger-1" style={{ opacity: 0, animationFillMode: 'forwards' }}>
        {[
          { label: 'Total Leads', value: stats.total, color: 'text-violet-600' },
          { label: 'Hot Leads', value: stats.hot, color: 'text-red-500' },
          { label: 'Qualified', value: stats.qualified, color: 'text-emerald-600' },
          { label: 'Avg Score', value: stats.avgScore, color: 'text-amber-600' },
        ].map(s => (
          <div key={s.label} className="card-static p-4 text-center">
            <p className={`text-2xl font-bold ${s.color}`}>
              {typeof s.value === 'number' ? <AnimatedCounter value={s.value} /> : s.value}
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{s.label}</p>
          </div>
        ))}
      </div>

      {/* Filters & View Toggle */}
      <div className="flex flex-wrap items-center gap-3 animate-fade-in stagger-2" style={{ opacity: 0, animationFillMode: 'forwards' }}>
        <div className="relative flex-1 min-w-[200px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search leads..."
            className="input-modern pl-9 pr-4 py-2"
          />
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="input-modern w-auto">
          <option value="">All Statuses</option>
          {['new', 'contacted', 'qualified', 'unqualified', 'appointment_booked', 'follow_up', 'converted', 'lost'].map(s => (
            <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
          ))}
        </select>
        <select value={tempFilter} onChange={(e) => setTempFilter(e.target.value)} className="input-modern w-auto">
          <option value="">All Temperatures</option>
          <option value="hot">🔥 Hot</option>
          <option value="warm">🌤 Warm</option>
          <option value="cold">❄️ Cold</option>
        </select>
        <div className="flex rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border-color)' }}>
          <button
            onClick={() => setViewMode('kanban')}
            className={`p-2 transition-all ${viewMode === 'kanban' ? 'bg-violet-600 text-white' : ''}`}
            style={viewMode !== 'kanban' ? { color: 'var(--text-secondary)' } : {}}
            title="Kanban view"
          >
            <LayoutGrid size={16} />
          </button>
          <button
            onClick={() => setViewMode('table')}
            className={`p-2 transition-all ${viewMode === 'table' ? 'bg-violet-600 text-white' : ''}`}
            style={viewMode !== 'table' ? { color: 'var(--text-secondary)' } : {}}
            title="Table view"
          >
            <List size={16} />
          </button>
        </div>
      </div>

      {/* Add Lead Modal */}
      {showAdd && (
        <div className="fixed inset-0 flex items-center justify-center z-50 p-4" style={{ background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(4px)' }} onClick={() => setShowAdd(false)}>
          <div className="w-full max-w-lg shadow-2xl animate-scale-in" style={{ background: 'var(--bg-secondary)', borderRadius: 20 }} onClick={(e) => e.stopPropagation()}>
            <div className="p-6 border-b" style={{ borderColor: 'var(--border-color)' }}>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Add New Lead</h2>
                <button onClick={() => setShowAdd(false)} className="p-1.5 rounded-lg transition-colors" style={{ color: 'var(--text-muted)' }} onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-tertiary)'} onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
                  <X size={18} />
                </button>
              </div>
            </div>
            <form onSubmit={handleAdd} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <input placeholder="First Name *" value={form.first_name} onChange={e => setForm({...form, first_name: e.target.value})} required className="input-modern" />
                <input placeholder="Last Name" value={form.last_name} onChange={e => setForm({...form, last_name: e.target.value})} className="input-modern" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <input placeholder="Phone" value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} className="input-modern" />
                <input placeholder="Email" type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} className="input-modern" />
              </div>
              <input placeholder="Company" value={form.company} onChange={e => setForm({...form, company: e.target.value})} className="input-modern" />
              <select value={form.source} onChange={e => setForm({...form, source: e.target.value})} className="input-modern">
                <option value="manual">Manual</option>
                <option value="inbound_call">Inbound Call</option>
                <option value="outbound">Outbound</option>
                <option value="website">Website</option>
                <option value="import">Import</option>
              </select>
              <textarea placeholder="Notes" value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} rows={2} className="input-modern resize-none" />
              <div className="flex gap-3 justify-end pt-2">
                <button type="button" onClick={() => setShowAdd(false)} className="btn-secondary text-sm">Cancel</button>
                <button type="submit" disabled={saving} className="btn-primary text-sm">
                  {saving ? 'Saving...' : 'Create Lead'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Content */}
      {loading ? (
        viewMode === 'kanban' ? (
          <div className="flex gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="w-72 flex-shrink-0">
                <div className="skeleton h-10 rounded-xl mb-3" />
                <div className="space-y-2">
                  {Array.from({ length: 3 }).map((_, j) => (
                    <div key={j} className="skeleton h-32 rounded-xl" />
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="card-static p-5"><SkeletonTable rows={6} cols={7} /></div>
        )
      ) : leads.length === 0 ? (
        <div className="text-center py-16 animate-fade-in">
          <Users size={48} className="mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
          <p className="text-lg font-medium" style={{ color: 'var(--text-secondary)' }}>No leads found</p>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>Add leads manually or they'll be created from calls</p>
        </div>
      ) : viewMode === 'kanban' ? (
        <KanbanBoard leads={leads} onLeadUpdate={handleLeadUpdate} />
      ) : (
        <div className="card-static overflow-hidden animate-fade-in stagger-3" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b" style={{ borderColor: 'var(--border-color)', background: 'var(--bg-tertiary)' }}>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Name</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Contact</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Source</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Status</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Temp</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Score</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Created</th>
                </tr>
              </thead>
              <tbody className="divide-y" style={{ borderColor: 'var(--border-color)' }}>
                {leads.map((l) => (
                  <tr
                    key={l.id}
                    className="cursor-pointer transition-colors"
                    onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-tertiary)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                    onClick={() => navigate(`/leads/${l.id}`)}
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 bg-gradient-to-br from-violet-400 to-blue-400 rounded-xl flex items-center justify-center text-white text-xs font-bold shrink-0">
                          {l.first_name?.[0]}{l.last_name?.[0] || ''}
                        </div>
                        <div>
                          <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{l.first_name} {l.last_name || ''}</p>
                          {l.company && <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{l.company}</p>}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>{l.phone || '—'}</div>
                      <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{l.email || ''}</div>
                    </td>
                    <td className="px-4 py-3 text-xs capitalize font-medium" style={{ color: 'var(--text-secondary)' }}>{(l.source || '').replace(/_/g, ' ')}</td>
                    <td className="px-4 py-3"><StatusBadge value={l.status} /></td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1">
                        {l.temperature === 'hot' && <Flame size={12} className="text-red-500" />}
                        <StatusBadge value={l.temperature} />
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-sm font-bold ${l.qualification_score >= 70 ? 'text-emerald-600' : l.qualification_score >= 40 ? 'text-amber-600' : 'text-slate-500'}`}>
                        {l.qualification_score}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm" style={{ color: 'var(--text-muted)' }}>{formatTime(l.created_at)}</td>
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

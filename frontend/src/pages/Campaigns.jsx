import { useState, useEffect } from 'react';
import { Megaphone, Loader2, Plus, X } from 'lucide-react';
import api from '../services/api';
import StatusBadge from '../components/StatusBadge';

function formatTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ name: '', description: '' });
  const [saving, setSaving] = useState(false);

  const fetchCampaigns = () => {
    setLoading(true);
    api.getCampaigns().then(setCampaigns).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetchCampaigns(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.createCampaign(form);
      setShowAdd(false);
      setForm({ name: '', description: '' });
      fetchCampaigns();
    } catch (err) { alert(err.message); }
    setSaving(false);
  };

  const handleStatusChange = async (id, status) => {
    try {
      await api.updateCampaign(id, { status });
      fetchCampaigns();
    } catch (err) { alert(err.message); }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold gradient-text">Campaigns</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>Manage outbound calling campaigns</p>
        </div>
        <button onClick={() => setShowAdd(true)} className="flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-500 text-sm font-medium">
          <Plus size={16} /> New Campaign
        </button>
      </div>

      {showAdd && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" onClick={() => setShowAdd(false)}>
          <div className="rounded-2xl p-6 w-full max-w-md shadow-2xl" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }} onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Create Campaign</h2>
              <button onClick={() => setShowAdd(false)} className="p-1 rounded-lg transition-colors" style={{ color: 'var(--text-muted)' }} onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-tertiary)'} onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}><X size={18} /></button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3">
              <input placeholder="Campaign Name *" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required className="input-modern px-3 py-2 text-sm" />
              <textarea placeholder="Description" value={form.description} onChange={e => setForm({...form, description: e.target.value})} rows={3} className="input-modern px-3 py-2 text-sm resize-none" />
              <div className="flex gap-3 justify-end">
                <button type="button" onClick={() => setShowAdd(false)} className="btn-secondary px-4 py-2 text-sm">Cancel</button>
                <button type="submit" disabled={saving} className="btn-primary px-4 py-2 text-sm disabled:opacity-50">{saving ? 'Creating...' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 size={28} className="animate-spin text-violet-500" /></div>
      ) : campaigns.length === 0 ? (
        <div className="text-center py-12 text-slate-400">
          <Megaphone size={40} className="mx-auto mb-3 text-slate-300" />
          <p>No campaigns yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {campaigns.map(c => (
            <div key={c.id} className="card p-5">
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>{c.name}</h3>
                <StatusBadge value={c.status} />
              </div>
              {c.description && <p className="text-sm mb-3 line-clamp-2" style={{ color: 'var(--text-muted)' }}>{c.description}</p>}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="text-center p-2 rounded-lg" style={{ background: 'var(--bg-tertiary)' }}>
                  <p className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>{c.total_leads}</p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Leads</p>
                </div>
                <div className="text-center p-2 rounded-lg" style={{ background: 'var(--bg-tertiary)' }}>
                  <p className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>{c.completed_calls}</p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Calls</p>
                </div>
                <div className="text-center p-2 rounded-lg" style={{ background: 'var(--bg-tertiary)' }}>
                  <p className="text-lg font-bold text-green-600">{c.qualified_leads}</p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Qualified</p>
                </div>
                <div className="text-center p-2 rounded-lg" style={{ background: 'var(--bg-tertiary)' }}>
                  <p className="text-lg font-bold text-blue-600">{c.appointments}</p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Appointments</p>
                </div>
              </div>
              <div className="flex gap-2">
                {c.status === 'draft' && <button onClick={() => handleStatusChange(c.id, 'active')} className="px-3 py-1 text-xs bg-green-50 text-green-700 rounded-lg hover:bg-green-100">Start</button>}
                {c.status === 'active' && <button onClick={() => handleStatusChange(c.id, 'paused')} className="px-3 py-1 text-xs bg-amber-50 text-amber-700 rounded-lg hover:bg-amber-100">Pause</button>}
                {c.status === 'paused' && <button onClick={() => handleStatusChange(c.id, 'active')} className="px-3 py-1 text-xs bg-green-50 text-green-700 rounded-lg hover:bg-green-100">Resume</button>}
                <p className="text-xs self-center ml-auto" style={{ color: 'var(--text-muted)' }}>{formatTime(c.created_at)}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

import { useState, useEffect } from 'react';
import { Activity, Loader2 } from 'lucide-react';
import api from '../services/api';

function formatTime(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
}

const typeColors = {
  call_received: 'bg-blue-500',
  call_initiated: 'bg-violet-500',
  call_completed: 'bg-green-500',
  lead_created: 'bg-blue-400',
  lead_updated: 'bg-amber-500',
  lead_qualified: 'bg-green-600',
  appointment_booked: 'bg-emerald-500',
  appointment_cancelled: 'bg-red-400',
  appointment_completed: 'bg-green-500',
  appointment_confirmed: 'bg-green-400',
  campaign_started: 'bg-violet-400',
  campaign_completed: 'bg-green-600',
  campaign_active: 'bg-green-500',
  campaign_paused: 'bg-amber-400',
  campaign_created: 'bg-slate-500',
  follow_up_scheduled: 'bg-amber-500',
  crm_sync: 'bg-slate-400',
  webhook_received: 'bg-violet-400',
};

export default function ActivityPage() {
  const [activities, setActivities] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [typeFilter, setTypeFilter] = useState('');

  useEffect(() => {
    setLoading(true);
    const params = {};
    if (typeFilter) params.type = typeFilter;
    api.getActivity(params).then(d => { setActivities(d.items); setTotal(d.total); }).catch(console.error).finally(() => setLoading(false));
  }, [typeFilter]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold gradient-text">Activity Log</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>{total} total activities</p>
      </div>

      <div className="flex gap-3">
        <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)} className="input-modern px-3 py-2 text-sm w-auto">
          <option value="">All Types</option>
          {Object.keys(typeColors).sort().map(t => (
            <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 size={28} className="animate-spin text-violet-500" /></div>
      ) : activities.length === 0 ? (
        <div className="text-center py-12 text-slate-400">
          <Activity size={40} className="mx-auto mb-3 text-slate-300" />
          <p>No activity yet</p>
        </div>
      ) : (
        <div className="card-static p-5">
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-[19px] top-0 bottom-0 w-px" style={{ background: 'var(--border-color)' }} />

            <div className="space-y-4">
              {activities.map((a) => (
                <div key={a.id} className="flex items-start gap-4">
                  <div className={`w-[10px] h-[10px] rounded-full mt-1.5 shrink-0 ${typeColors[a.type] || 'bg-slate-400'} ring-4 relative z-10`} style={{ '--tw-ring-color': 'var(--bg-primary)' }} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm" style={{ color: 'var(--text-primary)' }}>{a.description}</p>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{formatTime(a.created_at)}</span>
                      <span className="text-xs capitalize" style={{ color: 'var(--text-muted)' }}>{(a.type || '').replace(/_/g, ' ')}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

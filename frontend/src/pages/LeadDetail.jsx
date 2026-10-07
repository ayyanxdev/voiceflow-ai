import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Phone, Mail, Building, Loader2, Edit2 } from 'lucide-react';
import api from '../services/api';
import StatusBadge from '../components/StatusBadge';

function formatTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString();
}

export default function LeadDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [lead, setLead] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});

  useEffect(() => {
    api.getLead(id).then(l => { setLead(l); setForm(l); }).catch(console.error).finally(() => setLoading(false));
  }, [id]);

  const handleSave = async () => {
    try {
      const updated = await api.updateLead(id, form);
      setLead(updated);
      setEditing(false);
    } catch (err) { alert(err.message); }
  };

  if (loading) return <div className="flex justify-center py-12"><Loader2 size={28} className="animate-spin text-violet-500" /></div>;
  if (!lead) return <div className="text-center py-12 text-slate-400">Lead not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/leads')} className="p-2 hover:bg-slate-100 rounded-lg"><ArrowLeft size={20} className="text-slate-600" /></button>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{lead.first_name} {lead.last_name || ''}</h1>
            <p className="text-sm text-slate-500">Lead #{lead.id} · {lead.source}</p>
          </div>
        </div>
        <button onClick={() => setEditing(!editing)} className="flex items-center gap-2 px-3 py-1.5 text-sm border border-slate-200 rounded-lg hover:bg-slate-50">
          <Edit2 size={14} /> {editing ? 'Cancel' : 'Edit'}
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-slate-200">
          <p className="text-xs text-slate-400 mb-1">Status</p>
          <StatusBadge value={lead.status} />
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-200">
          <p className="text-xs text-slate-400 mb-1">Temperature</p>
          <StatusBadge value={lead.temperature} />
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-200">
          <p className="text-xs text-slate-400 mb-1">Score</p>
          <p className={`text-2xl font-bold ${lead.qualification_score >= 70 ? 'text-green-600' : lead.qualification_score >= 40 ? 'text-amber-600' : 'text-slate-500'}`}>
            {lead.qualification_score}
          </p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-200">
          <p className="text-xs text-slate-400 mb-1">Source</p>
          <p className="text-sm font-medium text-slate-700 capitalize">{(lead.source || '').replace(/_/g, ' ')}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
          <h3 className="font-semibold text-slate-900 mb-4">Contact Information</h3>
          {editing ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <input value={form.first_name || ''} onChange={e => setForm({...form, first_name: e.target.value})} className="px-3 py-2 border rounded-lg text-sm" placeholder="First Name" />
                <input value={form.last_name || ''} onChange={e => setForm({...form, last_name: e.target.value})} className="px-3 py-2 border rounded-lg text-sm" placeholder="Last Name" />
              </div>
              <input value={form.phone || ''} onChange={e => setForm({...form, phone: e.target.value})} className="w-full px-3 py-2 border rounded-lg text-sm" placeholder="Phone" />
              <input value={form.email || ''} onChange={e => setForm({...form, email: e.target.value})} className="w-full px-3 py-2 border rounded-lg text-sm" placeholder="Email" />
              <input value={form.company || ''} onChange={e => setForm({...form, company: e.target.value})} className="w-full px-3 py-2 border rounded-lg text-sm" placeholder="Company" />
              <div className="grid grid-cols-2 gap-3">
                <select value={form.status || 'new'} onChange={e => setForm({...form, status: e.target.value})} className="px-3 py-2 border rounded-lg text-sm">
                  {['new', 'contacted', 'qualified', 'unqualified', 'appointment_booked', 'follow_up', 'converted', 'lost'].map(s => <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>)}
                </select>
                <select value={form.temperature || 'cold'} onChange={e => setForm({...form, temperature: e.target.value})} className="px-3 py-2 border rounded-lg text-sm">
                  <option value="cold">Cold</option><option value="warm">Warm</option><option value="hot">Hot</option>
                </select>
              </div>
              <textarea value={form.notes || ''} onChange={e => setForm({...form, notes: e.target.value})} rows={3} className="w-full px-3 py-2 border rounded-lg text-sm resize-none" placeholder="Notes" />
              <button onClick={handleSave} className="px-4 py-2 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-500">Save Changes</button>
            </div>
          ) : (
            <dl className="space-y-3">
              <div className="flex items-center gap-3"><User size={16} className="text-slate-400" /><span className="text-sm text-slate-700">{lead.first_name} {lead.last_name || ''}</span></div>
              <div className="flex items-center gap-3"><Phone size={16} className="text-slate-400" /><span className="text-sm text-slate-700">{lead.phone || '—'}</span></div>
              <div className="flex items-center gap-3"><Mail size={16} className="text-slate-400" /><span className="text-sm text-slate-700">{lead.email || '—'}</span></div>
              <div className="flex items-center gap-3"><Building size={16} className="text-slate-400" /><span className="text-sm text-slate-700">{lead.company || '—'}</span></div>
            </dl>
          )}
        </div>

        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
          <h3 className="font-semibold text-slate-900 mb-4">Notes</h3>
          <p className="text-sm text-slate-600 whitespace-pre-wrap">{lead.notes || 'No notes'}</p>
          <div className="mt-4 pt-4 border-t border-slate-100">
            <p className="text-xs text-slate-400">Created: {formatTime(lead.created_at)}</p>
            <p className="text-xs text-slate-400">Updated: {formatTime(lead.updated_at)}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

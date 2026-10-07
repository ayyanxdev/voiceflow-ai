import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GripVertical, Flame, Phone, Mail, Building } from 'lucide-react';
import StatusBadge from './StatusBadge';

const columns = [
  { id: 'new', label: 'New', color: '#3b82f6', bgColor: 'rgba(59, 130, 246, 0.08)' },
  { id: 'contacted', label: 'Contacted', color: '#f59e0b', bgColor: 'rgba(245, 158, 11, 0.08)' },
  { id: 'qualified', label: 'Qualified', color: '#10b981', bgColor: 'rgba(16, 185, 129, 0.08)' },
  { id: 'appointment_booked', label: 'Appointment', color: '#6366f1', bgColor: 'rgba(99, 102, 241, 0.08)' },
  { id: 'converted', label: 'Converted', color: '#8b5cf6', bgColor: 'rgba(139, 92, 246, 0.08)' },
  { id: 'lost', label: 'Lost', color: '#ef4444', bgColor: 'rgba(239, 68, 68, 0.08)' },
];

export default function KanbanBoard({ leads = [], onLeadUpdate }) {
  const navigate = useNavigate();
  const [draggedLead, setDraggedLead] = useState(null);

  const getLeadsForColumn = (status) => {
    return leads.filter(l => l.status === status);
  };

  const handleDragStart = (e, lead) => {
    setDraggedLead(lead);
    e.dataTransfer.effectAllowed = 'move';
    e.currentTarget.style.opacity = '0.5';
  };

  const handleDragEnd = (e) => {
    e.currentTarget.style.opacity = '1';
    setDraggedLead(null);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e, targetStatus) => {
    e.preventDefault();
    if (draggedLead && draggedLead.status !== targetStatus) {
      onLeadUpdate?.(draggedLead.id, { status: targetStatus });
    }
    setDraggedLead(null);
  };

  const scoreColor = (score) => {
    if (score >= 70) return 'text-emerald-600';
    if (score >= 40) return 'text-amber-600';
    return 'text-slate-500';
  };

  return (
    <div className="flex gap-4 overflow-x-auto pb-4" style={{ minHeight: 500 }}>
      {columns.map(col => {
        const columnLeads = getLeadsForColumn(col.id);
        return (
          <div
            key={col.id}
            className="flex-shrink-0 w-72 rounded-xl border flex flex-col"
            style={{ borderColor: 'var(--border-color)', background: 'var(--bg-secondary)' }}
            onDragOver={handleDragOver}
            onDrop={(e) => handleDrop(e, col.id)}
          >
            {/* Column Header */}
            <div className="p-3 border-b flex items-center justify-between" style={{ borderColor: 'var(--border-color)', background: col.bgColor }}>
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full" style={{ background: col.color }} />
                <h3 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{col.label}</h3>
              </div>
              <span className="text-xs px-2 py-0.5 rounded-full font-medium" style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)' }}>
                {columnLeads.length}
              </span>
            </div>

            {/* Cards */}
            <div className="flex-1 p-2 space-y-2 overflow-y-auto">
              {columnLeads.length === 0 ? (
                <div className="text-center py-8 text-xs" style={{ color: 'var(--text-muted)' }}>
                  Drop leads here
                </div>
              ) : (
                columnLeads.map(lead => (
                  <div
                    key={lead.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, lead)}
                    onDragEnd={handleDragEnd}
                    className="p-3 rounded-xl border cursor-grab active:cursor-grabbing transition-all hover:shadow-md"
                    style={{ borderColor: 'var(--border-color)', background: 'var(--bg-secondary)' }}
                    onClick={() => navigate(`/leads/${lead.id}`)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 bg-gradient-to-br from-violet-400 to-blue-400 rounded-lg flex items-center justify-center text-white text-xs font-bold shrink-0">
                          {lead.first_name?.[0]}{lead.last_name?.[0] || ''}
                        </div>
                        <div>
                          <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                            {lead.first_name} {lead.last_name || ''}
                          </p>
                        </div>
                      </div>
                      <GripVertical size={14} style={{ color: 'var(--text-muted)' }} className="shrink-0 mt-1" />
                    </div>

                    {lead.company && (
                      <div className="flex items-center gap-1 mb-1">
                        <Building size={10} style={{ color: 'var(--text-muted)' }} />
                        <p className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>{lead.company}</p>
                      </div>
                    )}

                    {lead.phone && (
                      <div className="flex items-center gap-1 mb-1">
                        <Phone size={10} style={{ color: 'var(--text-muted)' }} />
                        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{lead.phone}</p>
                      </div>
                    )}

                    <div className="flex items-center justify-between mt-2 pt-2 border-t" style={{ borderColor: 'var(--border-color)' }}>
                      <div className="flex items-center gap-1">
                        {lead.temperature === 'hot' && <Flame size={10} className="text-red-500" />}
                        <StatusBadge value={lead.temperature} />
                      </div>
                      <span className={`text-xs font-bold ${scoreColor(lead.qualification_score)}`}>
                        {lead.qualification_score}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

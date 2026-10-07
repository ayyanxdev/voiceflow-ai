import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Phone, Clock, User, FileText, Loader2, Play, Download, Copy, Check } from 'lucide-react';
import api from '../services/api';
import StatusBadge from '../components/StatusBadge';
import AudioPlayer from '../components/AudioPlayer';

function formatDuration(s) {
  const m = Math.floor(s / 60);
  return `${m}:${(s % 60).toString().padStart(2, '0')}`;
}

function formatTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString();
}

export default function CallDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [call, setCall] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    api.getCall(id).then(setCall).catch(console.error).finally(() => setLoading(false));
  }, [id]);

  const handleCopyTranscript = () => {
    if (call?.transcript) {
      navigator.clipboard.writeText(call.transcript);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) return <div className="flex justify-center py-12"><Loader2 size={28} className="animate-spin text-violet-500" /></div>;
  if (!call) return <div className="text-center py-12" style={{ color: 'var(--text-muted)' }}>Call not found</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 animate-fade-in">
        <button
          onClick={() => navigate('/calls')}
          className="p-2 rounded-xl transition-colors"
          style={{ color: 'var(--text-secondary)' }}
          onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-tertiary)'}
          onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
        >
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Call #{call.id}</h1>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{call.direction} call · {formatTime(call.created_at)}</p>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 animate-fade-in stagger-1" style={{ opacity: 0, animationFillMode: 'forwards' }}>
        {[
          { label: 'Status', value: <StatusBadge value={call.status} /> },
          { label: 'Outcome', value: <StatusBadge value={call.outcome} /> },
          { label: 'Duration', value: formatDuration(call.duration_seconds), bold: true },
          { label: 'Score', value: call.qualification_score, bold: true, color: call.qualification_score >= 70 ? 'text-emerald-600' : call.qualification_score >= 40 ? 'text-amber-600' : 'text-slate-500' },
        ].map(card => (
          <div key={card.label} className="card-static p-4">
            <p className="text-xs mb-1" style={{ color: 'var(--text-muted)' }}>{card.label}</p>
            {typeof card.value === 'string' || card.bold ? (
              <p className={`text-lg font-bold ${card.color || ''}`} style={{ color: card.color ? undefined : 'var(--text-primary)' }}>{card.value}</p>
            ) : card.value}
          </div>
        ))}
      </div>

      {/* Audio Player */}
      {call.recording_url && (
        <div className="animate-fade-in stagger-2" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <AudioPlayer src={call.recording_url} title={`Call Recording #${call.id}`} />
        </div>
      )}

      {/* Details Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Transcript */}
        <div className="card-static p-5 animate-fade-in stagger-3" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
              <FileText size={16} /> Transcript
            </h3>
            {call.transcript && (
              <button
                onClick={handleCopyTranscript}
                className="flex items-center gap-1 text-xs px-2 py-1 rounded-lg transition-colors"
                style={{ color: 'var(--text-muted)' }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-tertiary)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                {copied ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                {copied ? 'Copied!' : 'Copy'}
              </button>
            )}
          </div>
          <div className="rounded-xl p-4 max-h-96 overflow-y-auto" style={{ background: 'var(--bg-tertiary)' }}>
            {call.transcript ? (
              <div className="space-y-3">
                {call.transcript.split('\n').filter(Boolean).map((line, i) => {
                  const isAI = line.startsWith('AI:') || line.startsWith('Agent:');
                  const isCaller = line.startsWith('Caller:') || line.startsWith('Customer:');
                  return (
                    <div key={i} className={`flex ${isAI ? 'justify-start' : 'justify-end'}`}>
                      <div
                        className={`max-w-[85%] px-3 py-2 rounded-xl text-sm ${isAI ? 'rounded-tl-sm' : 'rounded-tr-sm'}`}
                        style={{
                          background: isAI ? 'rgba(99, 102, 241, 0.1)' : 'var(--bg-secondary)',
                          color: 'var(--text-primary)',
                        }}
                      >
                        <p className="text-xs font-semibold mb-1" style={{ color: isAI ? '#6366f1' : 'var(--text-muted)' }}>
                          {isAI ? 'AI Agent' : 'Caller'}
                        </p>
                        <p className="leading-relaxed">{line.replace(/^(AI|Caller|Agent|Customer):\s*/, '')}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No transcript available</p>
            )}
          </div>
        </div>

        {/* AI Summary + Info */}
        <div className="space-y-6">
          <div className="card-static p-5 animate-fade-in stagger-4" style={{ opacity: 0, animationFillMode: 'forwards' }}>
            <h3 className="font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>AI Summary</h3>
            {call.summary ? (
              <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{call.summary}</p>
            ) : (
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No summary available</p>
            )}
          </div>

          <div className="card-static p-5 animate-fade-in stagger-5" style={{ opacity: 0, animationFillMode: 'forwards' }}>
            <h3 className="font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Call Details</h3>
            <dl className="space-y-3">
              {[
                { label: 'Direction', value: call.direction, capitalize: true },
                { label: 'Sentiment', value: call.sentiment || '—', capitalize: true },
                { label: 'Started', value: formatTime(call.started_at) },
                { label: 'Ended', value: formatTime(call.ended_at) },
                { label: 'External ID', value: call.external_call_id || '—', mono: true },
                { label: 'Appointment Booked', value: call.appointment_booked === '1' ? 'Yes ✓' : 'No' },
              ].map(item => (
                <div key={item.label} className="flex justify-between text-sm">
                  <dt style={{ color: 'var(--text-muted)' }}>{item.label}</dt>
                  <dd className={`font-medium ${item.capitalize ? 'capitalize' : ''} ${item.mono ? 'font-mono text-xs' : ''}`} style={{ color: 'var(--text-primary)' }}>
                    {item.value}
                  </dd>
                </div>
              ))}
            </dl>
          </div>

          {call.recording_url && (
            <div className="card-static p-5 animate-fade-in stagger-6" style={{ opacity: 0, animationFillMode: 'forwards' }}>
              <h3 className="font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Recording</h3>
              <a
                href={call.recording_url}
                target="_blank"
                rel="noopener"
                className="flex items-center gap-2 text-sm font-medium text-violet-600 hover:text-violet-700"
              >
                <Download size={14} /> Download recording
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

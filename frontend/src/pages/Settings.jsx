import { useState, useEffect, useRef } from 'react';
import { Settings as SettingsIcon, Loader2, Check, X, Save, Eye, EyeOff, Copy, Bot, Building, Phone, Clock, RefreshCw } from 'lucide-react';
import api from '../services/api';

const defaultPrompt = `# ROLE
You are the AI Receptionist for Elite Roofing. You sound like a friendly, professional human receptionist.

# OPENING
Start every call with:
"Hi, thanks for calling Elite Roofing! This is our AI assistant — how can I help you today?"

# HOW TO COLLECT INFORMATION
Ask one thing at a time. Sound natural.

# BOOKING AN APPOINTMENT
When the caller wants to book:
1. Confirm their name
2. Confirm their phone number
3. Confirm the address
4. Ask for a preferred date and time

# BUSINESS HOURS
Our standard business hours are Monday to Friday, 8 AM to 6 PM.`;

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('integrations');
  const [agentPrompt, setAgentPrompt] = useState(defaultPrompt);
  const [showPrompt, setShowPrompt] = useState(true);
  const [savingPrompt, setSavingPrompt] = useState(false);
  const [promptSaved, setPromptSaved] = useState(false);
  const [businessName, setBusinessName] = useState('Elite Roofing');
  const [businessPhone, setBusinessPhone] = useState('+1 (555) 100-2000');
  const [businessHours, setBusinessHours] = useState('Mon-Fri: 8AM - 6PM');
  const [showApiKey, setShowApiKey] = useState({});
  const textareaRef = useRef(null);

  useEffect(() => {
    api.getSettings().then(setSettings).catch(console.error).finally(() => setLoading(false));
  }, []);

  const handleSavePrompt = async () => {
    setSavingPrompt(true);
    // Simulate save (in real app, this would call an API)
    await new Promise(r => setTimeout(r, 1000));
    setSavingPrompt(false);
    setPromptSaved(true);
    setTimeout(() => setPromptSaved(false), 3000);
  };

  const handleCopyPrompt = () => {
    navigator.clipboard.writeText(agentPrompt);
  };

  if (loading) return <div className="flex justify-center py-12"><Loader2 size={28} className="animate-spin text-violet-500" /></div>;
  if (!settings) return <div className="text-center py-12" style={{ color: 'var(--text-muted)' }}>Failed to load settings</div>;

  const integrations = [
    { name: 'Retell AI', configured: settings.retell_configured, key: 'RETELL_API_KEY', desc: 'Voice AI agent for phone calls', color: 'bg-violet-500' },
    { name: 'Vapi AI', configured: settings.vapi_configured, key: 'VAPI_API_KEY', desc: 'Alternative voice AI provider', color: 'bg-blue-500' },
    { name: 'Google Calendar', configured: settings.google_configured, key: 'GOOGLE_CLIENT_ID', desc: 'Sync appointments with Google', color: 'bg-emerald-500' },
    { name: 'OpenAI', configured: settings.ai_provider_configured, key: 'OPENAI_API_KEY', desc: 'AI-powered call summaries', color: 'bg-amber-500' },
  ];

  const tabs = [
    { id: 'integrations', label: 'Integrations', icon: SettingsIcon },
    { id: 'agent', label: 'AI Agent', icon: Bot },
    { id: 'business', label: 'Business', icon: Building },
  ];

  return (
    <div className="space-y-6">
      <div className="animate-fade-in">
        <h1 className="text-2xl md:text-3xl font-bold gradient-text">Settings</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>Configure your AI receptionist and integrations</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 rounded-xl border animate-fade-in stagger-1" style={{ borderColor: 'var(--border-color)', background: 'var(--bg-tertiary)', opacity: 0, animationFillMode: 'forwards' }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all flex-1 justify-center ${
              activeTab === tab.id ? 'bg-violet-600 text-white shadow-md' : ''
            }`}
            style={activeTab !== tab.id ? { color: 'var(--text-secondary)' } : {}}
          >
            <tab.icon size={16} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Integrations Tab */}
      {activeTab === 'integrations' && (
        <div className="space-y-4 animate-fade-in stagger-2" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <div className="card-static p-6">
            <h2 className="font-semibold text-lg mb-1" style={{ color: 'var(--text-primary)' }}>Connected Services</h2>
            <p className="text-sm mb-5" style={{ color: 'var(--text-muted)' }}>Manage your API keys and service connections</p>
            <div className="space-y-3">
              {integrations.map((intg) => (
                <div key={intg.name} className="flex items-center justify-between p-4 rounded-xl border transition-all" style={{ borderColor: 'var(--border-color)', background: 'var(--bg-tertiary)' }}>
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${intg.color}`}>
                      {intg.configured ? <Check size={18} className="text-white" /> : <X size={18} className="text-white/60" />}
                    </div>
                    <div>
                      <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{intg.name}</p>
                      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{intg.desc}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                      intg.configured ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
                    }`}>
                      {intg.configured ? 'Connected' : 'Offline'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card-static p-6">
            <h2 className="font-semibold text-lg mb-1" style={{ color: 'var(--text-primary)' }}>Environment Variables</h2>
            <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>
              Configure these in your <code className="px-1.5 py-0.5 rounded text-xs" style={{ background: 'var(--bg-tertiary)' }}>backend/.env</code> file
            </p>
            <div className="rounded-xl p-4 font-mono text-xs space-y-2" style={{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>
              <p>APP_ENV=development</p>
              <p>RETELL_API_KEY=<span className="text-emerald-500">••••••••</span></p>
              <p>VAPI_API_KEY=<span className="text-emerald-500">••••••••</span></p>
              <p>GOOGLE_CLIENT_ID=<span className="text-emerald-500">••••••••</span></p>
              <p>GOOGLE_CLIENT_SECRET=<span className="text-emerald-500">••••••••</span></p>
              <p>OPENAI_API_KEY=<span className="text-emerald-500">••••••••</span></p>
            </div>
          </div>
        </div>
      )}

      {/* Agent Config Tab */}
      {activeTab === 'agent' && (
        <div className="space-y-4 animate-fade-in stagger-2" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <div className="card-static p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>AI Agent Prompt</h2>
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Customize how your AI receptionist talks to callers</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopyPrompt}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors"
                  style={{ borderColor: 'var(--border-color)', color: 'var(--text-secondary)' }}
                >
                  <Copy size={12} /> Copy
                </button>
                <button
                  onClick={() => setShowPrompt(!showPrompt)}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors"
                  style={{ borderColor: 'var(--border-color)', color: 'var(--text-secondary)' }}
                >
                  {showPrompt ? <EyeOff size={12} /> : <Eye size={12} />}
                  {showPrompt ? 'Preview' : 'Edit'}
                </button>
              </div>
            </div>

            {/* Prompt Editor */}
            <div className="relative">
              {showPrompt ? (
                <textarea
                  ref={textareaRef}
                  value={agentPrompt}
                  onChange={(e) => setAgentPrompt(e.target.value)}
                  className="w-full h-[500px] p-4 rounded-xl border font-mono text-sm leading-relaxed resize-none focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                  style={{
                    background: 'var(--bg-tertiary)',
                    borderColor: 'var(--border-color)',
                    color: 'var(--text-primary)',
                  }}
                  spellCheck={false}
                />
              ) : (
                <div
                  className="w-full h-[500px] p-4 rounded-xl border overflow-y-auto prose prose-sm max-w-none"
                  style={{
                    background: 'var(--bg-tertiary)',
                    borderColor: 'var(--border-color)',
                    color: 'var(--text-primary)',
                  }}
                >
                  <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">{agentPrompt}</pre>
                </div>
              )}

              {/* Line count */}
              <div className="absolute bottom-3 right-3 text-xs px-2 py-1 rounded-lg" style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)' }}>
                {agentPrompt.split('\n').length} lines · {agentPrompt.length} chars
              </div>
            </div>

            {/* Save Bar */}
            <div className="flex items-center justify-between mt-4 p-3 rounded-xl border" style={{ borderColor: 'var(--border-color)', background: 'var(--bg-tertiary)' }}>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                Changes apply to new calls after saving
              </p>
              <div className="flex items-center gap-3">
                {promptSaved && (
                  <span className="text-xs font-medium text-emerald-600 animate-fade-in flex items-center gap-1">
                    <Check size={14} /> Saved successfully
                  </span>
                )}
                <button
                  onClick={handleSavePrompt}
                  disabled={savingPrompt}
                  className="btn-primary flex items-center gap-2 text-sm"
                >
                  {savingPrompt ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
                  {savingPrompt ? 'Saving...' : 'Save Prompt'}
                </button>
              </div>
            </div>
          </div>

          {/* Quick Templates */}
          <div className="card-static p-6">
            <h2 className="font-semibold text-lg mb-4" style={{ color: 'var(--text-primary)' }}>Quick Templates</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {[
                { name: 'Friendly Receptionist', desc: 'Warm, conversational tone', active: true },
                { name: 'Professional Sales', desc: 'Focused on conversions', active: false },
                { name: 'Emergency Handler', desc: 'Urgent call priority', active: false },
              ].map(t => (
                <button
                  key={t.name}
                  className={`p-4 rounded-xl border text-left transition-all ${t.active ? 'border-violet-500 bg-violet-50 dark:bg-violet-900/10' : ''}`}
                  style={!t.active ? { borderColor: 'var(--border-color)', background: 'var(--bg-tertiary)' } : {}}
                >
                  <p className="text-sm font-semibold" style={{ color: t.active ? '#7c3aed' : 'var(--text-primary)' }}>{t.name}</p>
                  <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{t.desc}</p>
                  {t.active && <span className="text-xs text-violet-600 font-medium mt-2 inline-block">Active</span>}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Business Tab */}
      {activeTab === 'business' && (
        <div className="space-y-4 animate-fade-in stagger-2" style={{ opacity: 0, animationFillMode: 'forwards' }}>
          <div className="card-static p-6">
            <h2 className="font-semibold text-lg mb-4" style={{ color: 'var(--text-primary)' }}>Business Information</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>Business Name</label>
                  <input
                    type="text"
                    value={businessName}
                    onChange={(e) => setBusinessName(e.target.value)}
                    className="input-modern"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>Phone Number</label>
                  <input
                    type="text"
                    value={businessPhone}
                    onChange={(e) => setBusinessPhone(e.target.value)}
                    className="input-modern"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>Business Hours</label>
                <input
                  type="text"
                  value={businessHours}
                  onChange={(e) => setBusinessHours(e.target.value)}
                  className="input-modern"
                />
              </div>
            </div>
          </div>

          <div className="card-static p-6">
            <h2 className="font-semibold text-lg mb-4" style={{ color: 'var(--text-primary)' }}>Phone Numbers</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 rounded-xl border" style={{ borderColor: 'var(--border-color)', background: 'var(--bg-tertiary)' }}>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-violet-500 rounded-xl flex items-center justify-center">
                    <Phone size={18} className="text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>+1 (555) 100-2000</p>
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Main business line · Retell AI</p>
                  </div>
                </div>
                <span className="text-xs px-3 py-1 rounded-full bg-emerald-100 text-emerald-700 font-medium">Active</span>
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button className="btn-primary flex items-center gap-2 text-sm">
              <Save size={14} /> Save Changes
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

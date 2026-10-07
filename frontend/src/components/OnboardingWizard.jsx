import { useState } from 'react';
import { Bot, Phone, Calendar, MessageSquare, Check, ChevronRight, ChevronLeft, Sparkles, Rocket } from 'lucide-react';

const steps = [
  {
    id: 'welcome',
    icon: Sparkles,
    title: 'Welcome to VoiceFlow AI!',
    subtitle: 'Your AI receptionist is ready to be configured',
    description: 'Let\'s set up your AI voice agent in a few simple steps. This will take about 2 minutes.',
  },
  {
    id: 'business',
    icon: Phone,
    title: 'Business Info',
    subtitle: 'Tell us about your business',
    fields: [
      { key: 'businessName', label: 'Business Name', placeholder: 'Elite Roofing', required: true },
      { key: 'phone', label: 'Business Phone', placeholder: '+1 (555) 100-2000', required: true },
      { key: 'industry', label: 'Industry', placeholder: 'Home Services / Roofing', required: false },
    ],
  },
  {
    id: 'hours',
    icon: Calendar,
    title: 'Business Hours',
    subtitle: 'When should the AI answer calls?',
    fields: [
      { key: 'openTime', label: 'Opening Time', type: 'time', defaultValue: '08:00' },
      { key: 'closeTime', label: 'Closing Time', type: 'time', defaultValue: '18:00' },
      { key: 'timezone', label: 'Timezone', type: 'select', options: ['America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles'], defaultValue: 'America/Chicago' },
    ],
  },
  {
    id: 'agent',
    icon: MessageSquare,
    title: 'AI Agent Style',
    subtitle: 'How should your AI receptionist sound?',
    options: [
      { id: 'friendly', label: 'Friendly & Warm', desc: 'Casual, conversational, like a friend', icon: '😊' },
      { id: 'professional', label: 'Professional', desc: 'Polished, business-appropriate tone', icon: '💼' },
      { id: 'sales', label: 'Sales-Focused', desc: 'Persuasive, focused on conversions', icon: '🎯' },
    ],
  },
  {
    id: 'complete',
    icon: Rocket,
    title: 'You\'re All Set!',
    subtitle: 'Your AI receptionist is ready to take calls',
    description: 'Your AI agent is now configured and ready. You can customize the prompt further in Settings → AI Agent.',
  },
];

export default function OnboardingWizard({ onComplete }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    businessName: '',
    phone: '',
    industry: '',
    openTime: '08:00',
    closeTime: '18:00',
    timezone: 'America/Chicago',
    agentStyle: 'friendly',
  });

  const step = steps[currentStep];
  const isFirst = currentStep === 0;
  const isLast = currentStep === steps.length - 1;
  const isComplete = currentStep === steps.length;

  const handleNext = () => {
    if (isLast) {
      setCurrentStep(steps.length);
      onComplete?.(formData);
    } else {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (!isFirst) setCurrentStep(prev => prev - 1);
  };

  const handleFieldChange = (key, value) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  if (isComplete) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'var(--bg-primary)' }}>
        <div className="text-center max-w-md animate-scale-in">
          <div className="w-20 h-20 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-2xl shadow-emerald-500/30">
            <Check size={40} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>You're All Set! 🎉</h1>
          <p className="text-lg mb-6" style={{ color: 'var(--text-secondary)' }}>Your AI receptionist is configured and ready</p>
          <button onClick={onComplete} className="btn-primary text-base px-8 py-3">
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'var(--bg-primary)' }}>
      <div className="w-full max-w-lg">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            {steps.map((s, i) => (
              <div
                key={s.id}
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                  i < currentStep ? 'bg-emerald-500 text-white' :
                  i === currentStep ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/30' :
                  'text-sm'
                }`}
                style={i > currentStep ? { background: 'var(--bg-tertiary)', color: 'var(--text-muted)' } : {}}
              >
                {i < currentStep ? <Check size={14} /> : i + 1}
              </div>
            ))}
          </div>
          <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--bg-tertiary)' }}>
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${(currentStep / (steps.length - 1)) * 100}%`, background: 'linear-gradient(90deg, #6366f1, #3b82f6)' }}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="card-static p-8 animate-fade-in" key={step.id}>
          <div className="text-center mb-6">
            <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4" style={{ background: 'rgba(99, 102, 241, 0.1)' }}>
              <step.icon size={28} className="text-violet-600" />
            </div>
            <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>{step.title}</h2>
            <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>{step.subtitle}</p>
          </div>

          {step.description && (
            <p className="text-center text-sm mb-6" style={{ color: 'var(--text-secondary)' }}>{step.description}</p>
          )}

          {/* Fields */}
          {step.fields && (
            <div className="space-y-4">
              {step.fields.map(field => (
                <div key={field.key}>
                  <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
                    {field.label} {field.required && <span className="text-red-500">*</span>}
                  </label>
                  {field.type === 'select' ? (
                    <select
                      value={formData[field.key] || field.defaultValue}
                      onChange={(e) => handleFieldChange(field.key, e.target.value)}
                      className="input-modern"
                    >
                      {field.options.map(opt => (
                        <option key={opt} value={opt}>{opt}</option>
                      ))}
                    </select>
                  ) : field.type === 'time' ? (
                    <input
                      type="time"
                      value={formData[field.key] || field.defaultValue}
                      onChange={(e) => handleFieldChange(field.key, e.target.value)}
                      className="input-modern"
                    />
                  ) : (
                    <input
                      type="text"
                      value={formData[field.key] || ''}
                      onChange={(e) => handleFieldChange(field.key, e.target.value)}
                      placeholder={field.placeholder}
                      className="input-modern"
                    />
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Agent Style Options */}
          {step.options && (
            <div className="space-y-3">
              {step.options.map(opt => (
                <button
                  key={opt.id}
                  onClick={() => handleFieldChange('agentStyle', opt.id)}
                  className={`w-full p-4 rounded-xl border text-left transition-all ${
                    formData.agentStyle === opt.id ? 'border-violet-500 bg-violet-50 dark:bg-violet-900/10' : ''
                  }`}
                  style={formData.agentStyle !== opt.id ? { borderColor: 'var(--border-color)', background: 'var(--bg-tertiary)' } : {}}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{opt.icon}</span>
                    <div>
                      <p className="text-sm font-semibold" style={{ color: formData.agentStyle === opt.id ? '#7c3aed' : 'var(--text-primary)' }}>
                        {opt.label}
                      </p>
                      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{opt.desc}</p>
                    </div>
                    {formData.agentStyle === opt.id && (
                      <div className="ml-auto w-5 h-5 bg-violet-600 rounded-full flex items-center justify-center">
                        <Check size={12} className="text-white" />
                      </div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between mt-6">
          <button
            onClick={handlePrev}
            disabled={isFirst}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-xl transition-all ${
              isFirst ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            style={{ color: 'var(--text-secondary)' }}
          >
            <ChevronLeft size={16} /> Back
          </button>
          <button onClick={handleNext} className="btn-primary flex items-center gap-2 text-sm">
            {isLast ? 'Complete Setup' : 'Continue'}
            {!isLast && <ChevronRight size={16} />}
          </button>
        </div>
      </div>
    </div>
  );
}

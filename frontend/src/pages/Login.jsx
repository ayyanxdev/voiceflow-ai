import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Bot, Loader2, Phone, Mic, Calendar, ArrowRight, Shield, Zap, Headphones } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('admin@voiceflow.ai');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Image & Branding */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        {/* Background Image */}
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: 'url(/login-image.jpg)' }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-rose-950/90 via-fuchsia-950/70 to-pink-900/85" />
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-between p-12 w-full">
          {/* Logo */}
          <div className="flex items-center gap-3 animate-fade-in">
            <div className="w-11 h-11 bg-rose-500 rounded-xl flex items-center justify-center">
              <Bot size={24} className="text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">VoiceFlow AI</h1>
              <p className="text-xs text-slate-400">Voice Automation Platform</p>
            </div>
          </div>

          {/* Center Content */}
          <div className="flex-1 flex flex-col justify-center max-w-lg animate-slide-in-left">
            <div className="mb-6">
              <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-lg bg-white/10 border border-white/10 text-xs font-medium text-pink-100 mb-6">
                <Zap size={12} className="text-amber-400" />
                AI-Powered Voice Agent Platform
              </span>
            </div>
            <h2 className="text-4xl font-bold text-white leading-tight mb-4 tracking-tight">
              Your AI receptionist that never misses a call
            </h2>
            <p className="text-lg text-slate-300 leading-relaxed mb-8">
              Automate inbound & outbound calls, qualify leads, and book appointments — all with a natural-sounding AI voice agent.
            </p>

            {/* Feature Pills */}
            <div className="flex flex-wrap gap-3 mb-10">
              {[
                { icon: Phone, label: 'AI Voice Calls', color: 'text-pink-200 bg-pink-500/10 border-pink-300/20' },
                { icon: Headphones, label: '24/7 Receptionist', color: 'text-sky-200 bg-sky-500/10 border-sky-300/20' },
                { icon: Calendar, label: 'Auto Booking', color: 'text-rose-200 bg-rose-500/10 border-rose-300/20' },
                { icon: Shield, label: 'Lead Qualification', color: 'text-amber-200 bg-amber-500/10 border-amber-300/20' },
              ].map(({ icon: Icon, label, color }) => (
                <div key={label} className={`flex items-center gap-2 px-4 py-2 rounded-xl border backdrop-blur-sm ${color}`}>
                  <Icon size={14} />
                  <span className="text-sm font-medium">{label}</span>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-12 relative" style={{ background: 'var(--bg-primary)' }}>
        {/* Subtle background pattern */}
        <div className="absolute inset-0 opacity-30" style={{
          backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(201,73,120,0.12) 1px, transparent 0)',
          backgroundSize: '32px 32px'
        }} />

        <div className="w-full max-w-md relative z-10">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8 animate-fade-in">
            <div className="w-14 h-14 bg-rose-600 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Bot size={28} className="text-white" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">VoiceFlow AI</h1>
          </div>

          {/* Welcome Text */}
          <div className="mb-8 animate-fade-in">
            <h2 className="text-3xl font-bold text-slate-900 tracking-tight mb-2">Welcome back</h2>
            <p className="text-slate-500">Sign in to your VoiceFlow AI dashboard</p>
          </div>

          {/* Login Card */}
          <form onSubmit={handleSubmit} className="space-y-5 animate-slide-in-up">
            {error && (
              <div className="p-4 rounded-2xl text-sm font-medium bg-red-50 border border-red-100 text-red-600 flex items-center gap-2 animate-slide-in-up">
                <div className="w-5 h-5 rounded-full bg-red-100 flex items-center justify-center shrink-0">
                  <span className="text-xs font-bold">!</span>
                </div>
                {error}
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-slate-700">Email address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3.5 rounded-2xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500/40 focus:border-violet-400 transition-all bg-white border border-slate-200 text-sm"
                placeholder="you@company.com"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-slate-700">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3.5 rounded-2xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500/40 focus:border-violet-400 transition-all bg-white border border-slate-200 text-sm"
                placeholder="Enter your password"
                required
              />
            </div>

            <div className="flex items-center">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-violet-600 focus:ring-violet-500" defaultChecked />
                <span className="text-sm text-slate-600">Remember me</span>
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-3.5 disabled:opacity-50 flex items-center justify-center gap-2 text-sm"
            >
              {loading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  Sign In
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-slate-50 text-slate-400">Demo credentials</span>
            </div>
          </div>

          {/* Demo Credentials */}
          <div className="p-4 rounded-2xl bg-white border border-slate-100 shadow-sm animate-fade-in stagger-2" style={{ opacity: 0, animationFillMode: 'forwards' }}>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-rose-50 flex items-center justify-center border border-rose-100">
                <Mic size={16} className="text-rose-700" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">Demo Account</p>
                <p className="text-xs text-slate-500">admin@voiceflow.ai / admin123</p>
              </div>
            </div>
          </div>

          {/* Bottom Features */}
          <div className="mt-8 grid grid-cols-3 gap-4 animate-fade-in stagger-3" style={{ opacity: 0, animationFillMode: 'forwards' }}>
            {[
              { icon: Phone, label: 'AI Voice Agent' },
              { icon: Mic, label: 'Smart Handling' },
              { icon: Calendar, label: 'Auto Booking' },
            ].map(({ icon: Icon, label }) => (
              <div key={label} className="text-center">
                <div className="w-10 h-10 mx-auto mb-2 rounded-xl flex items-center justify-center bg-white border border-slate-100 shadow-sm">
                  <Icon size={16} className="text-slate-500" />
                </div>
                <p className="text-xs text-slate-500 font-medium">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

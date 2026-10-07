import { lazy, Suspense, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './components/Toast';
import Layout from './components/Layout';
import { Loader2 } from 'lucide-react';
import OnboardingWizard from './components/OnboardingWizard';

const Login = lazy(() => import('./pages/Login'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Calls = lazy(() => import('./pages/Calls'));
const CallDetail = lazy(() => import('./pages/CallDetail'));
const Leads = lazy(() => import('./pages/Leads'));
const LeadDetail = lazy(() => import('./pages/LeadDetail'));
const Appointments = lazy(() => import('./pages/Appointments'));
const Campaigns = lazy(() => import('./pages/Campaigns'));
const Analytics = lazy(() => import('./pages/Analytics'));
const ActivityPage = lazy(() => import('./pages/ActivityPage'));
const Settings = lazy(() => import('./pages/Settings'));

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 size={32} className="animate-spin text-rose-600" />
      </div>
    );
  }
  return user ? <Layout>{children}</Layout> : <Navigate to="/login" />;
}

function AppRoutes() {
  const { user, loading } = useAuth();
  const [showOnboarding, setShowOnboarding] = useState(() => !localStorage.getItem('onboardingComplete'));

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--bg-primary)' }}>
        <Loader2 size={32} className="animate-spin text-rose-600" />
      </div>
    );
  }

  if (user && showOnboarding) {
    return <OnboardingWizard onComplete={() => { localStorage.setItem('onboardingComplete', 'true'); setShowOnboarding(false); }} />;
  }

  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--bg-primary)' }}><Loader2 size={28} className="animate-spin text-rose-600" /></div>}>
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/calls" element={<ProtectedRoute><Calls /></ProtectedRoute>} />
        <Route path="/calls/:id" element={<ProtectedRoute><CallDetail /></ProtectedRoute>} />
        <Route path="/leads" element={<ProtectedRoute><Leads /></ProtectedRoute>} />
        <Route path="/leads/:id" element={<ProtectedRoute><LeadDetail /></ProtectedRoute>} />
        <Route path="/appointments" element={<ProtectedRoute><Appointments /></ProtectedRoute>} />
        <Route path="/campaigns" element={<ProtectedRoute><Campaigns /></ProtectedRoute>} />
        <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
        <Route path="/activity" element={<ProtectedRoute><ActivityPage /></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Suspense>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </ToastProvider>
  );
}

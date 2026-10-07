import { useState, useEffect } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard, Phone, Users, Calendar, Megaphone,
  BarChart3, Activity, Settings, LogOut, Bot, Menu,
  ChevronLeft, ChevronRight, Sun, Moon
} from 'lucide-react';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/calls', label: 'Calls', icon: Phone },
  { to: '/leads', label: 'Leads', icon: Users },
  { to: '/appointments', label: 'Appointments', icon: Calendar },
  { to: '/campaigns', label: 'Campaigns', icon: Megaphone },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/activity', label: 'Activity', icon: Activity },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [dark, setDark] = useState(() => localStorage.getItem('theme') === 'dark');
  const currentPage = navItems.find(({ to }) => pathname === to || pathname.startsWith(`${to}/`));

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [dark]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen" style={{ background: 'var(--bg-primary)' }}>
      {/* Mobile Overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed md:static z-50 h-full flex flex-col transition-all duration-300 ease-in-out sidebar-gradient
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
          ${collapsed ? 'w-[72px]' : 'w-64'}
        `}
        style={{ background: 'var(--sidebar-bg)' }}
      >
        {/* Logo */}
        <div className="px-4 py-5 flex items-center justify-between">
          {!collapsed && (
            <div className="flex items-center gap-3 animate-fade-in">
              <div className="sidebar-brand-mark w-9 h-9 bg-rose-500 rounded-xl flex items-center justify-center">
                <Bot size={20} className="text-white" />
              </div>
              <div>
                <h1 className="font-bold text-[15px] text-slate-800 dark:text-white tracking-tight">VoiceFlow AI</h1>
                <p className="text-[10px] text-slate-500 tracking-wide uppercase">Voice Automation</p>
              </div>
            </div>
          )}
          {collapsed && (
            <div className="sidebar-brand-mark w-9 h-9 bg-rose-500 rounded-xl flex items-center justify-center mx-auto">
              <Bot size={20} className="text-white" />
            </div>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hidden md:flex p-1.5 rounded-lg text-slate-500 hover:text-rose-800 hover:bg-white/80 dark:hover:text-white dark:hover:bg-white/10 transition-colors"
            aria-label={collapsed ? 'Expand navigation' : 'Collapse navigation'}
          >
            {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-3 px-2 space-y-0.5 overflow-y-auto">
          {navItems.map(({ to, label, icon: Icon }, i) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                `sidebar-nav-link flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold ${
                  isActive
                    ? 'sidebar-nav-link-active bg-rose-200 text-rose-800 dark:bg-rose-900/30 dark:text-rose-200'
                    : 'text-slate-600 hover:bg-white/80 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-white/5 dark:hover:text-white'
                } ${collapsed ? 'justify-center' : ''} animate-slide-in-left stagger-${i + 1}`
              }
              style={{ opacity: 0, animationFillMode: 'forwards' }}
              title={collapsed ? label : ''}
            >
              <Icon size={18} className="sidebar-nav-icon shrink-0" strokeWidth={1.8} />
              {!collapsed && <span>{label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* User Section */}
        <div className="px-2 py-4 border-t border-rose-200 dark:border-white/[0.06]">
          {!collapsed ? (
            <div className="flex items-center justify-between px-3 animate-fade-in">
              <div className="min-w-0">
                <p className="text-[13px] font-semibold text-slate-800 dark:text-white truncate">{user?.name || 'User'}</p>
                <p className="text-[11px] text-slate-500 capitalize">{user?.role || 'admin'}</p>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-slate-500 hover:text-rose-700 hover:bg-white/80 dark:hover:text-white dark:hover:bg-white/10 rounded-xl transition-colors"
                title="Logout"
              >
                <LogOut size={15} />
              </button>
            </div>
          ) : (
            <button
              onClick={handleLogout}
              className="w-full flex justify-center p-2 text-slate-500 hover:text-rose-700 hover:bg-white/80 dark:hover:text-white dark:hover:bg-white/10 rounded-xl transition-colors"
              title="Logout"
            >
              <LogOut size={15} />
            </button>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header
          className="h-16 border-b flex items-center justify-between px-4 md:px-6 shrink-0 backdrop-blur-md"
          style={{
            borderColor: 'var(--border-color)',
            background: 'var(--glass-bg)',
          }}
        >
          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileOpen(true)}
            className="md:hidden p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            aria-label="Open navigation"
          >
            <Menu size={20} style={{ color: 'var(--text-primary)' }} />
          </button>

          <div className="hidden md:block flex-1">
            <p className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>VoiceFlow / Workspace</p>
            <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{currentPage?.label || 'Workspace'}</p>
          </div>

          <div className="flex items-center gap-1.5">
            {/* Dark Mode Toggle */}
            <button
              onClick={() => setDark(!dark)}
              className="p-2.5 rounded-xl transition-colors"
              style={{ color: 'var(--text-secondary)' }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-tertiary)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              title={dark ? 'Light mode' : 'Dark mode'}
            >
              {dark ? <Sun size={17} /> : <Moon size={17} />}
            </button>

            {/* User Avatar (mobile) */}
            <div className="md:hidden w-8 h-8 bg-rose-600 rounded-lg flex items-center justify-center text-white text-xs font-bold">
              {user?.name?.[0] || 'U'}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 relative z-10">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

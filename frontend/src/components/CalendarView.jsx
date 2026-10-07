import { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';
import StatusBadge from './StatusBadge';

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

function getDaysInMonth(year, month) {
  return new Date(year, month + 1, 0).getDate();
}

function getFirstDayOfMonth(year, month) {
  return new Date(year, month, 1).getDay();
}

function isSameDay(d1, d2) {
  return d1.getFullYear() === d2.getFullYear() && d1.getMonth() === d2.getMonth() && d1.getDate() === d2.getDate();
}

function isToday(date) {
  return isSameDay(date, new Date());
}

function parseDate(iso) {
  if (!iso) return null;
  return new Date(iso);
}

export default function CalendarView({ appointments = [], onAppointmentClick }) {
  const [view, setView] = useState('month'); // month or week
  const [currentDate, setCurrentDate] = useState(new Date());

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const daysInMonth = getDaysInMonth(year, month);
  const firstDay = getFirstDayOfMonth(year, month);

  const prevMonth = () => {
    if (view === 'month') {
      setCurrentDate(new Date(year, month - 1, 1));
    } else {
      setCurrentDate(new Date(currentDate.getTime() - 7 * 24 * 60 * 60 * 1000));
    }
  };

  const nextMonth = () => {
    if (view === 'month') {
      setCurrentDate(new Date(year, month + 1, 1));
    } else {
      setCurrentDate(new Date(currentDate.getTime() + 7 * 24 * 60 * 60 * 1000));
    }
  };

  const today = () => setCurrentDate(new Date());

  const calendarDays = useMemo(() => {
    const days = [];
    // Previous month padding
    const prevMonthDays = getDaysInMonth(year, month - 1);
    for (let i = firstDay - 1; i >= 0; i--) {
      const d = new Date(year, month - 1, prevMonthDays - i);
      days.push({ date: d, isCurrentMonth: false });
    }
    // Current month
    for (let i = 1; i <= daysInMonth; i++) {
      days.push({ date: new Date(year, month, i), isCurrentMonth: true });
    }
    // Next month padding
    const remaining = 42 - days.length;
    for (let i = 1; i <= remaining; i++) {
      days.push({ date: new Date(year, month + 1, i), isCurrentMonth: false });
    }
    return days;
  }, [year, month, daysInMonth, firstDay]);

  const getEventsForDay = (date) => {
    return appointments.filter(a => {
      const apptDate = parseDate(a.start_time);
      return apptDate && isSameDay(apptDate, date);
    });
  };

  const statusColors = {
    scheduled: { bg: 'rgba(59, 130, 246, 0.1)', text: '#3b82f6', border: '#3b82f6' },
    confirmed: { bg: 'rgba(16, 185, 129, 0.1)', text: '#10b981', border: '#10b981' },
    completed: { bg: 'rgba(99, 102, 241, 0.1)', text: '#6366f1', border: '#6366f1' },
    cancelled: { bg: 'rgba(239, 68, 68, 0.1)', text: '#ef4444', border: '#ef4444' },
    no_show: { bg: 'rgba(245, 158, 11, 0.1)', text: '#f59e0b', border: '#f59e0b' },
  };

  return (
    <div className="space-y-4">
      {/* Calendar Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
            {view === 'month' ? `${MONTHS[month]} ${year}` : `Week of ${MONTHS[currentDate.getMonth()]} ${currentDate.getDate()}, ${year}`}
          </h2>
          <div className="flex rounded-lg border overflow-hidden" style={{ borderColor: 'var(--border-color)' }}>
            <button
              onClick={() => setView('month')}
              className={`px-3 py-1 text-xs font-medium transition-all ${view === 'month' ? 'bg-violet-600 text-white' : ''}`}
              style={view !== 'month' ? { color: 'var(--text-secondary)' } : {}}
            >
              Month
            </button>
            <button
              onClick={() => setView('week')}
              className={`px-3 py-1 text-xs font-medium transition-all ${view === 'week' ? 'bg-violet-600 text-white' : ''}`}
              style={view !== 'week' ? { color: 'var(--text-secondary)' } : {}}
            >
              Week
            </button>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={today} className="px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors" style={{ borderColor: 'var(--border-color)', color: 'var(--text-secondary)' }}>
            Today
          </button>
          <button onClick={prevMonth} className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" style={{ color: 'var(--text-secondary)' }}>
            <ChevronLeft size={18} />
          </button>
          <button onClick={nextMonth} className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" style={{ color: 'var(--text-secondary)' }}>
            <ChevronRight size={18} />
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      {view === 'month' ? (
        <div className="card-static overflow-hidden">
          {/* Day Headers */}
          <div className="calendar-grid border-b" style={{ borderColor: 'var(--border-color)' }}>
            {DAYS.map(day => (
              <div key={day} className="p-3 text-center text-xs font-semibold uppercase" style={{ color: 'var(--text-muted)' }}>
                {day}
              </div>
            ))}
          </div>

          {/* Calendar Days */}
          <div className="calendar-grid">
            {calendarDays.map((day, i) => {
              const events = getEventsForDay(day.date);
              const todayFlag = isToday(day.date);
              return (
                <div
                  key={i}
                  className={`calendar-day border-b border-r ${todayFlag ? 'today' : ''} ${!day.isCurrentMonth ? 'other-month' : ''}`}
                  style={{ borderColor: 'var(--border-color)' }}
                >
                  <span className={`text-xs font-medium mb-1 ${todayFlag ? 'text-violet-600 font-bold' : ''}`} style={!todayFlag ? { color: 'var(--text-secondary)' } : {}}>
                    {day.date.getDate()}
                  </span>
                  <div className="w-full space-y-0.5 overflow-hidden">
                    {events.slice(0, 3).map((event, j) => {
                      const colors = statusColors[event.status] || statusColors.scheduled;
                      return (
                        <div
                          key={event.id || j}
                          className="calendar-event cursor-pointer truncate"
                          style={{ background: colors.bg, color: colors.text, borderLeft: `2px solid ${colors.border}` }}
                          onClick={(e) => { e.stopPropagation(); onAppointmentClick?.(event); }}
                        >
                          {event.customer_name || event.title}
                        </div>
                      );
                    })}
                    {events.length > 3 && (
                      <div className="text-center text-xs font-medium" style={{ color: 'var(--text-muted)' }}>
                        +{events.length - 3} more
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        /* Week View */
        <div className="card-static overflow-hidden">
          <div className="grid grid-cols-7">
            {DAYS.map((day, i) => {
              const weekDate = new Date(currentDate);
              weekDate.setDate(currentDate.getDate() - currentDate.getDay() + i);
              const events = getEventsForDay(weekDate);
              const todayFlag = isToday(weekDate);
              return (
                <div key={day} className={`border-r last:border-r-0 ${todayFlag ? 'bg-violet-50 dark:bg-violet-900/10' : ''}`} style={{ borderColor: 'var(--border-color)', minHeight: 400 }}>
                  <div className={`p-3 border-b text-center ${todayFlag ? 'bg-violet-100 dark:bg-violet-900/20' : ''}`} style={{ borderColor: 'var(--border-color)' }}>
                    <p className="text-xs font-semibold uppercase" style={{ color: 'var(--text-muted)' }}>{day}</p>
                    <p className={`text-lg font-bold ${todayFlag ? 'text-violet-600' : ''}`} style={!todayFlag ? { color: 'var(--text-primary)' } : {}}>
                      {weekDate.getDate()}
                    </p>
                  </div>
                  <div className="p-2 space-y-1">
                    {events.map((event, j) => {
                      const colors = statusColors[event.status] || statusColors.scheduled;
                      const time = parseDate(event.start_time);
                      return (
                        <div
                          key={event.id || j}
                          className="p-2 rounded-lg text-xs cursor-pointer transition-all hover:scale-[1.02]"
                          style={{ background: colors.bg, borderLeft: `3px solid ${colors.border}` }}
                          onClick={() => onAppointmentClick?.(event)}
                        >
                          <p className="font-semibold truncate" style={{ color: colors.text }}>
                            {time ? time.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }) : ''}
                          </p>
                          <p className="truncate" style={{ color: 'var(--text-primary)' }}>{event.customer_name}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="flex flex-wrap gap-4 text-xs">
        {Object.entries(statusColors).map(([status, colors]) => (
          <div key={status} className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded" style={{ background: colors.border }} />
            <span className="capitalize" style={{ color: 'var(--text-secondary)' }}>{status.replace('_', ' ')}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

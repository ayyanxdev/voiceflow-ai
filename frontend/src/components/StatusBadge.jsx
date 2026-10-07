const colorMap = {
  // Lead statuses
  new: 'bg-blue-100 text-blue-700',
  contacted: 'bg-yellow-100 text-yellow-700',
  qualified: 'bg-green-100 text-green-700',
  unqualified: 'bg-red-100 text-red-700',
  appointment_booked: 'bg-emerald-100 text-emerald-700',
  follow_up: 'bg-amber-100 text-amber-700',
  converted: 'bg-green-100 text-green-700',
  lost: 'bg-gray-100 text-gray-600',
  // Temperature
  hot: 'bg-red-100 text-red-700',
  warm: 'bg-orange-100 text-orange-700',
  cold: 'bg-blue-100 text-blue-600',
  // Call statuses
  initiated: 'bg-gray-100 text-gray-600',
  ringing: 'bg-yellow-100 text-yellow-700',
  answered: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
  missed: 'bg-red-100 text-red-600',
  // Call outcomes
  qualified: 'bg-green-100 text-green-700',
  unqualified: 'bg-red-100 text-red-700',
  appointment_booked: 'bg-emerald-100 text-emerald-700',
  callback_requested: 'bg-amber-100 text-amber-700',
  transferred: 'bg-purple-100 text-purple-700',
  no_answer: 'bg-gray-100 text-gray-600',
  voicemail: 'bg-gray-100 text-gray-600',
  not_interested: 'bg-red-100 text-red-600',
  wrong_number: 'bg-gray-100 text-gray-600',
  information_request: 'bg-blue-100 text-blue-700',
  other: 'bg-gray-100 text-gray-600',
  // Appointment statuses
  scheduled: 'bg-blue-100 text-blue-700',
  confirmed: 'bg-green-100 text-green-700',
  cancelled: 'bg-red-100 text-red-600',
  rescheduled: 'bg-amber-100 text-amber-700',
  no_show: 'bg-red-100 text-red-700',
  // Campaign statuses
  draft: 'bg-gray-100 text-gray-600',
  active: 'bg-green-100 text-green-700',
  paused: 'bg-amber-100 text-amber-700',
};

export default function StatusBadge({ value, className = '' }) {
  const label = (value || '').replace(/_/g, ' ');
  const colors = colorMap[value] || 'bg-gray-100 text-gray-600';
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${colors} ${className}`}>
      {label}
    </span>
  );
}

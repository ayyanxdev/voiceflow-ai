const API_BASE = '/api';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  setToken(token) {
    this.token = token;
    if (token) localStorage.setItem('token', token);
    else localStorage.removeItem('token');
  }

  async request(path, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (this.token) headers['Authorization'] = `Bearer ${this.token}`;

    const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
    if (res.status === 401) {
      this.setToken(null);
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }
    if (res.status === 204) return null;
    const text = await res.text();
    const data = text ? JSON.parse(text) : null;
    if (!res.ok) throw new Error((data && data.detail) || 'Request failed');
    return data;
  }

  get(path) { return this.request(path); }
  post(path, body) { return this.request(path, { method: 'POST', body: JSON.stringify(body) }); }
  put(path, body) { return this.request(path, { method: 'PUT', body: JSON.stringify(body) }); }
  delete(path) { return this.request(path, { method: 'DELETE' }); }

  // Auth
  login(email, password) { return this.post('/auth/login', { email, password }); }
  getMe() { return this.get('/auth/me'); }

  // Dashboard
  getDashboard() { return this.get('/dashboard'); }

  // Leads
  getLeads(params = {}) { const q = new URLSearchParams(params).toString(); return this.get(`/leads${q ? '?' + q : ''}`); }
  getLead(id) { return this.get(`/leads/${id}`); }
  createLead(data) { return this.post('/leads', data); }
  updateLead(id, data) { return this.put(`/leads/${id}`, data); }
  deleteLead(id) { return this.delete(`/leads/${id}`); }

  // Calls
  getCalls(params = {}) { const q = new URLSearchParams(params).toString(); return this.get(`/calls${q ? '?' + q : ''}`); }
  getCall(id) { return this.get(`/calls/${id}`); }

  // Appointments
  getAppointments(params = {}) { const q = new URLSearchParams(params).toString(); return this.get(`/appointments${q ? '?' + q : ''}`); }
  createAppointment(data) { return this.post('/appointments', data); }
  updateAppointment(id, data) { return this.put(`/appointments/${id}`, data); }
  cancelAppointment(id) { return this.delete(`/appointments/${id}`); }

  // Campaigns
  getCampaigns(params = {}) { const q = new URLSearchParams(params).toString(); return this.get(`/campaigns${q ? '?' + q : ''}`); }
  getCampaign(id) { return this.get(`/campaigns/${id}`); }
  createCampaign(data) { return this.post('/campaigns', data); }
  updateCampaign(id, data) { return this.put(`/campaigns/${id}`, data); }

  // Activity
  getActivity(params = {}) { const q = new URLSearchParams(params).toString(); return this.get(`/activity${q ? '?' + q : ''}`); }

  // Settings
  getSettings() { return this.get('/settings'); }

  // Demo
  seedDemo() { return this.post('/demo/seed'); }

  // Export (authenticated blob download)
  async downloadCsv(path, filename, params = {}) {
    const q = new URLSearchParams(params).toString();
    const headers = {};
    if (this.token) headers['Authorization'] = `Bearer ${this.token}`;
    const res = await fetch(`${API_BASE}${path}${q ? '?' + q : ''}`, { headers });
    if (!res.ok) throw new Error('Export failed');
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  exportCalls(params = {}) { return this.downloadCsv('/export/calls', 'calls_export.csv', params); }
  exportLeads(params = {}) { return this.downloadCsv('/export/leads', 'leads_export.csv', params); }
  exportAppointments(params = {}) { return this.downloadCsv('/export/appointments', 'appointments_export.csv', params); }
}

export const api = new ApiService();
export default api;

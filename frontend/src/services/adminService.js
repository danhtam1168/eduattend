import api from './api';

export const adminService = {
  // ── TEACHERS ──
  getTeachers: async () => {
    const res = await api.get('/api/admin/teachers');
    return res.data;
  },
  createTeacher: async (data) => {
    const res = await api.post('/api/admin/teachers', data);
    return res.data;
  },
  updateTeacher: async (id, data) => {
    const res = await api.put(`/api/admin/teachers/${id}`, data);
    return res.data;
  },
  deactivateTeacher: async (id) => {
    const res = await api.delete(`/api/admin/teachers/${id}`);
    return res.data;
  },

  // ── STUDENTS ──
  getStudents: async (class_name) => {
    const params = class_name ? { class_name } : {};
    const res = await api.get('/api/admin/students', { params });
    return res.data;
  },
  createStudent: async (data) => {
    const res = await api.post('/api/admin/students', data);
    return res.data;
  },
  updateStudent: async (id, data) => {
    const res = await api.put(`/api/admin/students/${id}`, data);
    return res.data;
  },

  // ── SESSIONS ──
  getSessions: async (params = {}) => {
    const res = await api.get('/api/admin/sessions', { params });
    return res.data;
  },
  createSession: async (data) => {
    const res = await api.post('/api/admin/sessions', data);
    return res.data;
  },
  updateSession: async (id, data) => {
    const res = await api.put(`/api/admin/sessions/${id}`, data);
    return res.data;
  },
  cancelSession: async (id) => {
    const res = await api.delete(`/api/admin/sessions/${id}`);
    return res.data;
  },

  // ── SALARY RATES ──
  getSalaryRates: async () => {
    const res = await api.get('/api/admin/salary-rates');
    return res.data;
  },
  createSalaryRate: async (data) => {
    const res = await api.post('/api/admin/salary-rates', data);
    return res.data;
  },
  updateSalaryRate: async (id, data) => {
    const res = await api.put(`/api/admin/salary-rates/${id}`, data);
    return res.data;
  },

  // ── SALARY REPORT ──
  getSalaryReport: async (month) => {
    const res = await api.get('/api/admin/salary/report', { params: { month } });
    return res.data;
  },
};

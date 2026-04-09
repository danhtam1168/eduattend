import api from './api';

export const adminService = {
  // ── DASHBOARD ──
  getDashboard: async () => {
    const res = await api.get('/api/admin/dashboard');
    return res.data;
  },

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

  // ── SUBJECTS ──
  getSubjects: async () => {
    const res = await api.get('/api/admin/subjects');
    return res.data;
  },

  // ── CLASSES ──
  getClasses: async (params = {}) => {
    const res = await api.get('/api/admin/classes', { params });
    return res.data;
  },
  createClass: async (data) => {
    const res = await api.post('/api/admin/classes', data);
    return res.data;
  },
  updateClass: async (id, data) => {
    const res = await api.put(`/api/admin/classes/${id}`, data);
    return res.data;
  },
  getClassStudents: async (class_id) => {
    const res = await api.get(`/api/admin/classes/${class_id}/students`);
    return res.data;
  },
  enrollStudent: async (class_id, student_id) => {
    const res = await api.post(`/api/admin/classes/${class_id}/students`, { student_id });
    return res.data;
  },
  removeStudentFromClass: async (class_id, student_id) => {
    const res = await api.delete(`/api/admin/classes/${class_id}/students/${student_id}`);
    return res.data;
  },

  // ── SCHEDULES / TIMETABLE ──
  getSchedulesGrid: async (params = {}) => {
    // params can include from_date, to_date, class_id
    const res = await api.get('/api/admin/schedules', { params });
    return res.data;
  },
  createSchedule: async (data) => {
    const res = await api.post('/api/admin/schedules', data);
    return res.data;
  },
  updateSchedule: async (id, data) => {
    const res = await api.put(`/api/admin/schedules/${id}`, data);
    return res.data;
  },
  deleteSchedule: async (id) => {
    const res = await api.delete(`/api/admin/schedules/${id}`);
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

  // ── SCHEDULES ──
  getSessions: async (params = {}) => {
    const res = await api.get('/api/admin/schedules', { params });
    return res.data;
  },
  createSession: async (data) => {
    const res = await api.post('/api/admin/schedules', data);
    return res.data;
  },
  updateSession: async (id, data) => {
    const res = await api.put(`/api/admin/schedules/${id}`, data);
    return res.data;
  },
  cancelSession: async (id) => {
    const res = await api.delete(`/api/admin/schedules/${id}`);
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

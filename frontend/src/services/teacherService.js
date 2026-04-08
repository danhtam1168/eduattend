import api from './api';

export const teacherService = {
  // Buổi dạy của tôi
  getMySessions: async (params = {}) => {
    const res = await api.get('/api/teacher/sessions', { params });
    return res.data;
  },
  getTodaySessions: async () => {
    const res = await api.get('/api/teacher/sessions/today');
    return res.data;
  },
  getSessionDetail: async (id) => {
    const res = await api.get(`/api/teacher/sessions/${id}`);
    return res.data;
  },
  confirmSession: async (id) => {
    const res = await api.post(`/api/teacher/sessions/${id}/confirm`);
    return res.data;
  },

  // Điểm danh
  getSessionStudents: async (id) => {
    const res = await api.get(`/api/teacher/sessions/${id}/students`);
    return res.data;
  },
  markAttendance: async (id, attendances) => {
    const res = await api.post(`/api/teacher/sessions/${id}/attendance`, { attendances });
    return res.data;
  },

  // Profile
  updateProfile: async (data) => {
    const res = await api.put('/api/teacher/profile', data);
    return res.data;
  },
};

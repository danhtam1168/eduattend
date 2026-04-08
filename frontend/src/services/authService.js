import api from './api';

export const authService = {
  login: async (employee_id, password) => {
    const res = await api.post('/api/auth/login', { employee_id, password });
    return res.data;
  },

  me: async () => {
    const res = await api.get('/api/auth/me');
    return res.data;
  },

  changePassword: async (old_password, new_password) => {
    const res = await api.put('/api/auth/change-password', { old_password, new_password });
    return res.data;
  },
};

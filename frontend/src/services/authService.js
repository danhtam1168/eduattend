import api from './api';

export const authService = {
  login: async (username, password) => {
    const res = await api.post('/api/auth/login', { username, password });
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

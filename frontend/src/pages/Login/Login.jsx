import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, LogIn, AlertCircle, Users, GraduationCap, Calendar } from 'lucide-react';
import Input from '../../components/ui/Input';
import { authService } from '../../services/authService';
import useAuthStore from '../../store/authStore';
import styles from './Login.module.css';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [form, setForm] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.username || !form.password) {
      setError('Vui lòng nhập đầy đủ thông tin');
      return;
    }
    setLoading(true);
    try {
      const data = await authService.login(form.username, form.password);
      login(data.data.user, data.data.access_token);
      const role = data.data.user.role;
      navigate(role === 'admin' ? '/admin/dashboard' : '/teacher/sessions', { replace: true });
    } catch (err) {
      setError(err.response?.data?.message || 'Đăng nhập thất bại');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      {/* Left — Illustration */}
      <div className={styles.left}>
        <div className={styles.illustration}>
          <div className={styles.logoBox}>
            <div className={styles.logoIcon}>
              <BookOpen size={28} />
            </div>
            <span className={styles.brandName}>EduAttend</span>
          </div>
          <p className={styles.tagline}>
            Hệ thống quản lý điểm danh học sinh &amp; chấm công giáo viên cho trung tâm dạy thêm
          </p>
          <div className={styles.statsRow}>
            <div className={styles.statItem}>
              <span className={styles.statValue}><Users size={20} /></span>
              <span className={styles.statLabel}>Giáo viên</span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statValue}><GraduationCap size={20} /></span>
              <span className={styles.statLabel}>Học sinh</span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statValue}><Calendar size={20} /></span>
              <span className={styles.statLabel}>Buổi dạy</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right — Form */}
      <div className={styles.right}>
        <div className={styles.formBox}>
          <div className={styles.formHeader}>
            <p className={styles.welcome}>Chào mừng trở lại 👋</p>
            <h1 className={styles.formTitle}>Đăng nhập</h1>
            <p className={styles.formSubtitle}>Nhập thông tin tài khoản của bạn để tiếp tục</p>
          </div>

          <form className={styles.form} onSubmit={handleSubmit}>
            {error && (
              <div className={styles.errorBox}>
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            <Input
              label="Tên đăng nhập"
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder="Nhập username..."
              required
              disabled={loading}
            />

            <Input
              label="Mật khẩu"
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Nhập mật khẩu..."
              required
              disabled={loading}
            />

            <button type="submit" className={styles.submitBtn} disabled={loading}>
              {loading ? (
                <span style={{
                  width: 16, height: 16, border: '2px solid currentColor',
                  borderTopColor: 'transparent', borderRadius: '50%',
                  display: 'inline-block', animation: 'spin 0.6s linear infinite'
                }} />
              ) : <LogIn size={18} />}
              {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;

import { Calendar } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import useAuthStore from '../../store/authStore';
import styles from './Header.module.css';

const PAGE_TITLES = {
  '/admin/dashboard':     'Dashboard',
  '/admin/teachers':      'Quản lý giáo viên',
  '/admin/students':      'Quản lý học sinh',
  '/admin/sessions':      'Quản lý buổi dạy',
  '/admin/salary-report': 'Báo cáo lương',
  '/admin/settings':      'Mệnh giá lương',
  '/teacher/sessions':    'Buổi dạy của tôi',
  '/teacher/profile':     'Thông tin cá nhân',
};

const Header = () => {
  const { user } = useAuthStore();
  const { pathname } = useLocation();

  const title = Object.entries(PAGE_TITLES).find(([path]) =>
    pathname.startsWith(path)
  )?.[1] || 'EduAttend';

  const today = new Date().toLocaleDateString('vi-VN', {
    weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric',
  });

  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <h1 className={styles.pageTitle}>{title}</h1>
      </div>
      <div className={styles.right}>
        <div className={styles.date}>
          <Calendar size={14} />
          {today}
        </div>
        <div className={styles.userBadge}>
          <span className={styles.empId}>{user?.employee_id}</span>
        </div>
      </div>
    </header>
  );
};

export default Header;

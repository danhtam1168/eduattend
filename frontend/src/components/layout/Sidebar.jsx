import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Users, GraduationCap, CalendarDays,
  FileText, Settings, LogOut, BookOpen, ClipboardCheck,
  User, Building2
} from 'lucide-react';
import clsx from 'clsx';
import useAuthStore from '../../store/authStore';
import styles from './Sidebar.module.css';

const adminLinks = [
  { section: 'MAIN MENU' },
  { to: '/admin/dashboard',     label: 'Dashboard',       icon: LayoutDashboard },
  { to: '/admin/teachers',      label: 'Giáo viên',       icon: Users },
  { to: '/admin/students',      label: 'Học sinh',         icon: GraduationCap },
  { to: '/admin/classes',       label: 'Lớp học',          icon: Users },
  { to: '/admin/subjects',      label: 'Môn học',          icon: BookOpen },
  { to: '/admin/rooms',         label: 'Phòng học',        icon: Building2 },
  { to: '/admin/schedules',     label: 'Xếp lịch học',     icon: CalendarDays },
  { to: '/admin/sessions',      label: 'Buổi dạy',         icon: ClipboardCheck },
  { section: 'BÁO CÁO' },
  { to: '/admin/salary-report', label: 'Báo cáo lương',   icon: FileText },
  { section: 'CÀI ĐẶT' },
  { to: '/admin/settings',      label: 'Mệnh giá lương',  icon: Settings },
];

const teacherLinks = [
  { section: 'MAIN MENU' },
  { to: '/teacher/sessions',    label: 'Buổi dạy của tôi', icon: CalendarDays },
  { to: '/teacher/profile',     label: 'Thông tin cá nhân',icon: User },
];

const Sidebar = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const links = user?.role === 'admin' ? adminLinks : teacherLinks;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const initials = user?.full_name
    ? user.full_name.split(' ').map(w => w[0]).slice(-2).join('').toUpperCase()
    : 'U';

  return (
    <aside className={styles.sidebar}>
      {/* Logo */}
      <div className={styles.logo}>
        <div className={styles.logoIcon}>
          <BookOpen size={18} />
        </div>
        <div className={styles.logoText}>
          <span className={styles.logoName}>EduAttend</span>
          <span className={styles.logoSub}>Trung tâm dạy thêm</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className={styles.nav}>
        {links.map((item, i) => {
          if (item.section) {
            return (
              <div key={i} className={styles.navSection}>
                <span className={styles.navSectionLabel}>{item.section}</span>
              </div>
            );
          }
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                clsx(styles.navItem, isActive && styles.active)
              }
            >
              <Icon className={styles.navIcon} />
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      {/* User info + Logout */}
      <div className={styles.bottom}>
        <div className={styles.userCard}>
          <div className={styles.avatar}>{initials}</div>
          <div>
            <div className={styles.userName}>{user?.full_name || 'User'}</div>
            <div className={styles.userRole}>
              {user?.role === 'admin' ? 'Admin' : 'Giáo viên'}
            </div>
          </div>
        </div>
        <button className={styles.logoutBtn} onClick={handleLogout}>
          <LogOut size={16} />
          Đăng xuất
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;

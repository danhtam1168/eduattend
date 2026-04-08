import { useEffect, useState } from 'react';
import { Users, GraduationCap, CalendarDays, CheckCircle2 } from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../../components/ui/Card';
import Badge from '../../../components/ui/Badge';
import { adminService } from '../../../services/adminService';
import { formatDate, formatShift, getCurrentMonth } from '../../../utils/formatters';
import { SESSION_STATUS } from '../../../utils/constants';
import styles from './Dashboard.module.css';

const StatCard = ({ icon: Icon, value, label, color, bg }) => (
  <div className={styles.statCard}>
    <div className={styles.statIconBox} style={{ background: bg }}>
      <Icon size={22} color={color} />
    </div>
    <div className={styles.statInfo}>
      <div className={styles.statValue}>{value}</div>
      <div className={styles.statLabel}>{label}</div>
    </div>
  </div>
);

const Dashboard = () => {
  const [teachers, setTeachers]   = useState([]);
  const [students, setStudents]   = useState([]);
  const [sessions, setSessions]   = useState([]);
  const [loading, setLoading]     = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const month = getCurrentMonth();
        const [t, st, se] = await Promise.all([
          adminService.getTeachers(),
          adminService.getStudents(),
          adminService.getSessions({ month, per_page: 10 }),
        ]);
        setTeachers(t.data || []);
        setStudents(st.data || []);
        setSessions(se.data?.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const confirmedCount = sessions.filter(s => s.status === 'confirmed').length;

  return (
    <div className={styles.page}>
      {/* Stats */}
      <div className={styles.statsGrid}>
        <StatCard icon={Users}         value={loading ? '...' : teachers.length}  label="Giáo viên" color="#F2B43A" bg="#FFF8EC" />
        <StatCard icon={GraduationCap} value={loading ? '...' : students.length}  label="Học sinh"  color="#3B82F6" bg="#DBEAFE" />
        <StatCard icon={CalendarDays}  value={loading ? '...' : sessions.length}  label="Buổi dạy (tháng này)" color="#22C55E" bg="#DCFCE7" />
        <StatCard icon={CheckCircle2}  value={loading ? '...' : confirmedCount}   label="Đã xác nhận" color="#8B5CF6" bg="#EDE9FE" />
      </div>

      {/* Recent sessions + Teacher list */}
      <div className={styles.grid2}>
        <Card>
          <CardHeader title="Buổi dạy gần đây" />
          <CardBody>
            <div className={styles.sessionList}>
              {loading ? <p className={styles.empty}>Đang tải...</p>
                : sessions.length === 0 ? <p className={styles.empty}>Không có buổi dạy nào</p>
                : sessions.slice(0, 8).map(s => {
                  const d = new Date(s.date);
                  return (
                    <div key={s.id} className={styles.sessionItem}>
                      <div className={styles.sessionDate}>
                        <span className={styles.sessionDay}>{d.getDate()}</span>
                        <span className={styles.sessionMon}>T{d.getMonth()+1}</span>
                      </div>
                      <div className={styles.sessionInfo}>
                        <div className={styles.sessionName}>{s.teacher_name || '---'}</div>
                        <div className={styles.sessionMeta}>
                          {formatShift(s.shift)} · {s.class_type || '---'}
                        </div>
                      </div>
                      <Badge color={SESSION_STATUS[s.status]?.color || 'pending'}>
                        {SESSION_STATUS[s.status]?.label || s.status}
                      </Badge>
                    </div>
                  );
                })}
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Danh sách giáo viên" />
          <CardBody>
            <div className={styles.teacherList}>
              {loading ? <p className={styles.empty}>Đang tải...</p>
                : teachers.length === 0 ? <p className={styles.empty}>Chưa có giáo viên nào</p>
                : teachers.map(t => {
                  const initials = t.full_name?.split(' ').map(w => w[0]).slice(-2).join('').toUpperCase();
                  return (
                    <div key={t.id} className={styles.teacherItem}>
                      <div className={styles.avatar}>{initials}</div>
                      <div>
                        <div className={styles.teacherName}>{t.full_name}</div>
                        <div className={styles.teacherId}>{t.employee_id}</div>
                      </div>
                      <Badge color={t.is_active ? 'present' : 'absent'}>
                        {t.is_active ? 'Hoạt động' : 'Khoá'}
                      </Badge>
                    </div>
                  );
                })}
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;

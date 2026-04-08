import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, ClipboardCheck, Clock, BookOpen } from 'lucide-react';
import Badge from '../../../components/ui/Badge';
import Button from '../../../components/ui/Button';
import { teacherService } from '../../../services/teacherService';
import { formatDate, formatShift, getCurrentMonth } from '../../../utils/formatters';
import { SESSION_STATUS } from '../../../utils/constants';
import styles from './MySessions.module.css';

const MySessions = () => {
  const navigate = useNavigate();
  const [today,    setToday]    = useState([]);
  const [sessions, setSessions] = useState([]);
  const [month,    setMonth]    = useState(getCurrentMonth());
  const [loading,  setLoading]  = useState(true);
  const [confirming, setConfirming] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const [tod, all] = await Promise.all([
        teacherService.getTodaySessions(),
        teacherService.getMySessions({ month, per_page: 100 }),
      ]);
      setToday(tod.data || []);
      setSessions(all.data?.items || []);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [month]);

  const handleConfirm = async (session) => {
    if (!window.confirm('Xác nhận bạn đã dạy buổi này?')) return;
    setConfirming(session.id);
    try {
      await teacherService.confirmSession(session.id);
      load();
    } catch (err) {
      alert(err.response?.data?.message || 'Lỗi xác nhận');
    } finally { setConfirming(null); }
  };

  const handleAttendance = (session) => {
    navigate(`/teacher/sessions/${session.id}/attend`);
  };

  return (
    <div className={styles.page}>
      {/* Today's sessions */}
      {today.length > 0 && (
        <div className={styles.todayBox}>
          <div className={styles.todayTitle}>📅 HÔM NAY</div>
          <div className={styles.todayHeading}>Buổi dạy hôm nay của bạn</div>
          <div className={styles.todayGrid}>
            {today.map(s => (
              <div key={s.id} className={styles.todaySession}>
                <div className={styles.todayShift}>{formatShift(s.shift)}</div>
                <div className={styles.todayClass}>{s.class_type || 'N/A'}</div>
                {s.status === 'pending' && (
                  <button
                    className={styles.confirmBtn}
                    onClick={() => handleConfirm(s)}
                    disabled={confirming === s.id}
                  >
                    <CheckCircle size={13} />
                    {confirming === s.id ? 'Đang xác nhận...' : 'Xác nhận có dạy'}
                  </button>
                )}
                {s.status === 'confirmed' && (
                  <>
                    <div className={styles.confirmedTag}><CheckCircle size={13} /> Đã xác nhận</div>
                    <button className={styles.confirmBtn} onClick={() => handleAttendance(s)} style={{ marginTop: '0.5rem' }}>
                      <ClipboardCheck size={13} />
                      Điểm danh học sinh
                    </button>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Month filter */}
      <div className={styles.toolbar}>
        <label style={{ fontSize: 'var(--font-size-sm)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Tháng:</label>
        <input type="month" value={month} onChange={e => setMonth(e.target.value)}
          style={{ padding: '0.45rem 0.875rem', border: '1.5px solid var(--color-border)', borderRadius: 'var(--radius-md)', fontSize: 'var(--font-size-sm)', fontFamily: 'var(--font-family)' }} />
      </div>

      {/* All sessions grid */}
      <div className={styles.sessionsGrid}>
        {loading ? (
          <div className={styles.empty}>Đang tải...</div>
        ) : sessions.length === 0 ? (
          <div className={styles.empty}>Không có buổi dạy nào trong tháng này</div>
        ) : (
          sessions.map(s => (
            <div key={s.id} className={styles.sessionCard}>
              <div className={styles.sessionCardTop}>
                <div>
                  <div className={styles.sessionDate}>{formatDate(s.date)}</div>
                  <div className={styles.sessionShift}>{formatShift(s.shift)}</div>
                </div>
                <Badge color={SESSION_STATUS[s.status]?.color || 'pending'}>
                  {SESSION_STATUS[s.status]?.label || s.status}
                </Badge>
              </div>

              <div className={styles.sessionMeta}>
                <BookOpen size={14} />
                {s.class_type || 'N/A'} — {s.salary_amount?.toLocaleString('vi-VN')} đ
              </div>

              <div className={styles.sessionActions}>
                {s.status === 'pending' && (
                  <Button size="sm" icon={<CheckCircle size={14} />}
                    loading={confirming === s.id}
                    onClick={() => handleConfirm(s)}>
                    Xác nhận
                  </Button>
                )}
                {s.status === 'confirmed' && (
                  <Button size="sm" variant="secondary" icon={<ClipboardCheck size={14} />}
                    onClick={() => handleAttendance(s)}>
                    Điểm danh
                  </Button>
                )}
                {s.status === 'cancelled' && (
                  <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>Buổi dạy đã bị huỷ</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MySessions;

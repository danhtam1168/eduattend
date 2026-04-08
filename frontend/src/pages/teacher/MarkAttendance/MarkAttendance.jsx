import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Check } from 'lucide-react';
import { teacherService } from '../../../services/teacherService';
import { formatDate, formatShift } from '../../../utils/formatters';
import Button from '../../../components/ui/Button';
import Badge from '../../../components/ui/Badge';
import styles from './MarkAttendance.module.css';

const MarkAttendance = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Lưu trạng thái attendance dưới dạng object { student_id: { is_present, note } }
  const [attendances, setAttendances] = useState({});

  useEffect(() => {
    const load = async () => {
      try {
        const [sessRes, stuRes] = await Promise.all([
          teacherService.getSessionDetail(id),
          teacherService.getSessionStudents(id)
        ]);
        setSession(sessRes.data);
        
        const stus = stuRes.data || [];
        setStudents(stus);

        // Khởi tạo state attendances từ dữ liệu API
        const attMap = {};
        stus.forEach(s => {
          attMap[s.id] = {
            is_present: s.is_present ?? true, // Mặc định là Có mặt nếu chưa điểm danh
            note: s.att_note || ''
          };
        });
        setAttendances(attMap);

      } catch (err) {
        console.error(err);
        alert('Không tải được dữ liệu buổi dạy');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  const togglePresence = (studentId) => {
    setAttendances(prev => ({
      ...prev,
      [studentId]: {
        ...prev[studentId],
        is_present: !prev[studentId].is_present
      }
    }));
  };

  const handleNoteChange = (studentId, note) => {
    setAttendances(prev => ({
      ...prev,
      [studentId]: {
        ...prev[studentId],
        note
      }
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    // Chuẩn bị payload dạng mảng
    const payload = students.map(s => ({
      student_id: s.id,
      is_present: attendances[s.id].is_present,
      note: attendances[s.id].note
    }));

    try {
      await teacherService.markAttendance(id, payload);
      alert('Lưu điểm danh thành công!');
      navigate('/teacher/sessions');
    } catch (err) {
      alert(err.response?.data?.message || 'Lỗi khi lưu điểm danh');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className={styles.empty}>Đang tải...</div>;
  if (!session) return <div className={styles.empty}>Buổi dạy không tồn tại</div>;

  const total = students.length;
  const presentCount = Object.values(attendances).filter(a => a.is_present).length;
  const absentCount = total - presentCount;

  return (
    <div className={styles.page}>
      <button className={styles.backBtn} onClick={() => navigate(-1)}>
        <ArrowLeft size={16} /> Quay lại
      </button>

      <div className={styles.sessionInfo}>
        <div className={styles.infoLeft}>
          <div className={styles.infoDate}>Buổi dạy ngày {formatDate(session.date)}</div>
          <div className={styles.infoMeta}>
            {formatShift(session.shift)} • {session.class_type} • Thù lao: {session.salary_amount?.toLocaleString()} đ
          </div>
        </div>
        <div className={styles.statsRow}>
          <div className={`${styles.statChip} ${styles.present}`}>
            <span style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, color: 'var(--color-present-text)' }}>{presentCount}</span>
            <span style={{ fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--color-present)' }}>Có mặt</span>
          </div>
          <div className={`${styles.statChip} ${styles.absent}`}>
            <span style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, color: 'var(--color-absent-text)' }}>{absentCount}</span>
            <span style={{ fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--color-absent)' }}>Vắng</span>
          </div>
        </div>
      </div>

      <div className={styles.studentList}>
        {students.length === 0 ? (
          <div className={styles.empty}>Không có học sinh nào trong lớp này</div>
        ) : (
          students.map(s => {
            const isPresent = attendances[s.id]?.is_present;
            return (
              <div 
                key={s.id} 
                className={`${styles.studentRow} ${isPresent ? styles.present : styles.absent}`}
                onClick={() => togglePresence(s.id)}
              >
                <div className={styles.checkIcon}>
                  <Check size={16} />
                </div>
                <div className={styles.studentName}>{s.name}</div>
                
                {/* Prevent click propagation on input so it doesn't toggle attendance */}
                <input
                  type="text"
                  className={styles.noteInput}
                  placeholder="Ghi chú (tuỳ chọn)..."
                  value={attendances[s.id]?.note || ''}
                  onChange={(e) => handleNoteChange(s.id, e.target.value)}
                  onClick={(e) => e.stopPropagation()} 
                />
              </div>
            );
          })
        )}
      </div>

      <div className={styles.bottomBar}>
        <div className={styles.summary}>
          Sĩ số: <span className={styles.summaryBold}>{total}</span> • 
          Có mặt: <span className={styles.summaryBold} style={{color: 'var(--color-present)'}}> {presentCount}</span> •
          Vắng: <span className={styles.summaryBold} style={{color: 'var(--color-absent)'}}> {absentCount}</span>
        </div>
        <Button size="lg" loading={saving} onClick={handleSave}>
          Lưu điểm danh
        </Button>
      </div>
    </div>
  );
};

export default MarkAttendance;

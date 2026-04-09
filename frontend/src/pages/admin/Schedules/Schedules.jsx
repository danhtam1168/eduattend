import { useState, useEffect, useMemo } from 'react';
import { Calendar as CalendarIcon, CheckSquare, Square, Trash2, Clock, Users, MapPin } from 'lucide-react';
import { Card, CardBody } from '../../../components/ui/Card';
import Button from '../../../components/ui/Button';
import { adminService } from '../../../services/adminService';
import styles from './Schedules.module.css';

const START_HOUR = 7;
const END_HOUR = 22;

const DAYS = [
  { id: 0, name: 'Thứ 2' },
  { id: 1, name: 'Thứ 3' },
  { id: 2, name: 'Thứ 4' },
  { id: 3, name: 'Thứ 5' },
  { id: 4, name: 'Thứ 6' },
  { id: 5, name: 'Thứ 7' },
  { id: 6, name: 'Chủ Nhật' },
];

const Schedules = () => {
  const [classesList, setClassesList] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Trạng thái hiển thị và thao tác
  const [visibleClasses, setVisibleClasses] = useState(new Set()); // Set of class_id
  const [activeClassId, setActiveClassId] = useState(null); // Lớp đang được chọn để xếp lịch nhanh

  const [saving, setSaving] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [classRes, tplRes] = await Promise.all([
        adminService.getClasses(),
        adminService.getClassSchedules() // Lấy toàn bộ template
      ]);
      const cls = classRes.data?.items || classRes.data || [];
      setClassesList(cls);
      setTemplates(tplRes.data || []);
      
      // Mặc định hiển thị tất cả
      setVisibleClasses(new Set(cls.map(c => c.id)));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  // Labels thời gian (07:00, 07:30)
  const timeLabels = useMemo(() => {
    const labels = [];
    for (let h = START_HOUR; h < END_HOUR; h++) {
      labels.push(`${h.toString().padStart(2, '0')}:00`);
      labels.push(`${h.toString().padStart(2, '0')}:30`);
    }
    return labels;
  }, []);

  const toggleVisibility = (classId) => {
    const next = new Set(visibleClasses);
    if (next.has(classId)) next.delete(classId);
    else next.add(classId);
    setVisibleClasses(next);
  };

  const toggleAll = () => {
    if (visibleClasses.size === classesList.length) {
      setVisibleClasses(new Set());
    } else {
      setVisibleClasses(new Set(classesList.map(c => c.id)));
    }
  };

  const handleCellClick = async (dayOfWeek, timeStr) => {
    if (!activeClassId) {
      alert("Vui lòng BẤM CHỌN một lớp học ở danh sách bên trái để bắt đầu xếp lịch nhanh.");
      return;
    }
    
    // Tính toán end_time mặc định là +1.5h
    const [h, m] = timeStr.split(':').map(Number);
    const endH = h + Math.floor((m + 90) / 60);
    const endM = (m + 90) % 60;
    const endStr = `${endH.toString().padStart(2, '0')}:${endM.toString().padStart(2, '0')}`;

    setSaving(true);
    try {
      await adminService.createClassSchedule({
        class_id: activeClassId,
        day_of_week: dayOfWeek,
        start_time: timeStr,
        end_time: endStr
        // Chưa hỗ trợ chọn phòng nhanh, sẽ thêm sau nếu gán phòng fix
      });
      // Load lại templates
      const res = await adminService.getClassSchedules();
      setTemplates(res.data || []);
    } catch (err) {
      alert(err.response?.data?.message || 'Lỗi khi xếp lịch');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm("Bạn có chắc xoá khung giờ này không? Các buổi dạy thực tế trong tương lai vẫn có thể bị ảnh hưởng.")) return;
    setSaving(true);
    try {
      await adminService.deleteClassSchedule(id);
      setTemplates(templates.filter(t => t.id !== id));
    } catch (err) {
      alert(err.response?.data?.message || 'Lỗi khi xoá');
    } finally {
      setSaving(false);
    }
  };

  // Tính toán màu sắc nhẹ nhàng ngẫu nhiên cho từng lớp để dễ phân biệt
  const getClassColor = (classId) => {
    const colors = ['#DBEAFE', '#D1FAE5', '#FEF3C7', '#FEE2E2', '#E0E7FF', '#FCE7F3', '#FEF08A', '#A7F3D0'];
    const textColors = ['#1E3A8A', '#065F46', '#92400E', '#991B1B', '#3730A3', '#9D174D', '#854D0E', '#064E3B'];
    const idx = classId % colors.length;
    return { bg: colors[idx], text: textColors[idx], border: textColors[idx] };
  };

  const activeClass = classesList.find(c => c.id === activeClassId);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleWrap}>
          <h2 className={styles.title}>Cấu hình Mẫu Thời Khóa Biểu (Cố định tuần)</h2>
          <p className={styles.desc}>Tick vào ô để Xếp lịch lặp lại hàng tuần. Mỗi khi tạo mẫu, các buổi dạy thật sẽ được tự động sinh ra hợp lý.</p>
        </div>
      </div>

      <div className={styles.layout}>
        {/* Sidebar Chọn Lớp */}
        <div className={styles.sidebar}>
          <div className={styles.sidebarHeader}>
            <h3 className={styles.sidebarTitle}>Danh sách lớp</h3>
            <button className={styles.iconBtn} onClick={toggleAll} title="Chọn hiển thị tất cả">
              {visibleClasses.size === classesList.length ? <CheckSquare size={16} /> : <Square size={16} />}
            </button>
          </div>
          
          <div className={styles.classList}>
            {loading ? <p style={{padding:'1rem',fontSize:'0.875rem'}}>Đang tải...</p> : classesList.map(c => {
              const isActive = activeClassId === c.id;
              const isVisible = visibleClasses.has(c.id);
              const color = getClassColor(c.id);
              return (
                <div key={c.id} className={`${styles.classItem} ${isActive ? styles.classItemActive : ''}`}>
                  <button className={styles.visToggle} onClick={() => toggleVisibility(c.id)}>
                    {isVisible ? <CheckSquare size={14} color="#4B5563" /> : <Square size={14} color="#9CA3AF" />}
                  </button>
                  <button 
                    className={styles.classBtn} 
                    onClick={() => setActiveClassId(isActive ? null : c.id)}
                  >
                    <span className={styles.colorDot} style={{backgroundColor: color.border}}></span>
                    {c.class_name}
                  </button>
                </div>
              );
            })}
          </div>

          {activeClassId && (
            <div className={styles.activeAlert}>
              Đang xếp lịch cho <strong>{activeClass?.class_name}</strong>. Hãy click vào ô bất kỳ trên lưới để chốt lịch.
            </div>
          )}
        </div>

        {/* Lưới Grid */}
        <div className={styles.mainGrid}>
          <div className={styles.gridContainer}>
            {/* Header Lưới (Thứ 2 -> CN) */}
            <div className={styles.timeColumnHeader}>GMT+7</div>
            {DAYS.map(d => (
              <div key={d.id} className={styles.dayHeader}>
                {d.name}
              </div>
            ))}

            {/* Các hàng giờ */}
            {timeLabels.map((timeLabel, index) => (
              <div key={`time-${index}`} className={styles.timeLabel} style={{ gridRow: index + 2, gridColumn: 1 }}>
                <span className={styles.timeText}>{timeLabel}</span>
              </div>
            ))}

            {/* Khung ô để click (Background Grid cells) */}
            {DAYS.map((d, dayIndex) => {
              return timeLabels.map((tLabel, tIndex) => (
                <div 
                  key={`cell-${d.id}-${tIndex}`}
                  className={`${styles.gridCell} ${activeClassId ? styles.gridCellClickable : ''}`}
                  style={{ gridRow: tIndex + 2, gridColumn: dayIndex + 2 }}
                  onClick={() => handleCellClick(d.id, tLabel)}
                >
                </div>
              ));
            })}

            {/* Hiển thị các khối sự kiện (Schedule Templates) */}
            {templates
              .filter(t => visibleClasses.has(t.class_id))
              .map(tpl => {
              const dayIndex = DAYS.findIndex(d => d.id === tpl.day_of_week);
              if (dayIndex === -1) return null;

              const [sh, sm] = tpl.start_time.split(':').map(Number);
              const [eh, em] = tpl.end_time.split(':').map(Number);

              const startRow = (sh - START_HOUR) * 2 + (sm >= 30 ? 1 : 0) + 2;
              const durationMins = (eh * 60 + em) - (sh * 60 + sm);
              const rowSpan = Math.ceil(durationMins / 30);
              
              const color = getClassColor(tpl.class_id);

              return (
                <div 
                  key={tpl.id} 
                  className={styles.eventBlock}
                  style={{ 
                    gridColumn: dayIndex + 2, 
                    gridRow: `${startRow} / span ${rowSpan}`,
                    backgroundColor: color.bg,
                    borderLeftColor: color.border,
                    color: color.text
                  }}
                  title={`[${tpl.class_name}] ${tpl.start_time.substring(0,5)} - ${tpl.end_time.substring(0,5)}`}
                >
                  <div className={styles.eventTitle}>{tpl.class_name}</div>
                  <div className={styles.eventSub}><Clock size={10} /> {tpl.start_time.substring(0,5)} - {tpl.end_time.substring(0,5)}</div>
                  {tpl.teacher_name && <div className={styles.eventSub}><Users size={10} /> {tpl.teacher_name}</div>}
                  <button className={styles.deleteBtn} onClick={(e) => handleDelete(e, tpl.id)}>
                    <Trash2 size={12} color={color.text} />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Schedules;

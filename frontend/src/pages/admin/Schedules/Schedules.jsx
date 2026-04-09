import { useState, useEffect, useMemo } from 'react';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, Plus, X, Clock, MapPin, Users } from 'lucide-react';
import { Card, CardBody, CardHeader } from '../../../components/ui/Card';
import Button from '../../../components/ui/Button';
import Modal from '../../../components/ui/Modal';
import Input from '../../../components/ui/Input';
import { adminService } from '../../../services/adminService';
import styles from './Schedules.module.css';

// Helpers cho hiển thị tuần
const getStartOfWeek = (date) => {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is sunday
  return new Date(d.setDate(diff));
};

const formatDate = (date) => {
  return date.toISOString().split('T')[0];
};

const addDays = (date, days) => {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
};

// Cấu hình Timeline (07:00 đến 22:00 -> 15 tiếng * 2 = 30 block)
const START_HOUR = 7;
const END_HOUR = 22;
const TIME_BLOCKS = (END_HOUR - START_HOUR) * 2;

const Schedules = () => {
  const [currentWeekStart, setCurrentWeekStart] = useState(getStartOfWeek(new Date()));
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Dữ liệu tham chiếu
  const [classesList, setClassesList] = useState([]);
  const [roomsList, setRoomsList] = useState([]);

  // Modal Xếp/Sửa lịch
  const [modalOpen, setModalOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(null); // { date, time }
  
  const [form, setForm] = useState({
    class_id: '',
    schedule_date: '',
    start_time: '',
    end_time: '',
    room_id: '',
    notes: ''
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  // Lấy danh sách ngày trong tuần hiện tại
  const weekDays = useMemo(() => {
    const days = [];
    for (let i = 0; i < 7; i++) {
      days.push(addDays(currentWeekStart, i));
    }
    return days;
  }, [currentWeekStart]);

  const loadData = async () => {
    setLoading(true);
    try {
      const startStr = formatDate(weekDays[0]);
      const endStr = formatDate(weekDays[6]);
      
      const [schedRes, classRes] = await Promise.all([
        adminService.getSchedulesGrid({ from_date: startStr, to_date: endStr }),
        adminService.getClasses()
      ]);
      setSchedules(schedRes.data || []);
      setClassesList(classRes.data?.items || classRes.data || []);
      
      // Giả lập danh sách phòng nếu backend chưa có /rooms
      setRoomsList([{id:1, name:'Phòng 101'}, {id:2, name:'Phòng 102'}, {id:3, name:'Phòng 201'}]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, [currentWeekStart]);

  const handlePrevWeek = () => setCurrentWeekStart(prev => addDays(prev, -7));
  const handleNextWeek = () => setCurrentWeekStart(prev => addDays(prev, 7));
  const handleToday = () => setCurrentWeekStart(getStartOfWeek(new Date()));

  // Tính toán lưới
  const timeLabels = [];
  for (let h = START_HOUR; h < END_HOUR; h++) {
    timeLabels.push(`${h.toString().padStart(2, '0')}:00`);
    timeLabels.push(`${h.toString().padStart(2, '0')}:30`);
  }

  // --- Modal Handlers ---
  const handleCellClick = (d, tLabel) => {
    let endStr = '';
    // Mặc định tạo 1 buổi 1.5h
    if (tLabel) {
      const [h, m] = tLabel.split(':').map(Number);
      const endD = new Date(); endD.setHours(h, m + 90);
      endStr = `${endD.getHours().toString().padStart(2, '0')}:${endD.getMinutes().toString().padStart(2, '0')}`;
    }
    setForm({
      class_id: '',
      schedule_date: formatDate(d),
      start_time: tLabel || '19:00',
      end_time: endStr || '20:30',
      room_id: '',
      notes: ''
    });
    setEditMode(false);
    setSelectedSlot(null);
    setError('');
    setModalOpen(true);
  };

  const handleEventClick = (e, sched) => {
    e.stopPropagation();
    setForm({
      class_id: sched.class_.id,
      schedule_date: sched.schedule_date,
      start_time: sched.start_time,
      end_time: sched.end_time,
      room_id: sched.room_id || '',
      notes: sched.notes || ''
    });
    setSelectedSlot(sched);
    setEditMode(true);
    setError('');
    setModalOpen(true);
  };

  const handleChange = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.class_id || !form.schedule_date || !form.start_time || !form.end_time) {
      setError('Vui lòng nhập đủ thông tin (Lớp, Ngày, Bắt đầu, Kết thúc)'); return;
    }
    setSaving(true); setError('');
    
    // Setup payload
    const payload = { ...form };
    if (!payload.room_id) delete payload.room_id; // Clean empty string

    try {
      if (editMode && selectedSlot) {
        await adminService.updateSchedule(selectedSlot.id, payload);
      } else {
        await adminService.createSchedule(payload);
      }
      setModalOpen(false);
      loadData();
    } catch (err) {
      setError(err.response?.data?.message || 'Đã xảy ra lỗi khi lưu lịch');
    } finally { setSaving(false); }
  };

  const handleDelete = async () => {
    if (!window.confirm('Bạn có chắc chắn huỷ bỏ lịch này không?')) return;
    setSaving(true);
    try {
      await adminService.deleteSchedule(selectedSlot.id);
      setModalOpen(false);
      loadData();
    } catch (err) {
      alert('Lỗi: ' + (err.response?.data?.message || 'Không thể xoá'));
      setSaving(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleWrap}>
          <h2 className={styles.title}>Quản lý lịch dạy</h2>
          <p className={styles.desc}>Sắp xếp thời khóa biểu hàng tuần cho các lớp học</p>
        </div>
        <div className={styles.toolbar}>
          <div className={styles.weekNav}>
            <Button variant="secondary" onClick={handlePrevWeek} icon={<ChevronLeft size={16} />} />
            <Button variant="secondary" onClick={handleToday}>Tuần này</Button>
            <Button variant="secondary" onClick={handleNextWeek} icon={<ChevronRight size={16} />} />
          </div>
          <p className={styles.weekDisplay}>
            Tuần {formatDate(weekDays[0])} đến {formatDate(weekDays[6])}
          </p>
          <Button icon={<Plus size={16} />} onClick={() => handleCellClick(new Date(), '')}>Thêm lịch</Button>
        </div>
      </div>

      <Card>
        <CardBody noPadding>
          <div className={styles.gridContainer}>
            {/* Header Lưới (Các thứ trong tuần) */}
            <div className={styles.timeColumnHeader}>GMT+7</div>
            {weekDays.map((d, i) => {
              const strDate = d.toLocaleDateString('vi-VN', { weekday: 'short', day: '2-digit', month: '2-digit' });
              const isToday = formatDate(d) === formatDate(new Date());
              return (
                <div key={i} className={`${styles.dayHeader} ${isToday ? styles.today : ''}`}>
                  {strDate}
                </div>
              );
            })}

            {/* Các hàng giờ */}
            {timeLabels.map((timeLabel, index) => (
              <div key={`time-${index}`} className={styles.timeLabel} style={{ gridRow: index + 2, gridColumn: 1 }}>
                <span className={styles.timeText}>{timeLabel}</span>
              </div>
            ))}

            {/* Khung ô để click (Background Grid cells) */}
            {weekDays.map((d, dayIndex) => {
              return timeLabels.map((tLabel, tIndex) => (
                <div 
                  key={`cell-${dayIndex}-${tIndex}`}
                  className={styles.gridCell}
                  style={{ gridRow: tIndex + 2, gridColumn: dayIndex + 2 }}
                  onClick={() => handleCellClick(d, tLabel)}
                >
                </div>
              ));
            })}

            {/* Hiển thị các khối sự kiện (Schedule Blocks) */}
            {schedules.map(sched => {
              const dDate = new Date(sched.schedule_date);
              const dayIndex = weekDays.findIndex(wd => formatDate(wd) === formatDate(dDate));
              if (dayIndex === -1) return null;

              const [sh, sm] = sched.start_time.split(':').map(Number);
              const [eh, em] = sched.end_time.split(':').map(Number);

              const startRow = (sh - START_HOUR) * 2 + (sm >= 30 ? 1 : 0) + 2;
              const durationMins = (eh * 60 + em) - (sh * 60 + sm);
              const rowSpan = Math.ceil(durationMins / 30);

              return (
                <div 
                  key={sched.id} 
                  className={`${styles.eventBlock} ${sched.status === 'cancelled' ? styles.cancelled : ''}`}
                  style={{ 
                    gridColumn: dayIndex + 2, 
                    gridRow: `${startRow} / span ${rowSpan}` 
                  }}
                  onClick={(e) => handleEventClick(e, sched)}
                >
                  <div className={styles.eventTitle}>{sched.class_?.class_name}</div>
                  <div className={styles.eventSub}><Clock size={10} /> {sched.start_time.substring(0,5)} - {sched.end_time.substring(0,5)}</div>
                  {sched.teacher && <div className={styles.eventSub}><Users size={10} /> {sched.teacher.full_name}</div>}
                  {sched.room && <div className={styles.eventSub}><MapPin size={10} /> {sched.room.room_name}</div>}
                </div>
              );
            })}
          </div>
        </CardBody>
      </Card>

      {/* Modal Cấu hình 1 buổi học */}
      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editMode ? 'Chỉnh sửa lịch học' : 'Tạo lịch học mới'}>
        {error && <div style={{ color: 'var(--color-absent)', marginBottom: '1rem', fontSize: '0.875rem' }}>{error}</div>}
        <form className={styles.formSpace} onSubmit={handleSave}>
          <div className={styles.formGroup}>
            <label className={styles.label}>Lớp học *</label>
            <select name="class_id" value={form.class_id} onChange={handleChange} className={styles.select} required disabled={editMode}>
              <option value="">-- Chọn lớp học --</option>
              {classesList.map(c => <option key={c.id} value={c.id}>{c.class_name}</option>)}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <Input label="Ngày học *" name="schedule_date" type="date" value={form.schedule_date} onChange={handleChange} required disabled={editMode} />
            <div className={styles.formGroup}>
              <label className={styles.label}>Phòng học</label>
              <select name="room_id" value={form.room_id} onChange={handleChange} className={styles.select}>
                <option value="">-- Chọn phòng --</option>
                {roomsList.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
              </select>
            </div>
            <Input label="Giờ bắt đầu *" name="start_time" type="time" value={form.start_time} onChange={handleChange} required />
            <Input label="Giờ kết thúc *" name="end_time" type="time" value={form.end_time} onChange={handleChange} required />
          </div>

          <div className={styles.formGroup} style={{ marginTop: '0.5rem' }}>
            <label className={styles.label}>Ghi chú</label>
            <textarea name="notes" value={form.notes} onChange={handleChange} className={styles.select} rows={2} placeholder="Nội dung cần lưu ý cho buổi học này..." />
          </div>

          <div className={styles.modalFooter}>
            {editMode && (
              <Button variant="secondary" type="button" onClick={handleDelete} style={{ color: 'var(--color-absent)' }}>
                Xoá Lịch
              </Button>
            )}
            <div style={{ flex: 1 }}></div>
            <Button variant="secondary" type="button" onClick={() => setModalOpen(false)}>Huỷ</Button>
            <Button loading={saving} type="submit">{editMode ? 'Cập nhật' : 'Tạo lịch'}</Button>
          </div>
        </form>
      </Modal>

    </div>
  );
};

export default Schedules;

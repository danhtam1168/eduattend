import { useState, useEffect, useMemo } from 'react';
import { Calendar as CalendarIcon, CheckSquare, Square, Trash2, Clock, Users, Building2, Save, X } from 'lucide-react';
import { Card, CardBody } from '../../../components/ui/Card';
import Button from '../../../components/ui/Button';
import Modal from '../../../components/ui/Modal';
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
  const [globalTemplates, setGlobalTemplates] = useState([]); // All templates from DB to show in global view
  const [loading, setLoading] = useState(true);
  
  // Trạng thái hiển thị và thao tác
  const [visibleClasses, setVisibleClasses] = useState(new Set()); 
  const [activeClassId, setActiveClassId] = useState(null); 
  
  // Trạng thái Nháp (Draft) của lớp đang được cấu hình
  const [draftSchedules, setDraftSchedules] = useState([]);
  const [isDrafting, setIsDrafting] = useState(false);

  const [saving, setSaving] = useState(false);

  // States for Room Picker Modal
  const [roomModal, setRoomModal] = useState({ isOpen: false, day_of_week: null, start_time: '', end_time: '' });
  const [availableRooms, setAvailableRooms] = useState([]);
  const [loadingRooms, setLoadingRooms] = useState(false);
  const [selectedRoomId, setSelectedRoomId] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [classRes, tplRes] = await Promise.all([
        adminService.getClasses(),
        adminService.getClassSchedules() 
      ]);
      const cls = classRes.data?.items || classRes.data || [];
      setClassesList(cls);
      setGlobalTemplates(tplRes.data || []);
      
      // Mặc định hiển thị tất cả nếu chưa có activeClass
      if (!activeClassId) setVisibleClasses(new Set(cls.map(c => c.id)));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const timeLabels = useMemo(() => {
    const labels = [];
    for (let h = START_HOUR; h < END_HOUR; h++) {
      labels.push(`${h.toString().padStart(2, '0')}:00`);
      labels.push(`${h.toString().padStart(2, '0')}:30`);
    }
    return labels;
  }, []);

  const toggleVisibility = (classId) => {
    if (activeClassId) return; // Không cho toggle ngẫu nhiên nếu đang ở chế độ Draft
    const next = new Set(visibleClasses);
    if (next.has(classId)) next.delete(classId);
    else next.add(classId);
    setVisibleClasses(next);
  };

  const toggleAll = () => {
    if (activeClassId) return;
    if (visibleClasses.size === classesList.length) {
      setVisibleClasses(new Set());
    } else {
      setVisibleClasses(new Set(classesList.map(c => c.id)));
    }
  };

  const handleSelectActiveClass = (cId) => {
    if (activeClassId === cId) {
      // Hủy chế độ Draft
      if (isDrafting && !window.confirm('Bạn có thay đổi chưa lưu. Bạn có chắc muốn huỷ xếp lịch cho lớp này không?')) return;
      setActiveClassId(null);
      setIsDrafting(false);
      setDraftSchedules([]);
      setVisibleClasses(new Set(classesList.map(c => c.id)));
    } else {
      if (isDrafting && !window.confirm('Bạn có thay đổi chưa lưu ở lớp trước. Chuyển sang lớp khác sẽ mất lịch nháp này?')) return;
      setActiveClassId(cId);
      setVisibleClasses(new Set([cId]));
      // Nạp templates hiện có của lớp này vào Drafting board
      const existing = globalTemplates.filter(t => t.class_id === cId);
      // Tạo draft copy
      setDraftSchedules(existing.map(t => ({ ...t, isDraft: false })));
      setIsDrafting(false); // Chưa có chỉnh sửa
    }
  };

  // Click vào lưới
  const handleCellClick = async (dayOfWeek, timeStr) => {
    if (!activeClassId) return; // Không cho phép thao tác ở Global View

    // Mặc định 1.5h
    const [h, m] = timeStr.split(':').map(Number);
    const endH = h + Math.floor((m + 90) / 60);
    const endM = (m + 90) % 60;
    const endStr = `${endH.toString().padStart(2, '0')}:${endM.toString().padStart(2, '0')}`;

    // Khởi tạo Modal chọn phòng
    setRoomModal({ isOpen: true, day_of_week: dayOfWeek, start_time: timeStr, end_time: endStr });
    setSelectedRoomId('');
    setLoadingRooms(true);
    
    // Gọi API lọc phòng trống
    try {
      const res = await adminService.getRooms({ 
        status: 'available', 
        day_of_week: dayOfWeek, 
        start_time: timeStr, 
        end_time: endStr 
      });
      setAvailableRooms(res.data || []);
    } catch(err) {
      alert("Lỗi tải danh sách phòng khả dụng");
    } finally {
      setLoadingRooms(false);
    }
  };

  const handleAddDraftSchedule = () => {
    if (!selectedRoomId && availableRooms.length > 0) {
       if(!window.confirm("Bạn chưa chọn phòng. Vẫn tiếp tục tạo lịch nháp (có thể báo lỗi nếu phòng là bắt buộc)?")) return;
    }
    const rInfo = availableRooms.find(r => r.id === parseInt(selectedRoomId));

    const newDraft = {
      id: `draft_${Date.now()}`,
      day_of_week: roomModal.day_of_week,
      start_time: roomModal.start_time,
      end_time: roomModal.end_time,
      room_id: selectedRoomId ? parseInt(selectedRoomId) : null,
      room: rInfo ? rInfo : null,
      isDraft: true
    };

    setDraftSchedules([...draftSchedules, newDraft]);
    setIsDrafting(true);
    setRoomModal({ ...roomModal, isOpen: false });
  };

  const handleDeleteDraft = (e, index) => {
    e.stopPropagation();
    const newDrafts = [...draftSchedules];
    newDrafts.splice(index, 1);
    setDraftSchedules(newDrafts);
    setIsDrafting(true);
  };

  const handleSaveBulk = async () => {
    if (!activeClassId) return;
    setSaving(true);
    try {
      await adminService.createBulkClassSchedules({
        class_id: activeClassId,
        schedules: draftSchedules
      });
      alert('Đã chốt thời khóa biểu thành công!');
      setIsDrafting(false);
      loadData(); // Tải lại global data
    } catch (err) {
      alert(err.response?.data?.message || 'Lỗi khi lưu thời khóa biểu');
    } finally {
      setSaving(false);
    }
  };

  const getClassColor = (classId) => {
    const colors = ['#DBEAFE', '#D1FAE5', '#FEF3C7', '#FEE2E2', '#E0E7FF', '#FCE7F3', '#FEF08A', '#A7F3D0'];
    const textColors = ['#1E3A8A', '#065F46', '#92400E', '#991B1B', '#3730A3', '#9D174D', '#854D0E', '#064E3B'];
    const idx = classId % colors.length;
    return { bg: colors[idx], text: textColors[idx], border: textColors[idx] };
  };

  const activeClass = classesList.find(c => c.id === activeClassId);

  // Chọn nguồn dữ liệu để hiển thị: Nếu dang edit thì show draft array, ngược lại show global
  const renderSchedules = activeClassId 
    ? draftSchedules.map((tpl, i) => ({ ...tpl, _sourceIdx: i })) 
    : globalTemplates.filter(t => visibleClasses.has(t.class_id));

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleWrapWrap} style={{display:'flex', justifyContent:'space-between', alignItems:'flex-start'}}>
          <div className={styles.titleWrap}>
            <h2 className={styles.title}>Cấu hình Mẫu Thời Khóa Biểu</h2>
            <p className={styles.desc}>
              {activeClassId 
                ? "Bấm vào các ô trống trên lưới để sắp lịch cho lớp hiện tại. Nhấn Xác nhận để chốt."
                : "Bấm vào một lớp bên trái để kích hoạt chế độ xếp lịch cho lớp đó."}
            </p>
          </div>
          {activeClassId && (
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <Button variant="secondary" onClick={() => handleSelectActiveClass(activeClassId)}>Huỷ</Button>
              <Button onClick={handleSaveBulk} loading={saving} icon={<Save size={16} />}>
                Xác nhận lưu ({draftSchedules.length} ca)
              </Button>
            </div>
          )}
        </div>
      </div>

      <div className={styles.layout}>
        <div className={styles.sidebar}>
          <div className={styles.sidebarHeader}>
            <h3 className={styles.sidebarTitle}>Danh sách lớp</h3>
            <button className={styles.iconBtn} onClick={toggleAll} title="Chọn hiển thị tất cả" disabled={!!activeClassId}>
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
                  <button className={styles.visToggle} onClick={() => toggleVisibility(c.id)} disabled={!!activeClassId}>
                    {isVisible ? <CheckSquare size={14} color={activeClassId ? '#D1D5DB' : '#4B5563'} /> : <Square size={14} color="#9CA3AF" />}
                  </button>
                  <button 
                    className={styles.classBtn} 
                    onClick={() => handleSelectActiveClass(c.id)}
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
              Đang xếp lịch cho <strong>{activeClass?.class_name}</strong>
              {isDrafting && <div style={{marginTop:'0.5rem', fontSize:'0.75rem', color:'#991B1B', fontWeight:'600'}}>Bạn có thay đổi chưa lưu!</div>}
            </div>
          )}
        </div>

        <div className={styles.mainGrid}>
          <div className={styles.gridContainer}>
            <div className={styles.timeColumnHeader}>GMT+7</div>
            {DAYS.map(d => (
              <div key={d.id} className={styles.dayHeader}>
                {d.name}
              </div>
            ))}

            {timeLabels.map((timeLabel, index) => (
              <div key={`time-${index}`} className={styles.timeLabel} style={{ gridRow: index + 2, gridColumn: 1 }}>
                <span className={styles.timeText}>{timeLabel}</span>
              </div>
            ))}

            {DAYS.map((d, dayIndex) => {
              return timeLabels.map((tLabel, tIndex) => (
                <div 
                  key={`cell-${d.id}-${tIndex}`}
                  className={`${styles.gridCell} ${activeClassId ? styles.gridCellClickable : styles.gridCellDisabled}`}
                  style={{ gridRow: tIndex + 2, gridColumn: dayIndex + 2 }}
                  onClick={() => handleCellClick(d.id, tLabel)}
                >
                </div>
              ));
            })}

            {renderSchedules.map((tpl) => {
              const dayIndex = DAYS.findIndex(d => d.id === tpl.day_of_week);
              if (dayIndex === -1) return null;

              const [sh, sm] = tpl.start_time.split(':').map(Number);
              const [eh, em] = tpl.end_time.split(':').map(Number);
              const startRow = (sh - START_HOUR) * 2 + (sm >= 30 ? 1 : 0) + 2;
              const durationMins = (eh * 60 + em) - (sh * 60 + sm);
              const rowSpan = Math.ceil(durationMins / 30);
              
              // Trong chế độ Draft, mượn mã màu của activeClass
              const targetClassId = activeClassId ? activeClassId : tpl.class_id;
              const color = getClassColor(targetClassId);
              
              // Nếu là bản nháp đang edit thì kẻ sọc
              const isDraftModeBlock = activeClassId && tpl.isDraft;

              return (
                <div 
                  key={`${tpl.id || 'draft'}-${dayIndex}-${startRow}`} 
                  className={`${styles.eventBlock} ${isDraftModeBlock ? styles.draftBlock : ''}`}
                  style={{ 
                    gridColumn: dayIndex + 2, 
                    gridRow: `${startRow} / span ${rowSpan}`,
                    backgroundColor: color.bg,
                    borderLeftColor: color.border,
                    color: color.text,
                    ...(isDraftModeBlock && {
                       backgroundImage: `repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.5) 10px, rgba(255,255,255,0.5) 20px)`
                    })
                  }}
                  title={`[${activeClass?.class_name || tpl.class_name}] ${tpl.start_time.substring(0,5)} - ${tpl.end_time.substring(0,5)}`}
                >
                  <div className={styles.eventTitle}>{activeClassId ? activeClass?.class_name : tpl.class_name}</div>
                  <div className={styles.eventSub}><Clock size={10} /> {tpl.start_time.substring(0,5)} - {tpl.end_time.substring(0,5)}</div>
                  {(tpl.room_name || tpl.room) && <div className={styles.eventSub}><Building2 size={10} /> {tpl.room?.room_name || tpl.room_name}</div>}
                  
                  {activeClassId && (
                    <button className={styles.deleteBtn} onClick={(e) => handleDeleteDraft(e, tpl._sourceIdx)}>
                      <Trash2 size={13} color={color.text} />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Modal Chọn Phòng Trống */}
      <Modal isOpen={roomModal.isOpen} onClose={() => setRoomModal({ ...roomModal, isOpen: false })} title="Chọn phòng cho ca học">
        <div style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: '#F3F4F6', borderRadius: '6px' }}>
          <div style={{ fontWeight: 600, color: '#374151', marginBottom: '0.25rem' }}>Khung giờ: {DAYS.find(d=>d.id===roomModal.day_of_week)?.name} ({roomModal.start_time} - {roomModal.end_time})</div>
          <div style={{ fontSize: '0.875rem', color: '#6B7280' }}>Hệ thống đã tự động lọc để loại bỏ các phòng bị trùng giờ với các lớp khác.</div>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.5rem' }}>Chọn phòng khả dụng</label>
          {loadingRooms ? (
            <p style={{fontSize:'0.875rem'}}>Đang tải danh sách phòng...</p>
          ) : (
            <select 
              value={selectedRoomId} 
              onChange={(e) => setSelectedRoomId(e.target.value)}
              style={{ width: '100%', padding: '0.625rem', borderRadius: '6px', border: '1px solid #D1D5DB' }}
            >
              <option value="">-- Nếu không có ai chọn phòng thì bỏ trống --</option>
              {availableRooms.map(r => (
                <option key={r.id} value={r.id}>{r.room_name} (Chứa {r.capacity})</option>
              ))}
            </select>
          )}
          {!loadingRooms && availableRooms.length === 0 && (
            <p style={{marginTop:'0.5rem', color:'var(--color-absent)', fontSize:'0.875rem'}}>Cảnh báo: Hiện không có phòng trống ở khung giờ này.</p>
          )}
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', borderTop: '1px solid #E5E7EB', paddingTop: '1rem' }}>
          <Button variant="secondary" onClick={() => setRoomModal({ ...roomModal, isOpen: false })}>Huỷ</Button>
          <Button onClick={handleAddDraftSchedule}>Thêm ca này vào lịch</Button>
        </div>
      </Modal>

    </div>
  );
};

export default Schedules;

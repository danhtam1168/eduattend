import { useState, useEffect } from 'react';
import { Plus, Search, Edit2, Users, Trash2 } from 'lucide-react';
import { Card, CardBody, CardHeader } from '../../../components/ui/Card';
import Table from '../../../components/ui/Table';
import Badge from '../../../components/ui/Badge';
import Button from '../../../components/ui/Button';
import Modal from '../../../components/ui/Modal';
import Input from '../../../components/ui/Input';
import { adminService } from '../../../services/adminService';
import styles from './Classes.module.css';

const initForm = { class_name: '', subject_id: '', teacher_id: '', start_date: '', end_date: '', limit_students: 20 };

const Classes = () => {
  const [classes, setClasses] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);

  // Modal thêm/sửa lớp
  const [modalOpen, setModalOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [form, setForm] = useState(initForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  // Modal quản lý học sinh trong lớp
  const [studentModalOpen, setStudentModalOpen] = useState(false);
  const [selectedClass, setSelectedClass] = useState(null);
  const [enrolledStudents, setEnrolledStudents] = useState([]);
  const [allStudents, setAllStudents] = useState([]);
  const [studentToAdd, setStudentToAdd] = useState('');
  const [enrollLoading, setEnrollLoading] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [clsRes, teaRes, subRes, stuRes] = await Promise.all([
        adminService.getClasses(),
        adminService.getTeachers(),
        adminService.getSubjects(),
        adminService.getStudents()
      ]);
      setClasses(clsRes.data?.items || clsRes.data || []);
      setTeachers(teaRes.data?.items || teaRes.data || []);
      setSubjects(subRes.data || []);
      setAllStudents(stuRes.data?.items || stuRes.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(classes.filter(c =>
      c.class_name?.toLowerCase().includes(q) ||
      c.subject?.subject_name?.toLowerCase().includes(q) ||
      c.teacher?.full_name?.toLowerCase().includes(q)
    ));
  }, [search, classes]);

  const openCreate = () => { setEditItem(null); setForm(initForm); setError(''); setModalOpen(true); };
  const openEdit = (c) => { 
    setEditItem(c); 
    setForm({ 
      class_name: c.class_name, 
      subject_id: c.subject_id, 
      teacher_id: c.teacher_id, 
      start_date: c.start_date || '', 
      end_date: c.end_date || '', 
      limit_students: c.limit_students 
    }); 
    setError(''); setModalOpen(true); 
  };
  const closeModal = () => { setModalOpen(false); setError(''); };
  const handleChange = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.class_name || !form.subject_id || !form.teacher_id || !form.start_date) {
      setError('Vui lòng nhập đủ tên lớp, môn học, giáo viên và ngày bắt đầu');
      return;
    }
    setSaving(true);
    setError('');
    try {
      if (editItem) {
        await adminService.updateClass(editItem.id, form);
      } else {
        await adminService.createClass(form);
      }
      closeModal();
      loadData();
    } catch (err) {
      setError(err.response?.data?.message || 'Đã xảy ra lỗi');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (e, classId, className) => {
    e.stopPropagation();
    if (!window.confirm(`Bạn có chắc muốn xoá lớp học "${className}" không? Các dữ liệu đã sinh ra sẽ bị mất!`)) return;
    try {
      await adminService.deleteClass(classId);
      loadData();
    } catch (err) {
      alert(err.response?.data?.message || 'Lỗi khi xoá lớp học');
    }
  };

  // --- QUẢN LÝ HỌC SINH ---
  const openManageStudents = async (c) => {
    setSelectedClass(c);
    setEnrolledStudents([]);
    setStudentToAdd('');
    setStudentModalOpen(true);
    await loadClassStudents(c.id);
  };

  const loadClassStudents = async (classId) => {
    try {
      const res = await adminService.getClassStudents(classId);
      setEnrolledStudents(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddStudent = async () => {
    if (!studentToAdd) return;
    setEnrollLoading(true);
    try {
      await adminService.enrollStudent(selectedClass.id, studentToAdd);
      setStudentToAdd('');
      await loadClassStudents(selectedClass.id);
      loadData(); // Update count
    } catch (err) {
      alert(err.response?.data?.message || 'Lỗi đăng ký học sinh');
    } finally {
      setEnrollLoading(false);
    }
  };

  const handleRemoveStudent = async (enrollmentId, studentName, studentId) => {
    if (!window.confirm(`Rút học sinh "${studentName}" khỏi lớp này?`)) return;
    try {
      await adminService.removeStudentFromClass(selectedClass.id, studentId);
      await loadClassStudents(selectedClass.id);
      loadData(); // Update count
    } catch (err) {
      alert(err.response?.data?.message || 'Lỗi khi huỷ học phần');
    }
  };

  const columns = [
    { key: 'class_name', title: 'Tên lớp', render: (v) => <strong>{v}</strong> },
    { key: 'subject', title: 'Môn học', render: (_, r) => r.subject?.name },
    { key: 'teacher', title: 'Giáo viên', render: (_, r) => r.teacher?.full_name },
    { 
      key: 'students', 
      title: 'Học sinh', 
      width: '300px',
      render: (_, r) => {
        if (!r.students || r.students.length === 0) {
          return <span style={{ color: '#9CA3AF' }}>0 / {r.max_students}</span>;
        }
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            <div style={{ fontSize: '0.75rem', color: '#6B7280', marginBottom: '0.25rem' }}>
              {r.students.length} / {r.max_students} học sinh
            </div>
            <table className={styles.nestedTable}>
              <tbody>
                {r.students.map(s => (
                  <tr key={s.student_id}>
                    <td>{s.full_name}</td>
                    <td style={{ color: '#6B7280', fontSize: '0.75rem' }}>{s.schedule}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }
    },
    { key: 'formatted_schedule', title: 'Lịch học', render: (v) => <span style={{fontSize:'0.875rem', fontWeight:'500'}}>{v || 'Chưa xếp lịch'}</span> },
    { key: 'start_date', title: 'Khởi tạo', render: (v) => <span style={{fontSize:'0.875rem'}}>{v}</span> },
    {
      key: 'status', title: 'Trạng thái',
      render: (v) => <Badge color={v === 'active' ? 'present' : 'absent'}>{v === 'active' ? 'Hoạt động' : 'Đã đóng'}</Badge>
    },
    {
      key: 'id', title: 'Thao tác', width: '160px',
      render: (_, row) => (
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <Button size="sm" variant="secondary" icon={<Edit2 size={13} />} onClick={() => openEdit(row)}>Sửa</Button>
          <Button size="sm" variant="primary" icon={<Users size={13} />} onClick={() => openManageStudents(row)}>Học sinh</Button>
          <Button size="sm" variant="ghost" icon={<Trash2 size={13} color="var(--color-absent)" />} onClick={(e) => handleDelete(e, row.id, row.class_name)} />
        </div>
      )
    }
  ];

  return (
    <>
      <div className={styles.toolbar}>
        <div className={styles.searchWrap}>
          <Search size={15} className={styles.searchIcon} />
          <input
            className={styles.searchInput}
            placeholder="Tìm kiếm lớp học..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <Button icon={<Plus size={16} />} onClick={openCreate}>Tạo lớp học</Button>
      </div>

      <Card>
        <CardBody noPadding>
          <Table columns={columns} data={loading ? [] : filtered} emptyText={loading ? 'Đang tải...' : 'Chưa có lớp học nào'} />
        </CardBody>
      </Card>

      {/* Modal Lớp học */}
      <Modal isOpen={modalOpen} onClose={closeModal} title={editItem ? 'Sửa lớp học' : 'Tạo lớp học mới'} size="md"
        footer={<><Button variant="secondary" onClick={closeModal}>Huỷ</Button><Button loading={saving} onClick={handleSave}>Lưu</Button></>}>
        {error && <div style={{ color: 'var(--color-absent)', marginBottom: '1rem', fontSize: '0.875rem' }}>{error}</div>}
        <form className={styles.formGrid} onSubmit={handleSave}>
          <Input label="Tên lớp" name="class_name" value={form.class_name} onChange={handleChange} required />
          
          <div className={styles.inputGroup}>
            <label className={styles.label}>Môn học *</label>
            <select name="subject_id" value={form.subject_id} onChange={handleChange} className={styles.select} required>
              <option value="">-- Chọn môn học --</option>
              {subjects.map(s => <option key={s.id} value={s.id}>{s.subject_name}</option>)}
            </select>
          </div>

          <div className={styles.inputGroup}>
            <label className={styles.label}>Giáo viên *</label>
            <select name="teacher_id" value={form.teacher_id} onChange={handleChange} className={styles.select} required>
              <option value="">-- Chọn giáo viên --</option>
              {teachers.map(t => <option key={t.id} value={t.id}>{t.full_name} ({t.teacher_code})</option>)}
            </select>
          </div>

          <Input label="Ngày khai giảng" name="start_date" type="date" value={form.start_date} onChange={handleChange} required />
          <Input label="Ngày kết thúc (Không bắt buộc)" name="end_date" type="date" value={form.end_date} onChange={handleChange} />
          <Input label="Sĩ số tối đa" type="number" name="limit_students" value={form.limit_students} onChange={handleChange} min={1} required />
          
          {editItem && (
            <div className={styles.inputGroup}>
              <label className={styles.label}>Trạng thái</label>
              <select name="status" value={form.status || 'active'} onChange={handleChange} className={styles.select}>
                <option value="active">Hoạt động</option>
                <option value="completed">Đã kết thúc</option>
                <option value="cancelled">Đã huỷ</option>
              </select>
            </div>
          )}
        </form>
      </Modal>

      {/* Modal Học sinh */}
      <Modal isOpen={studentModalOpen} onClose={() => setStudentModalOpen(false)} title={`Danh sách học sinh - ${selectedClass?.class_name}`} size="lg">
        <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem' }}>
          <select 
            value={studentToAdd} 
            onChange={e => setStudentToAdd(e.target.value)}
            className={styles.select} 
            style={{ flex: 1 }}
          >
            <option value="">-- Chọn học sinh để thêm vào lớp --</option>
            {allStudents.filter(s => !enrolledStudents.find(e => e.student_id === s.id)).map(st => (
              <option key={st.id} value={st.id}>{st.full_name} ({st.student_code})</option>
            ))}
          </select>
          <Button onClick={handleAddStudent} loading={enrollLoading} disabled={!studentToAdd}>Thêm vào lớp</Button>
        </div>

        <div className={styles.tableWrapper}>
          <table className={styles.miniTable}>
            <thead>
              <tr>
                <th>Mã HS</th>
                <th>Tên học sinh</th>
                <th>Ngày tham gia</th>
                <th>Trạng thái</th>
                <th>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {enrolledStudents.length === 0 ? (
                <tr><td colSpan="5" style={{ textAlign: 'center', padding: '2rem' }}>Chưa có học sinh trong lớp</td></tr>
              ) : (
                enrolledStudents.map(enr => (
                  <tr key={enr.id}>
                    <td>{enr.student?.student_code}</td>
                    <td><strong>{enr.student?.full_name}</strong></td>
                    <td>{enr.enrollment_date}</td>
                    <td>
                      <Badge color={enr.status === 'active' ? 'present' : 'absent'}>{enr.status}</Badge>
                    </td>
                    <td>
                      <button className={styles.iconBtn} onClick={() => handleRemoveStudent(enr.id, enr.student?.full_name, enr.student?.id)}>
                        <Trash2 size={16} color="var(--color-absent)" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Modal>
    </>
  );
};

export default Classes;

import { useState, useEffect } from 'react';
import { Plus, Search, Edit2, Trash2, BookOpen } from 'lucide-react';
import { Card, CardBody } from '../../../components/ui/Card';
import Table from '../../../components/ui/Table';
import Badge from '../../../components/ui/Badge';
import Button from '../../../components/ui/Button';
import Modal from '../../../components/ui/Modal';
import Input from '../../../components/ui/Input';
import { adminService } from '../../../services/adminService';
import styles from './Subjects.module.css';

const initForm = {
  subject_name: '',
  subject_code: '',
  description: '',
  grade_level: '',
  fee_per_session: '',
  duration_minutes: 90,
  is_active: true
};

const Subjects = () => {
  const [subjects, setSubjects] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [search,   setSearch]   = useState('');
  
  const [modalOpen, setModalOpen] = useState(false);
  const [editItem,  setEditItem]  = useState(null);
  const [form,      setForm]      = useState(initForm);
  const [saving,    setSaving]    = useState(false);
  const [error,     setError]     = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const res = await adminService.getSubjects();
      setSubjects(res.data || []);
    } catch(e) {
      console.error(e);
      setSubjects([]);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(subjects.filter(s =>
      s.subject_name?.toLowerCase().includes(q) ||
      s.subject_code?.toLowerCase().includes(q) ||
      s.grade_level?.toLowerCase().includes(q)
    ));
  }, [search, subjects]);

  const openCreate = () => { setEditItem(null); setForm(initForm); setError(''); setModalOpen(true); };
  const openEdit   = (s)  => { setEditItem(s); setForm(s); setError(''); setModalOpen(true); };
  const closeModal = ()   => { setModalOpen(false); setError(''); };

  const handleChange = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.subject_name || !form.fee_per_session) {
      setError('Vui lòng nhập tên môn học và học phí'); return;
    }
    
    setSaving(true);
    setError('');
    
    const payload = { 
      ...form, 
      fee_per_session: parseFloat(form.fee_per_session) || 0,
      duration_minutes: parseInt(form.duration_minutes) || 90
    };
    
    try {
      if (editItem) {
        await adminService.updateSubject(editItem.id, payload);
      } else {
        await adminService.createSubject(payload);
      }
      closeModal();
      load();
    } catch (err) {
      setError(err.response?.data?.message || 'Đã xảy ra lỗi');
    } finally { setSaving(false); }
  };

  const handleDelete = async (e, subjectId, name) => {
    e.stopPropagation();
    if (!window.confirm(`Bạn có chắc muốn xoá (ẩn) môn học "${name}"?`)) return;
    try {
      await adminService.deleteSubject(subjectId);
      load();
    } catch (err) {
      alert(err.response?.data?.message || 'Lỗi khi xoá môn học');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
  };

  const columns = [
    {
      key: 'subject_name', title: 'Tên môn học',
      render: (v, row) => (
        <div className={styles.nameCell}>
          <div className={styles.iconBox}><BookOpen size={16} /></div>
          <div>
            <div className={styles.subjectName}><strong>{v}</strong></div>
            <div className={styles.subjectCode}>{row.subject_code || 'Chưa có mã'}</div>
          </div>
        </div>
      )
    },
    { key: 'grade_level',  title: 'Khối lớp' },
    { key: 'fee_per_session',  title: 'Học phí/buổi', render: (v) => formatCurrency(v) },
    { key: 'duration_minutes',  title: 'Thời lượng', render: (v) => `${v} phút` },
    {
      key: 'id', title: 'Thao tác', width: '120px',
      render: (_, row) => (
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <Button size="sm" variant="secondary" icon={<Edit2 size={13} />} onClick={() => openEdit(row)}>Sửa</Button>
          <Button size="sm" variant="ghost" icon={<Trash2 size={13} color="var(--color-absent)" />} onClick={(e) => handleDelete(e, row.id, row.subject_name)} />
        </div>
      )
    },
  ];

  return (
    <>
      <div className={styles.toolbar}>
        <div className={styles.searchWrap}>
          <Search size={15} className={styles.searchIcon} />
          <input
            className={styles.searchInput}
            placeholder="Tìm kiếm môn học, khối lớp..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <Button icon={<Plus size={16} />} onClick={openCreate}>
          Thêm môn học mới
        </Button>
      </div>

      <Card>
        <CardBody noPadding>
          <Table
            columns={columns}
            data={loading ? [] : filtered}
            emptyText={loading ? 'Đang tải...' : 'Không có môn học nào'}
          />
        </CardBody>
      </Card>

      <Modal
        isOpen={modalOpen}
        onClose={closeModal}
        title={editItem ? 'Chỉnh sửa môn học' : 'Thêm môn học mới'}
        size="md"
        footer={
          <>
            <Button variant="secondary" onClick={closeModal}>Huỷ</Button>
            <Button loading={saving} onClick={handleSave} type="submit">
              {editItem ? 'Lưu thay đổi' : 'Tạo mới'}
            </Button>
          </>
        }
      >
        {error && <div style={{ color: 'var(--color-absent)', marginBottom: '1rem', fontSize: '0.875rem' }}>{error}</div>}
        <form className={styles.formGrid} onSubmit={handleSave}>
          <Input label="Tên môn học" name="subject_name" value={form.subject_name} onChange={handleChange}
            placeholder="VD: Toán học" required />
            
          <Input label="Mã môn học" name="subject_code" value={form.subject_code} onChange={handleChange}
            placeholder="VD: MATH01" />
            
          <Input label="Khối lớp" name="grade_level" value={form.grade_level} onChange={handleChange}
            placeholder="VD: Lớp 10" />
            
          <Input label="Học phí / buổi (VNĐ)" name="fee_per_session" type="number" value={form.fee_per_session} onChange={handleChange}
            placeholder="VD: 100000" required />

          <Input label="Thời lượng (phút)" name="duration_minutes" type="number" value={form.duration_minutes} onChange={handleChange}
            placeholder="VD: 90" />
            
          <Input label="Mô tả" name="description" value={form.description} onChange={handleChange}
            placeholder="Mô tả ngắn về môn học..." className={styles.formFull} />
        </form>
      </Modal>
    </>
  );
};

export default Subjects;

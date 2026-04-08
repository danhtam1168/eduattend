import { useState, useEffect } from 'react';
import { UserPlus, Search, Edit2 } from 'lucide-react';
import { Card, CardBody } from '../../../components/ui/Card';
import Table from '../../../components/ui/Table';
import Badge from '../../../components/ui/Badge';
import Button from '../../../components/ui/Button';
import Modal from '../../../components/ui/Modal';
import Input from '../../../components/ui/Input';
import { adminService } from '../../../services/adminService';
import styles from '../Teachers/Teachers.module.css';

const initForm = { name: '', class_name: '', phone: '', note: '' };

const Students = () => {
  const [students, setStudents] = useState([]);
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
      const res = await adminService.getStudents();
      setStudents(res.data || []);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);
  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(students.filter(s =>
      s.name.toLowerCase().includes(q) ||
      (s.class_name || '').toLowerCase().includes(q)
    ));
  }, [search, students]);

  const openCreate = () => { setEditItem(null); setForm(initForm); setError(''); setModalOpen(true); };
  const openEdit = (s) => { setEditItem(s); setForm(s); setError(''); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setError(''); };
  const handleChange = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.name) { setError('Vui lòng nhập tên học sinh'); return; }
    setSaving(true); setError('');
    try {
      if (editItem) await adminService.updateStudent(editItem.id, form);
      else          await adminService.createStudent(form);
      closeModal(); load();
    } catch (err) {
      setError(err.response?.data?.message || 'Đã xảy ra lỗi');
    } finally { setSaving(false); }
  };

  const handleToggle = async (s) => {
    if (!window.confirm(`${s.is_active ? 'Khoá' : 'Kích hoạt'} học sinh "${s.name}"?`)) return;
    await adminService.updateStudent(s.id, { is_active: !s.is_active });
    load();
  };

  const columns = [
    { key: 'name', title: 'Tên học sinh', render: (v) => <strong>{v}</strong> },
    { key: 'class_name', title: 'Lớp / Khối' },
    { key: 'phone',      title: 'Điện thoại' },
    { key: 'note',       title: 'Ghi chú' },
    {
      key: 'is_active', title: 'Trạng thái',
      render: (v) => <Badge color={v ? 'present' : 'absent'}>{v ? 'Đang học' : 'Nghỉ học'}</Badge>
    },
    {
      key: 'id', title: 'Thao tác', width: '140px',
      render: (_, row) => (
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <Button size="sm" variant="secondary" icon={<Edit2 size={13} />} onClick={() => openEdit(row)}>Sửa</Button>
          <Button size="sm" variant={row.is_active ? 'ghost' : 'primary'} onClick={() => handleToggle(row)}>
            {row.is_active ? 'Khoá' : 'Kích hoạt'}
          </Button>
        </div>
      )
    }
  ];

  return (
    <>
      <div className={styles.toolbar}>
        <div className={styles.searchWrap}>
          <Search size={15} className={styles.searchIcon} />
          <input className={styles.searchInput} placeholder="Tìm kiếm học sinh..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <Button icon={<UserPlus size={16} />} onClick={openCreate}>Thêm học sinh</Button>
      </div>

      <Card>
        <CardBody noPadding>
          <Table columns={columns} data={loading ? [] : filtered} emptyText={loading ? 'Đang tải...' : 'Chưa có học sinh nào'} />
        </CardBody>
      </Card>

      <Modal isOpen={modalOpen} onClose={closeModal} title={editItem ? 'Chỉnh sửa học sinh' : 'Thêm học sinh mới'} size="md"
        footer={<><Button variant="secondary" onClick={closeModal}>Huỷ</Button><Button loading={saving} onClick={handleSave}>Lưu</Button></>}>
        {error && <div style={{ color: 'var(--color-absent)', marginBottom: '1rem', fontSize: '0.875rem' }}>{error}</div>}
        <form className={styles.formGrid} onSubmit={handleSave}>
          <Input label="Tên học sinh" name="name" value={form.name} onChange={handleChange} placeholder="Nguyễn Văn A" required className={styles.formFull} />
          <Input label="Lớp / Khối" name="class_name" value={form.class_name} onChange={handleChange} placeholder="VD: Lớp 12" />
          <Input label="Điện thoại phụ huynh" name="phone" value={form.phone} onChange={handleChange} placeholder="0901..." />
          <Input label="Ghi chú" name="note" value={form.note} onChange={handleChange} placeholder="Ghi chú..." className={styles.formFull} />
        </form>
      </Modal>
    </>
  );
};

export default Students;

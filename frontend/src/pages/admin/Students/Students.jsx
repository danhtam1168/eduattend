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

const initForm = { 
  full_name: '', 
  date_of_birth: '', 
  address: '', 
  parent_phone: '', 
  phone: '', 
  notes: '', 
  referred_by: '' 
};

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
      setStudents(res.data?.items || res.data || []);
    } catch(e) {
      console.error(e);
      setStudents([]);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);
  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(students.filter(s =>
      s.full_name?.toLowerCase().includes(q) ||
      (s.address || '').toLowerCase().includes(q) ||
      (s.student_code || '').toLowerCase().includes(q)
    ));
  }, [search, students]);

  const openCreate = () => { setEditItem(null); setForm(initForm); setError(''); setModalOpen(true); };
  const openEdit = (s) => { 
    setEditItem(s); 
    setForm({
      ...s,
      date_of_birth: s.date_of_birth || '',
      address: s.address || '',
      parent_phone: s.parent_phone || '',
      phone: s.phone || '',
      referred_by: s.referred_by || '',
      notes: s.notes || ''
    }); 
    setError(''); 
    setModalOpen(true); 
  };
  const closeModal = () => { setModalOpen(false); setError(''); };
  const handleChange = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.full_name) { setError('Vui lòng nhập họ tên học sinh'); return; }
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
    if (!window.confirm(`${s.is_active ? 'Khoá' : 'Kích hoạt'} học sinh "${s.full_name}"?`)) return;
    await adminService.deactivateStudent?.(s.id) || await adminService.updateStudent?.(s.id, { is_active: !s.is_active });
    load();
  };

  const columns = [
    { 
      key: 'full_name', 
      title: 'Tên học sinh', 
      render: (v, row) => (
        <div>
          <strong>{v}</strong>
          {row.referred_by_name && (
            <div style={{ fontSize: '0.75rem', color: 'var(--color-present)', fontStyle: 'italic', marginTop: '2px' }}>
              ({row.referred_by_name})
            </div>
          )}
          <div style={{ fontSize: '0.7rem', color: '#9ca3af', marginTop: '2px' }}>{row.student_code}</div>
        </div>
      ) 
    },
    { key: 'date_of_birth', title: 'Ngày sinh', render: (v) => v ? new Date(v).toLocaleDateString('vi-VN') : '-' },
    { key: 'address', title: 'Địa chỉ' },
    { 
      key: 'contact', 
      title: 'Liên hệ', 
      render: (_, r) => (
        <div style={{ fontSize: '0.875rem' }}>
          <div>P: {r.parent_phone || '-'}</div>
          <div>S: {r.phone || '-'}</div>
        </div>
      ) 
    },
    { key: 'notes',       title: 'Ghi chú' },
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
          <Input label="Họ tên học sinh" name="full_name" value={form.full_name} onChange={handleChange} placeholder="Nguyễn Văn A" required className={styles.formFull} />
          <Input label="Ngày sinh" name="date_of_birth" type="date" value={form.date_of_birth} onChange={handleChange} />
          <Input label="Địa chỉ" name="address" value={form.address} onChange={handleChange} placeholder="Địa chỉ nhà / Trường học" />
          <Input label="Điện thoại phụ huynh" name="parent_phone" value={form.parent_phone} onChange={handleChange} placeholder="0901..." />
          <Input label="Điện thoại cá nhân" name="phone" value={form.phone} onChange={handleChange} placeholder="0868..." />
          
          <div className={styles.inputGroup}>
            <label className={styles.label}>Người giới thiệu (Không bắt buộc)</label>
            <select name="referred_by" value={form.referred_by} onChange={handleChange} className={styles.select}>
              <option value="">-- Không có / Bỏ trống --</option>
              {students
                .filter(s => s.id !== editItem?.id)
                .map(s => (
                  <option key={s.id} value={s.id}>{s.full_name} ({s.student_code})</option>
                ))
              }
            </select>
          </div>

          <Input label="Ghi chú" name="notes" value={form.notes} onChange={handleChange} placeholder="Ghi chú..." className={styles.formFull} />
        </form>
      </Modal>
    </>
  );
};

export default Students;

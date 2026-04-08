import { useState, useEffect } from 'react';
import { Plus, Edit2 } from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../../components/ui/Card';
import Table from '../../../components/ui/Table';
import Badge from '../../../components/ui/Badge';
import Button from '../../../components/ui/Button';
import Modal from '../../../components/ui/Modal';
import Input from '../../../components/ui/Input';
import { adminService } from '../../../services/adminService';
import { formatCurrency } from '../../../utils/formatters';
import styles from '../Teachers/Teachers.module.css';

const initForm = { class_type: '', amount: '', description: '' };

const Settings = () => {
  const [rates,   setRates]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editItem,  setEditItem]  = useState(null);
  const [form,      setForm]      = useState(initForm);
  const [saving,    setSaving]    = useState(false);
  const [error,     setError]     = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const res = await adminService.getSalaryRates();
      setRates(res.data || []);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const openCreate = () => { setEditItem(null); setForm(initForm); setError(''); setModalOpen(true); };
  const openEdit = (r) => { setEditItem(r); setForm(r); setError(''); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setError(''); };
  const handleChange = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.class_type || !form.amount) { setError('Vui lòng điền đầy đủ'); return; }
    setSaving(true); setError('');
    try {
      if (editItem) await adminService.updateSalaryRate(editItem.id, { ...form, amount: +form.amount });
      else          await adminService.createSalaryRate({ ...form, amount: +form.amount });
      closeModal(); load();
    } catch (err) {
      setError(err.response?.data?.message || 'Đã xảy ra lỗi');
    } finally { setSaving(false); }
  };

  const columns = [
    { key: 'class_type',  title: 'Loại lớp / Khối', render: (v) => <strong>{v}</strong> },
    { key: 'amount',      title: 'Thù lao / buổi', render: (v) => <span style={{ color: 'var(--color-primary-dark)', fontWeight: 700 }}>{formatCurrency(v)}</span> },
    { key: 'description', title: 'Mô tả' },
    {
      key: 'is_active', title: 'Trạng thái',
      render: (v) => <Badge color={v ? 'present' : 'absent'}>{v ? 'Đang dùng' : 'Ẩn'}</Badge>
    },
    {
      key: 'id', title: 'Thao tác', width: '80px',
      render: (_, row) => <Button size="sm" variant="secondary" icon={<Edit2 size={13} />} onClick={() => openEdit(row)}>Sửa</Button>
    }
  ];

  return (
    <>
      <Card>
        <CardHeader
          title="Mệnh giá lương theo loại lớp"
          action={<Button icon={<Plus size={16} />} onClick={openCreate}>Thêm mệnh giá</Button>}
        />
        <CardBody noPadding>
          <Table columns={columns} data={loading ? [] : rates} emptyText={loading ? 'Đang tải...' : 'Chưa có mệnh giá nào'} />
        </CardBody>
      </Card>

      <Modal isOpen={modalOpen} onClose={closeModal} title={editItem ? 'Chỉnh sửa mệnh giá' : 'Thêm mệnh giá'} size="sm"
        footer={<><Button variant="secondary" onClick={closeModal}>Huỷ</Button><Button loading={saving} onClick={handleSave}>Lưu</Button></>}>
        {error && <div style={{ color: 'var(--color-absent)', marginBottom: '1rem', fontSize: '0.875rem' }}>{error}</div>}
        <form style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }} onSubmit={handleSave}>
          <Input label="Loại lớp / Khối" name="class_type" value={form.class_type} onChange={handleChange} placeholder="VD: Lớp 12, Tiếng Anh..." required />
          <Input label="Thù lao (VNĐ/buổi)" name="amount" type="number" value={form.amount} onChange={handleChange} placeholder="200000" required />
          <Input label="Mô tả" name="description" value={form.description} onChange={handleChange} placeholder="Ghi chú thêm..." />
        </form>
      </Modal>
    </>
  );
};

export default Settings;

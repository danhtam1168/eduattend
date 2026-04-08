import { useState, useEffect } from 'react';
import { FileText, Download } from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../../components/ui/Card';
import Table from '../../../components/ui/Table';
import Button from '../../../components/ui/Button';
import { adminService } from '../../../services/adminService';
import { formatCurrency, formatMonth, getCurrentMonth } from '../../../utils/formatters';
import styles from './SalaryReport.module.css';

const SalaryReport = () => {
  const [month,   setMonth]   = useState(getCurrentMonth());
  const [report,  setReport]  = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const res = await adminService.getSalaryReport(month);
      setReport(res.data);
    } catch { setReport(null); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [month]);

  const columns = [
    { key: 'employee_id',    title: 'Mã NV' },
    { key: 'full_name',      title: 'Họ và tên', render: (v) => <strong>{v}</strong> },
    { key: 'total_sessions', title: 'Số buổi', render: (v) => <span style={{ fontWeight: 600 }}>{v}</span> },
    { key: 'total_salary',   title: 'Tổng lương', render: (v) => <span style={{ color: 'var(--color-primary-dark)', fontWeight: 700 }}>{formatCurrency(v)}</span> },
  ];

  return (
    <div className={styles.page}>
      <div className={styles.toolbar}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <label style={{ fontSize: 'var(--font-size-sm)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Tháng:</label>
          <input type="month" value={month} onChange={e => setMonth(e.target.value)}
            style={{ padding: '0.45rem 0.875rem', border: '1.5px solid var(--color-border)', borderRadius: 'var(--radius-md)', fontSize: 'var(--font-size-sm)', fontFamily: 'var(--font-family)' }} />
        </div>
      </div>

      {/* Summary cards */}
      {report && (
        <div className={styles.summaryGrid}>
          <div className={styles.summaryCard}>
            <div className={styles.summaryLabel}>Giáo viên</div>
            <div className={styles.summaryValue}>{report.summary.total_teachers}</div>
          </div>
          <div className={styles.summaryCard}>
            <div className={styles.summaryLabel}>Tổng buổi dạy</div>
            <div className={styles.summaryValue}>{report.summary.total_sessions}</div>
          </div>
          <div className={styles.summaryCard} style={{ borderColor: 'var(--color-primary)' }}>
            <div className={styles.summaryLabel}>Tổng lương phải trả</div>
            <div className={styles.summaryValue} style={{ color: 'var(--color-primary-dark)' }}>
              {formatCurrency(report.summary.total_salary)}
            </div>
          </div>
        </div>
      )}

      <Card>
        <CardHeader title={`Bảng lương — ${formatMonth(month)}`} icon={<FileText size={16} />} />
        <CardBody noPadding>
          <Table
            columns={columns}
            data={loading ? [] : (report?.teachers || [])}
            emptyText={loading ? 'Đang tải...' : 'Không có dữ liệu cho tháng này'}
          />
        </CardBody>
      </Card>
    </div>
  );
};

export default SalaryReport;

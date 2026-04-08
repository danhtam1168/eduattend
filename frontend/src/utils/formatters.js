import { SHIFTS } from './constants';

export const formatDate = (dateStr) => {
  if (!dateStr) return '---';
  const d = new Date(dateStr);
  return d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
};

export const formatDateShort = (dateStr) => {
  if (!dateStr) return '---';
  const d = new Date(dateStr);
  return d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
};

export const formatDatetime = (dateStr) => {
  if (!dateStr) return '---';
  const d = new Date(dateStr);
  return d.toLocaleString('vi-VN');
};

export const formatCurrency = (amount) => {
  if (amount === null || amount === undefined) return '---';
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  }).format(amount);
};

export const formatShift = (shift) => SHIFTS[shift] || shift;

export const formatMonth = (monthStr) => {
  if (!monthStr) return '';
  const [year, month] = monthStr.split('-');
  return `Tháng ${parseInt(month)}/${year}`;
};

export const getCurrentMonth = () => {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  return `${y}-${m}`;
};

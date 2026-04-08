import clsx from 'clsx';
import styles from './Button.module.css';

const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  onClick,
  type = 'button',
  className = '',
  icon,
}) => {
  return (
    <button
      type={type}
      className={clsx(
        styles.btn,
        styles[size],
        styles[variant],
        loading && styles.loading,
        className
      )}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading ? (
        <span style={{ display: 'inline-block', width: 14, height: 14, border: '2px solid currentColor', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.6s linear infinite' }} />
      ) : icon}
      {children}
    </button>
  );
};

export default Button;

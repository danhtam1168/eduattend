import clsx from 'clsx';
import styles from './Badge.module.css';

const Badge = ({ children, color = 'pending', showDot = true }) => {
  return (
    <span className={clsx(styles.badge, styles[color])}>
      {showDot && <span className={styles.dot} />}
      {children}
    </span>
  );
};

export default Badge;

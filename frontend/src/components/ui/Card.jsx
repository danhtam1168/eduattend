import clsx from 'clsx';
import styles from './Card.module.css';

export const Card = ({ children, className = '' }) => (
  <div className={clsx(styles.card, className)}>{children}</div>
);

export const CardHeader = ({ title, action, icon }) => (
  <div className={styles.cardHeader}>
    <div className={styles.cardTitle}>
      <span className={styles.accent} />
      {icon && icon}
      {title}
    </div>
    {action && <div>{action}</div>}
  </div>
);

export const CardBody = ({ children, noPadding = false, className = '' }) => (
  <div className={clsx(styles.cardBody, noPadding && styles.noPadding, className)}>
    {children}
  </div>
);

export const CardFooter = ({ children }) => (
  <div className={styles.cardFooter}>{children}</div>
);

export default Card;

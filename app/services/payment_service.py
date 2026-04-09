from datetime import date
from app.extensions import db
from app.models.payment import Payment
from app.models.monthly_fee import MonthlyFee

class PaymentService:
    @staticmethod
    def get_payments(student_id, status, from_date, to_date):
        query = Payment.query
        if student_id:
            query = query.filter_by(student_id=int(student_id))
        if status:
            query = query.filter_by(status=status)
        if from_date:
            query = query.filter(Payment.payment_date >= date.fromisoformat(from_date))
        if to_date:
            query = query.filter(Payment.payment_date <= date.fromisoformat(to_date))

        return query.order_by(Payment.payment_date.desc()).all()

    @staticmethod
    def create_payment(data, admin_id):
        valid_methods = ['cash', 'bank_transfer', 'online_payment']
        if data['payment_method'] not in valid_methods:
            raise ValueError(f"Phương thức thanh toán phải là: {', '.join(valid_methods)}")

        payment = Payment(
            student_id=int(data['student_id']),
            fee_id=data.get('fee_id'),
            amount=float(data['amount']),
            payment_method=data['payment_method'],
            transaction_ref=data.get('transaction_ref', ''),
            status='completed',
            notes=data.get('notes', ''),
            received_by=admin_id,
        )
        db.session.add(payment)

        if data.get('fee_id'):
            fee = MonthlyFee.query.get(int(data['fee_id']))
            if fee:
                fee.status = 'paid'

        db.session.commit()
        return payment

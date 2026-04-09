from datetime import date
from flask import Blueprint, request
from app.extensions import db
from app.models.payment import Payment
from app.models.monthly_fee import MonthlyFee
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required, get_current_admin
from app.utils.validators import validate_required

payments_bp = Blueprint('admin_payments', __name__)


@payments_bp.route('', methods=['GET'])
@admin_required
def get_payments():
    student_id = request.args.get('student_id')
    status = request.args.get('status')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    query = Payment.query
    if student_id:
        query = query.filter_by(student_id=int(student_id))
    if status:
        query = query.filter_by(status=status)
    if from_date:
        query = query.filter(Payment.payment_date >= date.fromisoformat(from_date))
    if to_date:
        query = query.filter(Payment.payment_date <= date.fromisoformat(to_date))

    payments = query.order_by(Payment.payment_date.desc()).all()
    return success_response([p.to_dict() for p in payments])


@payments_bp.route('', methods=['POST'])
@admin_required
def create_payment():
    data = request.get_json()
    errors = validate_required(data, ['student_id', 'amount', 'payment_method'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    valid_methods = ['cash', 'bank_transfer', 'online_payment']
    if data['payment_method'] not in valid_methods:
        return error_response(f"Phương thức thanh toán phải là: {', '.join(valid_methods)}", 400)

    admin = get_current_admin()
    payment = Payment(
        student_id=int(data['student_id']),
        fee_id=data.get('fee_id'),
        amount=float(data['amount']),
        payment_method=data['payment_method'],
        transaction_ref=data.get('transaction_ref', ''),
        status='completed',
        notes=data.get('notes', ''),
        received_by=admin.id if admin else None,
    )
    db.session.add(payment)

    # Cập nhật trạng thái monthly_fee nếu có
    if data.get('fee_id'):
        fee = MonthlyFee.query.get(int(data['fee_id']))
        if fee:
            fee.status = 'paid'

    db.session.commit()
    return success_response(payment.to_dict(), "Ghi nhận thanh toán thành công", 201)

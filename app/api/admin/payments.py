from flask import Blueprint, request
from app.services.payment_service import PaymentService
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required, get_current_admin
from app.utils.validators import validate_required

payments_bp = Blueprint('admin_payments', __name__)

@payments_bp.route('', methods=['GET'])
@admin_required
def get_payments():
    try:
        student_id = request.args.get('student_id')
        status = request.args.get('status')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        payments = PaymentService.get_payments(student_id, status, from_date, to_date)
        return success_response([p.to_dict() for p in payments])
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@payments_bp.route('', methods=['POST'])
@admin_required
def create_payment():
    data = request.get_json()
    errors = validate_required(data, ['student_id', 'amount', 'payment_method'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    from app.extensions import db
    try:
        admin = get_current_admin()
        payment = PaymentService.create_payment(data, admin.id if admin else None)
        return success_response(payment.to_dict(), "Ghi nhận thanh toán thành công", 201)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

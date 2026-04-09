from flask import Blueprint, request
from app.services.monthly_fee_service import MonthlyFeeService
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required

monthly_fees_bp = Blueprint('admin_monthly_fees', __name__)

@monthly_fees_bp.route('', methods=['GET'])
@admin_required
def get_monthly_fees():
    try:
        month_year = request.args.get('month_year')
        student_id = request.args.get('student_id')
        class_id = request.args.get('class_id')
        status = request.args.get('status')

        fees = MonthlyFeeService.get_monthly_fees(month_year, student_id, class_id, status)
        return success_response([f.to_dict() for f in fees])
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@monthly_fees_bp.route('/generate', methods=['POST'])
@admin_required
def generate_monthly_fees():
    data = request.get_json() or {}
    month_year = data.get('month_year')
    from app.extensions import db
    try:
        created, updated = MonthlyFeeService.generate_monthly_fees(month_year)
        return success_response({
            "month_year": month_year,
            "created": created,
            "updated": updated,
        }, "Tính học phí thành công")
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@monthly_fees_bp.route('/<int:fee_id>/confirm', methods=['PUT'])
@admin_required
def confirm_fee(fee_id):
    from app.extensions import db
    try:
        fee = MonthlyFeeService.confirm_fee(fee_id)
        return success_response(fee.to_dict(), "Đã xác nhận hoá đơn học phí")
    except ValueError as e:
        if "không tồn tại" in str(e).lower():
            return error_response(str(e), 404)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@monthly_fees_bp.route('/<int:fee_id>', methods=['GET'])
@admin_required
def get_fee(fee_id):
    try:
        fee = MonthlyFeeService.get_fee(fee_id)
        return success_response(fee.to_dict())
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

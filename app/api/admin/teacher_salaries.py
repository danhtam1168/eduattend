from flask import Blueprint, request
from app.services.salary_service import SalaryService
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required, get_current_admin

teacher_salaries_bp = Blueprint('admin_teacher_salaries', __name__)

@teacher_salaries_bp.route('', methods=['GET'])
@admin_required
def get_salaries():
    try:
        month_year = request.args.get('month_year')
        status = request.args.get('status')

        salaries = SalaryService.get_salaries(month_year, status)
        return success_response([s.to_dict() for s in salaries])
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teacher_salaries_bp.route('/generate', methods=['POST'])
@admin_required
def generate_salaries():
    """Tính lương tháng dựa trên teacher_attendances"""
    data = request.get_json() or {}
    month_year = data.get('month_year')
    from app.extensions import db
    try:
        created, updated = SalaryService.generate_salaries(month_year)
        return success_response({"created": created, "updated": updated}, "Tính lương thành công")
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teacher_salaries_bp.route('/<int:salary_id>', methods=['PUT'])
@admin_required
def update_salary(salary_id):
    data = request.get_json()
    from app.extensions import db
    try:
        salary = SalaryService.update_salary(salary_id, data)
        return success_response(salary.to_dict(), "Cập nhật thành công")
    except ValueError as e:
        if "không tồn tại" in str(e).lower():
            return error_response(str(e), 404)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teacher_salaries_bp.route('/<int:salary_id>/approve', methods=['PUT'])
@admin_required
def approve_salary(salary_id):
    from app.extensions import db
    try:
        admin = get_current_admin()
        salary = SalaryService.approve_salary(salary_id, admin.id)
        return success_response(salary.to_dict(), "Đã phê duyệt bảng lương")
    except ValueError as e:
        if "không tồn tại" in str(e).lower():
            return error_response(str(e), 404)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teacher_salaries_bp.route('/<int:salary_id>/pay', methods=['PUT'])
@admin_required
def pay_salary(salary_id):
    from app.extensions import db
    try:
        admin = get_current_admin()
        salary = SalaryService.pay_salary(salary_id, admin.id)
        return success_response(salary.to_dict(), "Đã ghi nhận thanh toán lương")
    except ValueError as e:
        if "không tồn tại" in str(e).lower():
            return error_response(str(e), 404)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

from flask import Blueprint
from app.services.dashboard_service import DashboardService
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required

dashboard_bp = Blueprint('admin_dashboard', __name__)

@dashboard_bp.route('', methods=['GET'])
@admin_required
def get_dashboard():
    try:
        stats = DashboardService.get_dashboard_stats()
        return success_response(stats)
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

from datetime import datetime

VALID_SHIFTS = ('morning', 'afternoon', 'evening')


def validate_required(data: dict, fields: list) -> dict:
    """Kiểm tra các field bắt buộc, trả về dict lỗi"""
    errors = {}
    for field in fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors[field] = f"'{field}' không được để trống"
    return errors


def validate_date_format(date_str: str) -> bool:
    """Kiểm tra format YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False


def validate_month_format(month_str: str) -> bool:
    """Kiểm tra format YYYY-MM"""
    try:
        datetime.strptime(month_str, '%Y-%m')
        return True
    except (ValueError, TypeError):
        return False


def validate_shift(shift: str) -> bool:
    """Kiểm tra ca dạy hợp lệ"""
    return shift in VALID_SHIFTS

from flask import jsonify


def success_response(data=None, message="Thành công", status_code=200):
    return jsonify({
        "success": True,
        "message": message,
        "data":    data
    }), status_code


def error_response(message="Có lỗi xảy ra", status_code=400, errors=None):
    body = {
        "success": False,
        "message": message,
        "data":    None
    }
    if errors:
        body["errors"] = errors  # Chi tiết lỗi validation
    return jsonify(body), status_code


def paginated_response(items, total, page, per_page):
    return success_response({
        "items": items,
        "pagination": {
            "total":    total,
            "page":     page,
            "per_page": per_page,
            "pages":    (total + per_page - 1) // per_page
        }
    })

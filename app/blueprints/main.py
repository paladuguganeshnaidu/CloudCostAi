import os
import hmac
from functools import wraps
from base64 import b64decode

from flask import Blueprint, Response, flash, redirect, render_template, request, url_for, current_app

from app.services import (
    delete_prediction,
    generate_csv,
    get_dashboard_stats,
    get_prediction_history,
    perform_prediction,
    sanitize_form_data,
)

main_bp = Blueprint("main", __name__)


def _check_auth_header(auth_header: str) -> bool:
    try:
        if not auth_header.lower().startswith("basic "):
            return False
        payload = b64decode(auth_header.split(" ", 1)[1]).decode("utf-8")
        username, password = payload.split(":", 1)
        expected_user = os.environ.get("ADMIN_USER")
        expected_pass = os.environ.get("ADMIN_PASS")
        if not expected_user or not expected_pass:
            return False
        return hmac.compare_digest(username, expected_user) and hmac.compare_digest(password, expected_pass)
    except Exception:
        return False


def require_basic_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # If admin not enabled, deny
        if not current_app.config.get("SHOW_ADMIN"):
            return Response("Not Found", status=404)
        auth = request.headers.get("Authorization", "")
        if _check_auth_header(auth):
            return func(*args, **kwargs)
        # Request auth
        resp = Response("Unauthorized", status=401)
        resp.headers["WWW-Authenticate"] = 'Basic realm="CloudCostAI Admin"'
        return resp
    return wrapper


@main_bp.route("/")
def index():
    history = get_prediction_history(limit=5)
    return render_template("index.html", history=history, prediction_result=None, values={}, errors=[])


@main_bp.route("/predict", methods=["POST"])
def predict():
    errors, values = sanitize_form_data(request.form)
    if errors:
        for error in errors:
            flash(error, "danger")
        history = get_prediction_history(limit=5)
        return render_template(
            "index.html",
            history=history,
            prediction_result=None,
            values=values,
            errors=errors,
        )

    try:
        predicted_cost, _ = perform_prediction(values)
        flash("Prediction completed successfully.", "success")
        history = get_prediction_history(limit=5)
        return render_template(
            "index.html",
            history=history,
            prediction_result=predicted_cost,
            values=values,
            errors=[],
        )
    except Exception as exc:
        flash(f"Prediction failed: {exc}", "danger")
        history = get_prediction_history(limit=5)
        return render_template(
            "index.html",
            history=history,
            prediction_result=None,
            values=values,
            errors=[str(exc)],
        )


@main_bp.route("/history")
def history():
    search = request.args.get("q", "", type=str)
    rows = get_prediction_history(search=search)
    return {"predictions": [dict(row) for row in rows]}


@main_bp.route("/admin")
@require_basic_auth
def admin():
    search = request.args.get("q", "", type=str)
    stats = get_dashboard_stats(search=search)
    history_rows = get_prediction_history(search=search)
    return render_template("admin.html", stats=stats, history=history_rows, search=search)


@main_bp.route("/admin/delete/<int:prediction_id>", methods=["POST"])
@require_basic_auth
def delete_prediction_route(prediction_id: int):
    delete_prediction(prediction_id)
    flash("Prediction deleted successfully.", "success")
    return redirect(url_for("main.admin"))


@main_bp.route("/api/delete/<int:prediction_id>", methods=["DELETE"])
@require_basic_auth
def api_delete_prediction(prediction_id: int):
    try:
        delete_prediction(prediction_id)
        return {"status": "ok", "message": "deleted"}, 200
    except Exception as exc:
        return {"status": "error", "message": str(exc)}, 500


@main_bp.route("/download")
@require_basic_auth
def download():
    search = request.args.get("q", "", type=str)
    rows = get_prediction_history(search=search)
    content = generate_csv(rows)
    response = Response(content, mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=cloudcostai_predictions.csv"
    return response


@main_bp.route("/api/stats")
@require_basic_auth
def api_stats():
    search = request.args.get("q", "", type=str)
    stats = get_dashboard_stats(search=search)
    return stats

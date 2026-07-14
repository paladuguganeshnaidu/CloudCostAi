from flask import Blueprint, Response, flash, redirect, render_template, request, url_for

from app.services import (
    delete_prediction,
    generate_csv,
    get_dashboard_stats,
    get_prediction_history,
    perform_prediction,
    sanitize_form_data,
)

main_bp = Blueprint("main", __name__)


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
def admin():
    search = request.args.get("q", "", type=str)
    stats = get_dashboard_stats(search=search)
    history_rows = get_prediction_history(search=search)
    return render_template("admin.html", stats=stats, history=history_rows, search=search)


@main_bp.route("/admin/delete/<int:prediction_id>", methods=["POST"])
def delete_prediction_route(prediction_id: int):
    delete_prediction(prediction_id)
    flash("Prediction deleted successfully.", "success")
    return redirect(url_for("main.admin"))


@main_bp.route("/api/delete/<int:prediction_id>", methods=["DELETE"])
def api_delete_prediction(prediction_id: int):
    try:
        delete_prediction(prediction_id)
        return {"status": "ok", "message": "deleted"}, 200
    except Exception as exc:
        return {"status": "error", "message": str(exc)}, 500


@main_bp.route("/download")
def download():
    search = request.args.get("q", "", type=str)
    rows = get_prediction_history(search=search)
    content = generate_csv(rows)
    response = Response(content, mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=cloudcostai_predictions.csv"
    return response


@main_bp.route("/api/stats")
def api_stats():
    search = request.args.get("q", "", type=str)
    stats = get_dashboard_stats(search=search)
    return stats

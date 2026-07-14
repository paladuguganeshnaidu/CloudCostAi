import csv
import os
import sqlite3
import sys
from datetime import datetime
from io import StringIO
from pathlib import Path

import pandas as pd
from flask import (
    Flask,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.model.predict import predict_cost

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cloudcostai-secret-key")
app.config["DATABASE"] = Path(
    os.environ.get("DATABASE_PATH", str(PROJECT_ROOT / "cloudcostai.db"))
)


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            service_name TEXT NOT NULL,
            usage_quantity REAL NOT NULL,
            usage_unit TEXT NOT NULL,
            region TEXT NOT NULL,
            cpu REAL NOT NULL,
            memory REAL NOT NULL,
            network_in REAL NOT NULL,
            network_out REAL NOT NULL,
            usage_start TEXT NOT NULL,
            usage_end TEXT NOT NULL,
            cost_per_quantity REAL NOT NULL,
            predicted_cost REAL NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


def sanitize_form_data(form_data: dict) -> tuple[list[str], dict]:
    errors = []
    values = {
        "service_name": (form_data.get("service_name") or "").strip(),
        "usage_quantity": (form_data.get("usage_quantity") or "").strip(),
        "usage_unit": (form_data.get("usage_unit") or "").strip(),
        "region": (form_data.get("region") or "").strip(),
        "cpu": (form_data.get("cpu") or "").strip(),
        "memory": (form_data.get("memory") or "").strip(),
        "network_in": (form_data.get("network_in") or "").strip(),
        "network_out": (form_data.get("network_out") or "").strip(),
        "usage_start": (form_data.get("usage_start") or "").strip(),
        "usage_end": (form_data.get("usage_end") or "").strip(),
        "cost_per_quantity": (form_data.get("cost_per_quantity") or "").strip(),
    }

    if not values["service_name"]:
        errors.append("Service Name is required.")
    if not values["usage_unit"]:
        errors.append("Usage Unit is required.")
    if not values["region"]:
        errors.append("Region is required.")

    numeric_fields = [
        ("usage_quantity", "Usage Quantity"),
        ("cpu", "CPU Utilization"),
        ("memory", "Memory Utilization"),
        ("network_in", "Network Inbound Data"),
        ("network_out", "Network Outbound Data"),
        ("cost_per_quantity", "Cost per Quantity"),
    ]

    for field_name, label in numeric_fields:
        try:
            values[field_name] = float(values[field_name])
        except (TypeError, ValueError):
            errors.append(f"{label} must be a valid number.")

    if values.get("usage_start") and values.get("usage_end"):
        try:
            start_date = pd.to_datetime(values["usage_start"])
            end_date = pd.to_datetime(values["usage_end"])
            if start_date > end_date:
                errors.append("Usage Start Date cannot be later than Usage End Date.")
            values["usage_start"] = start_date.strftime("%Y-%m-%d")
            values["usage_end"] = end_date.strftime("%Y-%m-%d")
        except Exception:
            errors.append("Usage dates must be valid dates.")

    return errors, values


def build_input_dataframe(values: dict) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Resource ID": f"temp-{datetime.utcnow().timestamp()}",
                "Service Name": values["service_name"],
                "Usage Quantity": values["usage_quantity"],
                "Usage Unit": values["usage_unit"],
                "Region/Zone": values["region"],
                "CPU Utilization (%)": values["cpu"],
                "Memory Utilization (%)": values["memory"],
                "Network Inbound Data (Bytes)": values["network_in"],
                "Network Outbound Data (Bytes)": values["network_out"],
                "Usage Start Date": pd.to_datetime(values["usage_start"]),
                "Usage End Date": pd.to_datetime(values["usage_end"]),
                "Cost per Quantity ($)": values["cost_per_quantity"],
                "Total Cost (INR)": 0.0,
            }
        ]
    )


def save_prediction(values: dict, predicted_cost: float) -> None:
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO prediction_history (
            timestamp, service_name, usage_quantity, usage_unit, region, cpu,
            memory, network_in, network_out, usage_start, usage_end,
            cost_per_quantity, predicted_cost
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            values["service_name"],
            values["usage_quantity"],
            values["usage_unit"],
            values["region"],
            values["cpu"],
            values["memory"],
            values["network_in"],
            values["network_out"],
            values["usage_start"],
            values["usage_end"],
            values["cost_per_quantity"],
            predicted_cost,
        ),
    )
    conn.commit()
    conn.close()


def get_prediction_history(limit: int | None = None, search: str | None = None):
    conn = get_db_connection()
    query = "SELECT * FROM prediction_history"
    params = []
    if search:
        query += " WHERE lower(service_name) LIKE ? OR lower(region) LIKE ?"
        search_term = f"%{search.lower()}%"
        params.extend([search_term, search_term])
    query += " ORDER BY id DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_dashboard_stats(search: str | None = None) -> dict:
    rows = get_prediction_history(search=search)
    if not rows:
        return {
            "total_predictions": 0,
            "latest_prediction": None,
            "predictions_per_day": {"labels": [], "values": []},
            "average_predicted_cost": 0.0,
            "top_services": {"labels": [], "values": []},
            "top_regions": {"labels": [], "values": []},
        }

    latest_prediction = rows[0]
    daily_counts = {}
    service_counts = {}
    region_counts = {}
    total_cost = 0.0

    for row in rows:
        day = row["timestamp"][:10]
        daily_counts[day] = daily_counts.get(day, 0) + 1
        service_counts[row["service_name"]] = service_counts.get(row["service_name"], 0) + 1
        region_counts[row["region"]] = region_counts.get(row["region"], 0) + 1
        total_cost += row["predicted_cost"]

    return {
        "total_predictions": len(rows),
        "latest_prediction": dict(latest_prediction),
        "predictions_per_day": {
            "labels": list(daily_counts.keys()),
            "values": list(daily_counts.values()),
        },
        "average_predicted_cost": round(total_cost / len(rows), 2),
        "top_services": {
            "labels": list(service_counts.keys()),
            "values": list(service_counts.values()),
        },
        "top_regions": {
            "labels": list(region_counts.keys()),
            "values": list(region_counts.values()),
        },
    }


@app.route("/")
def index():
    history = get_prediction_history(limit=5)
    return render_template("index.html", history=history, prediction_result=None, values={}, errors=[])


@app.route("/predict", methods=["POST"])
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
        input_df = build_input_dataframe(values)
        prediction = predict_cost(input_df)
        predicted_cost = round(float(prediction[0]), 2)
        save_prediction(values, predicted_cost)
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


@app.route("/history")
def history():
    search = request.args.get("q", "", type=str)
    rows = get_prediction_history(search=search)
    return jsonify({"predictions": [dict(row) for row in rows]})


@app.route("/admin")
def admin():
    search = request.args.get("q", "", type=str)
    stats = get_dashboard_stats(search=search)
    history_rows = get_prediction_history(search=search)
    return render_template("admin.html", stats=stats, history=history_rows, search=search)


@app.route("/admin/delete/<int:prediction_id>", methods=["POST"])
def delete_prediction(prediction_id: int):
    conn = get_db_connection()
    conn.execute("DELETE FROM prediction_history WHERE id = ?", (prediction_id,))
    conn.commit()
    conn.close()
    flash("Prediction deleted successfully.", "success")
    return redirect(url_for("admin"))


@app.route("/download")
def download():
    search = request.args.get("q", "", type=str)
    rows = get_prediction_history(search=search)
    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "id",
            "timestamp",
            "service_name",
            "usage_quantity",
            "usage_unit",
            "region",
            "cpu",
            "memory",
            "network_in",
            "network_out",
            "usage_start",
            "usage_end",
            "cost_per_quantity",
            "predicted_cost",
        ],
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(dict(row))

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=cloudcostai_predictions.csv"
    return response


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
    )

from __future__ import annotations

import csv
from datetime import datetime
from io import StringIO
from typing import Any

import pandas as pd
from flask import Response

from src.data.feature_engineering import create_features
from src.model.predict import predict_cost
from app.database import get_db_connection


def sanitize_form_data(form_data: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
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
        except Exception as exc:
            errors.append(f"Usage dates must be valid dates. {exc}")

    return errors, values


def build_input_dataframe(values: dict[str, Any]) -> pd.DataFrame:
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


def save_prediction(values: dict[str, Any], predicted_cost: float) -> None:
    connection = get_db_connection()
    connection.execute(
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
    connection.commit()
    connection.close()


def get_prediction_history(limit: int | None = None, search: str | None = None) -> list[dict[str, Any]]:
    connection = get_db_connection()
    query = "SELECT * FROM prediction_history"
    params: list[Any] = []
    if search:
        query += " WHERE lower(service_name) LIKE ? OR lower(region) LIKE ?"
        search_term = f"%{search.lower()}%"
        params.extend([search_term, search_term])
    query += " ORDER BY id DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    rows = connection.execute(query, params).fetchall()
    connection.close()
    return [dict(row) for row in rows]


def get_dashboard_stats(search: str | None = None) -> dict[str, Any]:
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
    daily_counts: dict[str, int] = {}
    service_counts: dict[str, int] = {}
    region_counts: dict[str, int] = {}
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


def delete_prediction(prediction_id: int) -> None:
    connection = get_db_connection()
    connection.execute("DELETE FROM prediction_history WHERE id = ?", (prediction_id,))
    connection.commit()
    connection.close()


def generate_csv(rows: list[dict[str, Any]]) -> str:
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
    return output.getvalue()


def perform_prediction(values: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    dataframe = build_input_dataframe(values)
    engineered_frame = create_features(dataframe)
    prediction = predict_cost(engineered_frame)
    predicted_cost = round(float(prediction[0]), 2)
    save_prediction(values, predicted_cost)
    return predicted_cost, {"input_frame": engineered_frame}

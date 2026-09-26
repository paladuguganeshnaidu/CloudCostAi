# CloudCostAI

CloudCostAI is a Flask web application for **cloud-cost prediction**. The repository contains a saved machine-learning inference pipeline, a dashboard, prediction history storage and deployment configuration for a Python web service.

## Features

- Cloud-cost prediction form.
- Prediction result view.
- SQLite prediction history.
- Admin dashboard.
- Chart.js visualizations.
- CSV export of prediction history.
- Render deployment configuration.
- Saved model/preprocessor artifacts under `models/`.

## Technology stack

- Python
- Flask 3.0.x
- pandas
- NumPy
- scikit-learn
- joblib
- Gunicorn
- gevent
- python-dotenv
- Whitenoise

The exact pinned dependencies are listed in `requirements.txt`.

## Repository structure

```text
app/
  app.py
  templates/
    index.html
    admin.html
  static/
    css/
    js/
models/
  linear_regression.pkl
  preprocessor.pkl
  feature_names.pkl
data/
outputs/
logs/
reports/
src/
tests/
requirements.txt
render.yaml
runtime.txt
Procfile
README.md
```

## Local setup

Prerequisite: Python 3.10 or newer.

Create an environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the application:

```bash
python app/app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Configuration

The application supports environment-based configuration including:

- `SECRET_KEY`
- `DATABASE_PATH`
- Flask/Render `PORT`

Create a local `.env` from `.env.example` where appropriate.

Never commit production secrets.

## Render

The repository contains:

- `render.yaml`
- `Procfile`
- `runtime.txt`

The documented application entry point is:

```text
app.app:app
```

Gunicorn is used for service startup.

Before production deployment, verify the Render Python runtime against the current `runtime.txt` rather than relying on an older README value.

## Data storage

Prediction history currently uses SQLite.

SQLite is suitable for the current lightweight application, but concurrent production workloads and durable managed hosting require a deliberate storage strategy. A managed PostgreSQL/MySQL database is a natural next step for multi-instance or higher-volume deployment.

## Model artifacts

The application expects the saved artifacts under `models/`:

- `linear_regression.pkl`
- `preprocessor.pkl`
- `feature_names.pkl`

Do not load untrusted pickle/joblib files in a security-sensitive environment; serialized Python model artifacts can execute code when deserialized.

## Testing

A `tests/` directory is present. Run the available test suite with:

```bash
python -m pytest -q
```

Do not treat the presence of a test directory as proof of a particular coverage percentage or performance level. Record measured results separately when benchmarking.

## Performance

The repository does not provide a verified P95/P99 latency, throughput, concurrency or availability benchmark. Those values should be measured on the target deployment environment before being used in a report or production SLO.

## Security

Current implementation considerations include:

- Keep `SECRET_KEY` outside source control.
- Validate user inputs before model inference.
- Avoid exposing raw exception details in production.
- Restrict admin functionality.
- Treat model artifacts and prediction history as application data.
- Move from SQLite to a managed database for multi-instance deployments.

## Limitations

- The project depends on a pre-trained/saved regression pipeline.
- The README does not claim that the model is universally accurate for every cloud provider or billing schema.
- Model quality depends on the training data and feature pipeline stored with the project.
- SQLite limits horizontal scaling and concurrent writes.

## License

This repository contains an MIT License. See [LICENSE](LICENSE).

## Author

Paladugu Ganesh Naidu

Repository: https://github.com/paladuguganeshnaidu/CloudCostAi

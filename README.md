# CloudCostAI

## Project Description

CloudCostAI is a Flask-based web application for AI-powered cloud cost prediction. The project uses an existing machine learning inference pipeline with a saved model, preprocessor, and feature pipeline in `models/` and serves predictions through a modern Bootstrap dashboard.

## Features

- Dark glassmorphism UI
- Cloud cost prediction form
- Prediction result card
- SQLite prediction history
- Admin dashboard with charts
- Chart.js visualizations for predictions per day, top services, and regions
- CSV download of history
- Render-compatible deployment configuration

## Deployment Files

- `render.yaml`
- `Procfile`
- `runtime.txt`
- `requirements.txt`
- `.gitignore`
- `README.md`

## Installation

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/CloudCostAI.git
cd CloudCostAI
```

2. Create a Python virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Local Run

1. Start the Flask app locally:

```bash
python app/app.py
```

2. Open your browser at:

```text
http://127.0.0.1:5000
```

## Render Free Tier Deployment

### Prerequisites

- GitHub account
- Render account
- Repository pushed to GitHub

### Render Setup

1. Ensure the repository is pushed to the `main` branch.
2. On Render, create a new **Web Service**.
3. Connect your GitHub repository.
4. Set the branch to `main`.

### Build and Start Commands

- **Build Command:**

```bash
pip install -r requirements.txt
```

- **Start Command:**

```bash
gunicorn "app.app:app" --worker-class gevent --workers 2 --threads 4 --timeout 120
```

### Runtime

The project uses:

```text
python-3.13.5
```

from `runtime.txt`.

### Environment Variables

Render should provide:

- `SECRET_KEY` — set a secure random string
- `DATABASE_PATH` — optional, default is `cloudcostai.db`

You can create a local `.env` file from `.env.example` for development:

```text
cp .env.example .env
# then edit .env and set SECRET_KEY
```

The app reads environment variables at startup. Do NOT commit a production `SECRET_KEY` to version control.

### Render YAML

The repo includes `render.yaml` with the service configuration for Render Free Tier:

- `type: web`
- `plan: free`
- `env: python`
- `region: oregon`
- `buildCommand: pip install -r requirements.txt`
- `startCommand: gunicorn "app.app:app" --worker-class gevent --workers 2 --threads 4 --timeout 120`

## Production Configuration

- App startup is handled in `app/app.py` using:

```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
```

- Gunicorn is used for deployment, not `flask run`.
- The SQLite database is created automatically if missing.
- The app uses `pathlib.Path` for file resolution.

## Project Structure

```text
app/
  app.py
  templates/
    index.html
    admin.html
  static/
    css/
      style.css
    js/
      script.js
models/
  linear_regression.pkl
  preprocessor.pkl
  feature_names.pkl
data/
outputs/
logs/
reports/
src/
  data/
  model/
tests/
requirements.txt
render.yaml
runtime.txt
Procfile
README.md
.gitignore
```

## Notes on Render and SQLite

- Render Free Tier instances can persist app data, but SQLite is not ideal for large-scale production storage.
- Use SQLite for lightweight history on the free tier.
- If you need persistence beyond current instance lifetime, migrate to PostgreSQL or MySQL.

## Common Deployment Errors

- `ModuleNotFoundError`: ensure the app is started with `gunicorn "app.app:app"`.
- `ImportError`: ensure `src/` is included in Python path via `app/app.py` and `render.yaml` points to the correct app path.
- `Database locked`: avoid concurrent writes during heavy load; SQLite is best for light traffic.

## Troubleshooting

- Check Render build logs for dependency installation errors.
- Confirm `runtime.txt` uses `python-3.13.0`.
- Verify `Procfile` start command is correct.
- Use `DATABASE_PATH` environment variable if the default path needs adjustment.

## License

This project is licensed under the MIT License.

## GitHub Readiness

- CI workflow: `.github/workflows/ci.yml` runs tests on push and PRs to `main`.
- Line endings are normalized with `.gitattributes`.
- Ensure `SECRET_KEY` is set in your Render or GitHub Actions secrets — do not commit secrets.
- Use `.env.example` as a template for local development.
- Before opening a PR, run:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python -m pytest -q
```

If you want me to also create a LICENSE or GitHub issue/PR templates, say so and I will add them.


# Weather Data — Overview

This repository contains a multi-iteration Weather Data application (final iteration in `Iteration 11 - Final`).
The app collects, stores, visualizes and forecasts weather data for many Australian stations. Below is a concise feature list, quick-start instructions, and screenshots from the final iteration.

## Key features

- Data insertion: upload CSV station data via a simple web interface
- Data management: browse and manage stored records 
- Summary & statistics: generate aggregated summaries and daily statistics 
- Visualizer: interactive charts to explore historical weather variables.
- Forecaster: multivariate time-series forecasting per station using trained models
- REST endpoints and database: small SQLite-backed web app for storing/retrieving data
- Tests: unit tests and small test dataset for validation

## Screenshots

Home / Dashboard

![Home page](Iteration%2011%20-%20Final/Screenshots/Home%20page.png)

Data insertion

![Data Inserter](Iteration%2011%20-%20Final/Screenshots/Data%20Inserter.png)

Data management

![Data Management](Iteration%2011%20-%20Final/Screenshots/Data%20Management.png)

Summary view

![Data Summary](Iteration%2011%20-%20Final/Screenshots/Data%20Summary.png)

Visualizer

![Visualizer](Iteration%2011%20-%20Final/Screenshots/Visualizer.png)

Forecaster

![Forecaster](Iteration%2011%20-%20Final/Screenshots/Forecaster.png)

## How the forecasting works (brief)

- Models are multivariate forecasters trained per station and stored under `Iteration 11 - Final/models`.
- The `model.py` and `multivariate_forecaster.py` (in `models/`) contain training and prediction logic. The web UI calls `model.py` to run forecasts for the selected station and horizon.

## Tests and data

- Example datasets are in `Iteration 11 - Final/Data/` (training and test CSVs). The test suite `Iteration 11 - Final/weather_data_test.py` contains unit tests for the core data utilities.

## Project structure (high level)

- `Iteration 11 - Final/` — final web application iteration (primary target for running the app)
	- `app.py` — Flask web app entrypoint
	- `database.py` — database helpers
	- `model.py` — model training / loading utilities
	- `weather_data.py` — data ingestion and processing
	- `models/` — saved forecasting model artifacts (joblib)
	- `Data/` — CSV datasets used for training and testing
	- `templates/` and `static/` — front-end UI files

Other iterations (1–10) live in sibling folders and document the project's history and experimentation.

## Quick start (run the final web app)

1. Open a terminal and change into the final iteration folder:

```
cd "Iteration 11 - Final"
```

2. Install Python dependencies (prefer a virtual environment):

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the app (development):

```
python app.py
```

4. Open your browser at http://127.0.0.1:5000/ (or the port printed by the app).

Notes: the app is a small Flask application. If your platform uses a different command to run Flask directly (for example `flask run`), use it after setting the `FLASK_APP` environment variable.


## Where to look first

- Open `Iteration 11 - Final/app.py` to see how routes map to templates.
- Check `Iteration 11 - Final/weather_data.py` for data ingest and cleaning logic.
- Inspect `Iteration 11 - Final/models` to view saved model artifacts and `Iteration 11 - Final/model.py` to see how predictions are produced.

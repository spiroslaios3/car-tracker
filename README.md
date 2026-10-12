# Car Tracker

A personal digital service book for vehicles: keep a maintenance history, fuel entries and reminders (inspection, insurance, tyres, oil changes) in one place.

## Features

- Multiple vehicles with edit and delete
- Service history with costs and notes
- Fuel log with average consumption and cost per km
- Reminders by date and/or mileage, with overdue / due soon status
- Summary of urgent reminders across all vehicles

## Tech stack

- Backend: Python, FastAPI, SQLAlchemy, SQLite
- Frontend: HTML, CSS, vanilla JavaScript

## Run locally
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload

Then open http://127.0.0.1:8000/app/ (API docs at http://127.0.0.1:8000/docs).

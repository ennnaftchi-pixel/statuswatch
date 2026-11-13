# Status Watch

Open-source web service availability monitoring platform.

## About The Project

Status Watch is a lightweight, self-hostable web service supervision platform designed to monitor web services periodically, record their state, send Telegram alerts on failure and recovery, and expose metrics for dashboards. 

This project is developed as part of an academic mini-project for the 2nd-year Computer Science (L2-CS GLSI) curriculum at the Higher Institute of Computer Science of El-Manar (ISI, UTM).

* **Official Start Date:** November 16th, 2026
* **Supervised by:** Dr. Zakia Zouaghia
* **Authors:** Mohamed Nafti and Omar Abdi

---

## Tech Stack

* **Backend / Web:** Python 3.12, FastAPI, Jinja2
* **Database & ORM:** PostgreSQL 16, SQLAlchemy
* **Asynchronous Checks:** asyncio, httpx
* **Alerts:** Telegram Bot API
* **Observability:** Prometheus, Grafana
* **Deployment & Quality:** Docker, Docker Compose, GitHub Actions, pytest, ruff, Trivy

---

## Project Structure

```text
statuswatch/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── checker.py
│   ├── alerts.py
│   ├── security.py
│   ├── metrics.py
│   └── routes/
│       ├── __init__.py
│       ├── public.py
│       └── admin.py
├── templates/
├── tests/
│   └── __init__.py
├── prometheus/
│   └── prometheus.yml
├── grafana/
│   └── provisioning/
├── .github/
│   └── workflows/
│       └── ci.yml
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── pyproject.toml
└── README.md

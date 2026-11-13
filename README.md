# statuswatch
Open-source web service availability monitoring platform

This project is starting officially on November 16th 2026
For now, here's the project's file structure:

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

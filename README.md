# Status Watch

Open-source, lightweight, self-hostable web service availability monitoring platform.

Online services (club websites, APIs, internal apps) often go down before their teams notice—until users complain. Enterprise monitoring suites are either expensive or overly complex for small teams. Status Watch solves this by periodically checking web services, recording response history, sending instant Telegram alerts on failure and recovery, and exposing Prometheus metrics for Grafana dashboards—all deployable with a single `docker compose up` command.

## Academic Context

Developed as an academic mini-project (Outils de Travail Collaboratif — Génie Logiciel et Données) for the 2nd-year Computer Science (L2-CS GLSI) curriculum at the Higher Institute of Computer Science of El-Manar (ISI, Université Tunis El Manar).

- **Academic Year:** 2026/2027
- **Official Start Date:** November 9, 2026
- **MVP Defense Date:** December 4, 2026 (Phase 1: Nov 9 – Dec 3, 2026)
- **Supervised by:** Dr. Zakia Zouaghia
- **Authors:** Mohamed Nafti and Omar Abdi

## Architecture

```text
+-------------------+       HTTP       +-----------------------+       SQL        +----------------+
|  Public Visitor   | ---------------> |                       | ---------------> |   PostgreSQL   |
+-------------------+                  |  FastAPI Application  |                  | (users, checks |
                                       |  (status, admin, API) | <---+            | services,alerts)|
+-------------------+       HTTP       |                       |     |            +----------------+
|   Administrator   | ---------------> +-----------------------+     |                    ^
+-------------------+                    |             |             |                    |
                                   alerts |   schedules |             | scrapes /metrics   | results
                                          v             v             |                    |
                               +---------------+  +---------------+   |            +----------------+
                               | Telegram Bot  |  | Async Checker | --+----------->|   Monitored    |
                               |      API      |  | asyncio+httpx |   |            |    Services    |
                               +---------------+  +---------------+   |            +----------------+
                                                                     |
                                                           +--------------------+  queries  +---------+
                                                           |     Prometheus     | <-------- | Grafana |
                                                           +--------------------+           +---------+
```

### Core Components
- FastAPI Application: Serves the public status page, authenticated admin panel, and the /metrics endpoint.
- Asynchronous Checker (asyncio + httpx): Background worker that concurrently probes active services, stores check results, detects state transitions, and triggers alerts.
- PostgreSQL 16: Stores users, services, checks, and alerts.
- Telegram Bot API: Dispatches a single notification per state transition (down after 2 consecutive failures, and upon recovery).
- Prometheus & Grafana: Collects service uptime/latency metrics and visualizes them on dashboards.
## Non-Functional Requirements

### Security

- Passwords hashed with bcrypt/Argon2.
- Secrets managed strictly via environment variables (never committed to Git).
- Login rate limiting.
- CSRF mitigation via SameSite=Lax session cookies (blocks cross-site form POST attacks in modern browsers).
- SSRF protection (HTTP/HTTPS schemes only, internal/private IP ranges blocked).
- Docker image vulnerability scanning with Trivy.

### Performance

- Monitor 50+ services every 30 seconds asynchronously.
- Public status page rendered in under 500 ms.

### Reliability

- 10-second timeout per HTTP probe so slow targets never block the checker loop.
- Automatic container restarts.

### Usability

- Clean, responsive server-rendered UI where status is communicated with explicit text labels in addition to color indicators.

### Maintainability

- Modular codebase, automated linting (ruff), unit/integration tests (pytest) on every push, and clear installation documentation.

### Portability

- Full stack orchestrated and launched with `docker compose up`.

## Technology Stack

| Technology | Purpose |
|---|---|
| FastAPI | Web framework and application backend |
| Python asyncio + httpx | Concurrent asynchronous HTTP checks |
| PostgreSQL 16 | Relational database |
| SQLAlchemy | Database ORM |
| Telegram Bot API | Notifications |
| Prometheus | Metrics collection |
| Grafana | Monitoring dashboards |
| Docker & Docker Compose | Containerization |
| GitHub Actions | CI/CD automation |
| Ruff | Python linting |
| Pytest | Automated testing |
| Trivy | Container vulnerability scanning |

### Technology Justification

- **FastAPI:** Lightweight, native async support, server-side rendering without a separate frontend repo.
- **asyncio + httpx:** Concurrent non-blocking HTTP checks within a single process.
- **PostgreSQL:** Reliable relational storage with ORM protection against SQL injection.
- **Telegram Bot API:** Free, zero-dependency HTTP webhook delivery, instant mobile notifications.
- **Prometheus & Grafana:** Industry-standard metrics scraping and pre-provisioned dashboards.
- **Docker Compose:** Reproducible multi-container environment launched in one command.
- **GitHub Actions:** Automated linting, testing, Docker builds, and container security scanning on every push.

## Project Structure

```text
statuswatch/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point, lifespan & background checker startup
│   ├── models.py            # SQLAlchemy models (users, services, checks, alerts)
│   ├── checker.py           # Async HTTP probe engine (asyncio + httpx)
│   ├── alerts.py            # Telegram Bot API state-transition notifications
│   ├── security.py          # Password hashing, CSRF, SSRF validation & auth helpers
│   ├── metrics.py           # Prometheus metrics collectors (/metrics)
│   └── routes/
│       ├── __init__.py
│       ├── public.py        # Public status page routes
│       └── admin.py         # Authenticated admin CRUD & history routes
├── templates/               # Jinja2 HTML templates
├── tests/                   # pytest unit & integration test suite
│   └── __init__.py
├── prometheus/
│   └── prometheus.yml       # Prometheus scrape configuration
├── grafana/
│   └── provisioning/        # Pre-configured Grafana datasources & dashboards
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI pipeline (ruff, pytest, Docker, Trivy)
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── pyproject.toml
└── README.md
```

## Functional Requirements

### MVP — Phase 1

- **FA-1:** Administrator login and logout.
- **FA-2:** Create, view, update, and delete monitored services (name, URL, check interval, expected HTTP status).
- **FA-3:** Pause/resume monitoring and toggle public visibility.
- **FA-4:** View check history and configure Telegram notification recipients.
- **FV-1:** Public status page displaying current service status and 24-hour history.
- **FS-1:** Periodically check monitored services and persist results.
- **FS-2:** Declare a service down only after 2 consecutive failures.
- **FS-3:** Send one Telegram alert per state transition (outage or recovery).
- **FS-4:** Expose Prometheus metrics through `/metrics`.
- **FT-1:** Provide a Grafana dashboard for availability, latency, and incidents.

### Phase 2

- **FA-5:** Multi-administrator support with role-based access control (RBAC).
- **FV-2:** Calculate uptime percentages over 24-hour and 7-day periods.
- **FS-5:** Add email/Slack notifications, SSL certificate expiry monitoring, and automatic history purging.

## Roadmap

### Phase 1 — MVP (November 9 – December 3, 2026)

| Week | Planned work |
|---|---|
| Week 1 | Requirements, architecture, repository setup, and Docker environment |
| Week 2 | Authentication, service CRUD, and database integration |
| Week 3 | Asynchronous checker, public status page, and Telegram alerts |
| Week 4 | Prometheus, Grafana, CI/CD, security scanning, testing, documentation, and demo preparation |

**MVP defense:** December 4, 2026.

### Phase 2 — Extensions (Starting December 7, 2026)

- 24-hour and 7-day uptime calculations.
- Login rate limiting and additional security hardening.
- Email and Slack notifications.
- SSL certificate expiry monitoring.
- Terraform-based cloud deployment.
- Multi-user authentication and RBAC.

## Getting Started

### Prerequisites

- Git
- Docker
- Docker Compose

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ennnaftchi-pixel/statuswatch.git
   cd statuswatch
   ```

2. Create your environment configuration:

   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and configure the required database credentials, application secret, and Telegram bot settings.

4. Build and start the application:

   ```bash
   docker compose up -d --build
   ```

### Service URLs

| Service | URL |
|---|---|
| Public status page | http://localhost:8000 |
| Admin panel | http://localhost:8000/admin |
| Prometheus metrics | http://localhost:8000/metrics |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

## Development Workflow

- Use GitHub Issues to track requirements, bugs, and tasks.
- Create feature branches using `feat/feature-name`.
- Create bug-fix branches using `fix/bug-name`.
- Open pull requests against `main`.
- Run Ruff, Pytest, Docker builds, and Trivy checks before merging.

## License

This project is distributed under the MIT License. See [LICENSE](LICENSE) for details.

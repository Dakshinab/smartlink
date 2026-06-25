# SmartLink - AI-Powered URL Shortener with DevOps Pipeline

![CI/CD](https://github.com/Dakshinab/smartlink/actions/workflows/deploy.yml/badge.svg)

A production-grade URL shortener built with a complete DevOps pipeline - containerized microservices, automated CI/CD, cloud infrastructure as code, and real-time monitoring.

Live: http://161.118.245.201/health

---

## Architecture

```
Developer -> GitHub -> GitHub Actions -> Docker -> Oracle Cloud (Singapore)
                                                         |
                                                 Nginx (reverse proxy)
                                                         |
                                             Flask Link Service (API)
                                                         |
                                          Prometheus + Grafana (monitoring)
```

---

## Tech Stack

| Category | Technology |
|---|---|
| Backend | Python, Flask, SQLAlchemy |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Infrastructure | Terraform, Oracle Cloud Always Free |
| Web Server | Nginx reverse proxy |
| Monitoring | Prometheus, Grafana, Node Exporter |
| Database | SQLite dev, PostgreSQL prod |
| Testing | Pytest |

---

## Features

- URL Shortening - create short links with auto-generated or custom slugs
- Click Tracking - every redirect is counted in real time
- REST API - full CRUD with pagination and input validation
- Automated Testing - 7 pytest tests run on every push
- Auto Deployment - git push triggers full CI/CD pipeline
- Infrastructure as Code - entire cloud network built with Terraform
- Live Monitoring - Grafana dashboard showing server and app metrics
- Soft Delete - links deactivated not deleted, history preserved
- Rate Limiting - Nginx rate limiting to prevent API abuse

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Health check |
| POST | /links | Create short link |
| GET | /<short_code> | Redirect to original URL |
| GET | /links | List all links with pagination |
| DELETE | /links/<id> | Deactivate a link |

### Create a short link

```bash
curl -X POST http://161.118.245.201/links \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://github.com", "title": "GitHub"}'
```

### Response

```json
{
  "short_code": "aB3kR9",
  "short_url": "http://161.118.245.201/aB3kR9",
  "original_url": "https://github.com",
  "click_count": 0,
  "created_at": "2026-06-24T10:00:00",
  "is_active": true
}
```

### Create with custom slug

```bash
curl -X POST http://161.118.245.201/links \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://github.com", "custom_slug": "my-github"}'
```

### List all links

```bash
curl http://161.118.245.201/links?page=1&per_page=10
```

---

## DevOps Pipeline

Every git push triggers this automated pipeline:

```
git push
    |
GitHub Actions triggered
    |
Install Python 3.12 and dependencies
    |
Run 7 automated pytest tests
    |
If tests pass - build Docker image
    |
Push image to GitHub Container Registry (GHCR)
    |
Image available for deployment to Oracle Cloud Singapore
```

---

## Infrastructure as Code (Terraform)

All Oracle Cloud infrastructure is defined as code in the terraform/ directory:

- Virtual Cloud Network (VCN) with CIDR 10.0.0.0/16
- Internet Gateway for public traffic
- Route Tables for network routing
- Security Lists with firewall rules for ports 22, 80, 443, 5001, 3000, 9090
- Ubuntu 22.04 VM on Oracle Always Free tier (Singapore region)

```bash
cd terraform
terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

---

## Monitoring Stack

Grafana dashboard: http://161.118.245.201:3000

| Tool | Purpose | Port |
|---|---|---|
| Prometheus | Metrics collection and storage | 9090 |
| Grafana | Dashboard and visualization | 3000 |
| Node Exporter | Server hardware metrics | 9100 |

Metrics collected:
- Server CPU usage
- Memory usage
- Disk usage
- Network traffic
- HTTP request rates

---

## Local Development

```bash
# Clone repo
git clone https://github.com/Dakshinab/smartlink.git
cd smartlink/link-service

# Create virtual environment
python -m venv venv

# Activate - Windows
venv\Scripts\activate

# Activate - Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python run.py

# Run tests
python -m pytest tests/ -v
```

App runs at http://localhost:5001

---

## Run with Docker

```bash
# Build image
docker build -t smartlink-link-service .

# Run container
docker run -p 5001:5001 smartlink-link-service

# Run full stack with monitoring
docker compose up -d
```

---

## Project Structure

```
smartlink/
|
|-- link-service/              Flask REST API microservice
|   |-- app/
|   |   |-- __init__.py        App factory and database setup
|   |   |-- models.py          SQLAlchemy database models
|   |   |-- routes.py          API endpoints
|   |   |-- utils.py           Helper functions
|   |-- tests/
|   |   |-- test_routes.py     7 automated pytest tests
|   |-- Dockerfile             Container definition
|   |-- requirements.txt       Python dependencies
|   |-- run.py                 App entry point
|
|-- terraform/                 Infrastructure as Code
|   |-- main.tf                Oracle Cloud resources
|
|-- nginx/
|   |-- nginx.conf             Reverse proxy configuration
|
|-- prometheus/
|   |-- prometheus.yml         Metrics scraping config
|
|-- .github/
|   |-- workflows/
|       |-- deploy.yml         CI/CD pipeline
|
|-- docker-compose.yml         Full stack definition
|-- README.md                  This file
```

---

## What I Learned

- Designing and building a REST API from scratch using Flask
- Containerizing applications with Docker
- Writing automated tests with pytest
- Building CI/CD pipelines with GitHub Actions
- Provisioning cloud infrastructure with Terraform
- Deploying and managing applications on Oracle Cloud
- Setting up reverse proxy and rate limiting with Nginx
- Monitoring applications with Prometheus and Grafana

---

## Author

Dakshina Dissanayake
GitHub: https://github.com/Dakshinab
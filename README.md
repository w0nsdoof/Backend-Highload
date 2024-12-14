# Project Overview
This project was developed as a final exam submission for the "Backend for High-Load Environments" university course. The primary objective was to design and implement a scalable, robust backend system that addresses challenges in distributed, high-load environments while ensuring data consistency, system scalability, and effective observability.

![project diagram](docs/images/image-1.png)
## Technologies and Architecture
- **Backend Framework**: Django with Django Rest Framework (DRF)
- **Database**: PostgreSQL (primary and read replica)
- **Caching & Message Broker**: Redis
- **Task Queue**: Celery
- **Web Server**: Nginx (Load Balancer)
- **Monitoring**: Prometheus and Grafana
- **Containerization**: Docker

## Key Features Implemented
![bpmn diagram](docs/images/image.png)

### 1. Scalable API Design
- Developed a comprehensive Django API using viewsets and model serializers
- Implemented efficient backend functionalities for e-commerce platform

### 2. Multiple Service Instances
- Configured three separate django instances to handle concurrent requests
- Enabled horizontal scaling and improved request processing
![docker compose up](docs/images/image-4.png)
### 3. Load Balancing with Nginx
- Implemented Nginx as a load balancer to distribute incoming traffic
- Achieved performance improvements of approximately 2.85x compared to single-instance setup
![apache benchmark](docs/images/image-3.png)
### 4. Database Optimization
- Established a primary PostgreSQL database with a dedicated read replica
- Offloaded read-heavy operations to improve query response times
- Implemented database indexing and optimization strategies
![dbml diagram](docs/images/image-2.png)

### 5. Monitoring and Observability
- Integrated Prometheus for comprehensive metrics collection
![prometheus dashboard](docs/images/image-6.png)
- Utilized Grafana for real-time visualization of system performance
![grafana dashboard](docs/images/image-5.png)
- Implemented Django's built-in logging mechanisms
![logging settings](docs/images/image-7.png)

## Security Features
- Rate limiting on sensitive endpoints
- JWT authentication with encryption
![security encryption](docs/images/image-9.png)
- Security headers implementation
![custom middleware](docs/images/image-8.png)
- Secure password reset mechanisms

# Project Setup Guide

## Prerequisites
- Docker
- Docker Compose
- Git

## Configuration Steps

### 1. Clone the Repository
```bash
git clone [<repository-url>](https://github.com/w0nsdoof/E-commerce.git)
```

### 2. Create Environment Configuration
Create a `.env` file in the `config` folder with the following contents:

```env
# Django Secret Key
SECRET_KEY='django-insecure-e3wvg@csq3gl3ygj9i_bk)kkbxgoen9hcm7%hc7=v^7h&=nnih'

# Email Configuration
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT='587'
EMAIL_HOST_USER="example@gmail.com"
EMAIL_HOST_PASSWORD="abcd efgh ijkl mnop"

# Database Configuration
DB_NAME="final"
DB_USER="postgres"
DB_PASSWORD="1473"
DB_HOST='postgres'
DB_PORT=5432

DB_REPLICA_HOST='postgres'
DB_REPLICA_PORT=5433

# Application Settings
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://postgres:postgres@postgres:5432/backend_highload
REDIS_URL=redis://redis:6379/0
```

### 3. Prometheus Configuration
Create a `prometheus.yml` file with the following configuration:

```yaml
global:
  scrape_interval: 5s
  evaluation_interval: 5s

scrape_configs:
  - job_name: "prometheus"
    scrape_interval: 10s
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "django"
    static_configs:
      - targets: ["localhost:8000", "localhost:8001", "localhost:8002"]
```

### 4. Deploy the Application
Run the following command to start the application:

```bash
docker-compose up --build
```

## Important Notes
- Replace email credentials with your actual SMTP settings
- Modify `ALLOWED_HOSTS` as needed for your deployment environment
- Ensure you have the necessary ports available (80, 8000, 5432, etc.)

## Accessing the Application
- **Main Application**: http://localhost
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (default credentials)

## Troubleshooting
- Verify Docker and Docker Compose are properly installed
- Check that no other services are using the required ports

## Conclusion
The project demonstrates an advanced approach to building scalable, observable backend systems. By combining modern technologies and architectural patterns, the solution provides a robust framework for handling high-load environments while maintaining system reliability and performance.

## What is left from Final requirements
- Implementation of full (CI/CD) pipeline

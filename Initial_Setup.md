# Legal Automation System - Development Setup Guide

## Initial Setup

### 1. Development Environment Setup

#### Prerequisites Installation
```bash
# Install Python 3.8+
sudo apt update
sudo apt install python3.8 python3.8-venv python3.8-dev

# Install Node.js 16+
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install nodejs

# Install MongoDB 4.4+
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt update
sudo apt install mongodb-org
```

#### Python Virtual Environment
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install development requirements
pip install -r requirements-dev.txt
```

### 2. Security Configuration

#### SSL/TLS Setup
```bash
# Generate SSL certificates for development
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ./certs/dev.key \
    -out ./certs/dev.crt
```

#### Environment Variables
Create `.env` files for different environments:

```bash
# Create environment files
cp .env.example .env.development
cp .env.example .env.test
```

Example `.env.development`:
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/legal_automation
MONGODB_URI=mongodb://localhost:27017/legal_automation

# Security
JWT_SECRET=your-secure-jwt-secret
ENCRYPTION_KEY=your-secure-encryption-key
ALLOWED_ORIGINS=http://localhost:3000

# External Services
LEGAL_RESEARCH_API_KEY=your-api-key
ESIGN_API_KEY=your-esign-api-key

# AI Configuration
OPENAI_API_KEY=your-openai-api-key
AI_MODEL_PATH=/path/to/models

# Logging
LOG_LEVEL=DEBUG
LOG_PATH=/path/to/logs
```

### 3. Database Initialization

#### PostgreSQL Setup
```bash
# Create databases
createdb legal_automation
createdb legal_automation_test

# Run migrations
alembic upgrade head

# Seed initial data
python scripts/seed_data.py
```

#### MongoDB Setup
```bash
# Start MongoDB service
sudo systemctl start mongod

# Create collections and indexes
python scripts/init_mongodb.py
```

### 4. Version Control Setup

#### Git Configuration
```bash
# Initialize git repository
git init

# Configure git hooks
cp hooks/* .git/hooks/
chmod +x .git/hooks/*

# Configure git ignore
cp .gitignore.example .gitignore
```

Add to `.gitignore`:
```gitignore
# Virtual Environment
venv/
.env*

# Development Certificates
certs/

# IDE files
.vscode/
.idea/

# Compiled files
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# Logs
logs/
*.log

# Test coverage
.coverage
htmlcov/

# Build files
dist/
build/
*.egg-info/

# Node modules
node_modules/
```

### 5. Development Tools Setup

#### Install Development Tools
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Install testing tools
pip install pytest pytest-cov pytest-asyncio

# Install linting tools
pip install flake8 black isort mypy

# Install frontend development tools
npm install -g typescript eslint prettier
```

#### Configure Code Formatting
Create `pyproject.toml`:
```toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
```

Create `.flake8`:
```ini
[flake8]
max-line-length = 88
extend-ignore = E203
exclude = .git,__pycache__,build,dist
```

### 6. Running the Application

#### Start Backend Services
```bash
# Start API Gateway
uvicorn backend.api_gateway.main:app --reload --port 8000

# Start individual services
uvicorn backend.document_service.app:app --reload --port 8001
uvicorn backend.template_service.app:app --reload --port 8002
uvicorn backend.compliance_service.app:app --reload --port 8003
uvicorn backend.ai_orchestrator.app:app --reload --port 8004
```

#### Start Frontend Development Server
```bash
cd frontend
npm install
npm start
```

### 7. Testing Setup

#### Configure Test Environment
```bash
# Create test database
createdb legal_automation_test

# Run migrations on test database
DATABASE_URL=postgresql://user:password@localhost:5432/legal_automation_test alembic upgrade head

# Run tests
pytest
```

#### Configure Test Coverage
Create `pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
asyncio_mode = auto
```

### 8. Monitoring Setup

#### Install Monitoring Tools
```bash
# Install monitoring packages
pip install prometheus_client grafana-api

# Start Prometheus
docker run -d \
    -p 9090:9090 \
    -v ./prometheus.yml:/etc/prometheus/prometheus.yml \
    prom/prometheus

# Start Grafana
docker run -d \
    -p 3000:3000 \
    grafana/grafana
```

### 9. CI/CD Setup

Create `.github/workflows/ci.yml`:
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest
```

### 10. Documentation

#### Generate API Documentation
```bash
# Install documentation tools
pip install sphinx sphinx-autodoc-typehints

# Generate documentation
cd docs
make html
```

## Troubleshooting

Common issues and solutions:

1. **Database Connection Issues**
   - Check if database services are running
   - Verify connection strings in .env files
   - Ensure proper permissions are set

2. **SSL/TLS Certificate Issues**
   - Regenerate certificates
   - Check certificate paths in configuration
   - Verify certificate permissions

3. **Permission Issues**
   - Check file permissions for logs and certificates
   - Verify database user permissions
   - Check service account permissions

4. **Port Conflicts**
   - Check if ports are already in use
   - Modify service ports in configuration
   - Stop conflicting services

## Next Steps

After completing the setup:

1. Review security configurations
2. Set up monitoring dashboards
3. Configure backup systems
4. Set up continuous integration
5. Review deployment strategies
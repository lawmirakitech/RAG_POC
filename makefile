# Makefile for RAG POC

# Default environment name
ENV_NAME = rag_env

# === ENVIRONMENT ===

# Create conda environment from environment.yml
setup-env:
	# Create conda environment if it doesn't exist
	conda env create -f environment.yml -n $(ENV_NAME) || echo "Environment '$(ENV_NAME)' already exists"
	# Create .env file from template if it doesn't exist
	@if [ ! -f .env ]; then \
		echo "Creating .env file from template..."; \
		cp .env.example .env; \
	else \
		echo ".env already exists. Skipping."; \
	fi

# Activate conda environment (for interactive usage)
activate-env:
	@echo "Run the following command in your shell to activate the environment:"
	@echo "conda activate $(ENV_NAME)"

# Remove environment (cleanup)
remove-env:
	conda env remove -n $(ENV_NAME) -y

# === DOCKER ===

# Build all services
docker-build:
	docker-compose build

# Run all services
docker-up:
	docker-compose up

# Run all services in detached mode
docker-up-detach:
	docker-compose up -d

# Stop all services
docker-down:
	docker-compose down

# Clean up containers, volumes, and networks
docker-clean:
	docker-compose down -v --remove-orphans

# === APP RUN (LOCAL) ===

# Run FastAPI backend locally (for dev/debug, assumes conda env is active)
run-backend:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Run Streamlit frontend locally (for dev/debug, assumes conda env is active)
run-frontend:
	streamlit run frontend/app.py

# === UTILITIES ===

# Linting (example with flake8)
lint:
	flake8 backend frontend

# Format code (example with black)
format:
	black backend frontend

# Remove Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +

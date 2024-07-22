# Variables
DC := docker compose
DB := db
DOCKER_COMPOSE_FILE := docker-compose.yml
ENV_FILE := .env

# Default target
.DEFAULT_GOAL := help


# Development targets
# Run in local mode
run:
	@echo "Running in local mode."
	$(DC) -f $(DOCKER_COMPOSE_FILE) create $(DB)
	$(DC) -f $(DOCKER_COMPOSE_FILE) start $(DB)
	poetry run start

# Help target
help:
	@echo "Available targets:"
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^# (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 2, RLENGTH); \
			printf "\033[36m%-30s\033[0m %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

# Run linters: pre-commit (black, ruff, codespell) and mypy
lint:
	pre-commit install
	git ls-files | xargs pre-commit run --show-diff-on-failure --files

# Run code autoformatters (black).
format:
	pre-commit install
	git ls-files | xargs pre-commit run ruff-format --files

# Run all services in docker
up:
	@echo "Running all services in docker."
	$(DC) --env-file $(ENV_FILE) up -d

# Stop all services
down:
	@echo "Stopping all services."
	$(DC) down

# Build docker images
docker-build:
	$(DC) build

# Clean docker environment
docker-clean:
	$(DC) down -v
	docker system prune -f
	docker volume prune -f

# Refresh local database
refresh_db:
	@echo -n "Are you sure you want to refresh the local database? This will delete all data in your local db. [Y/n] "
	@read ans && [ $${ans:-N} = Y ] && $(MAKE) confirmed_refresh_db || echo "Aborting."

confirmed_refresh_db:
	@echo "Refreshing database."
	$(DC) down $(DB)
	docker volume rm backend_postgres_data

# Refresh all local services
refresh_all:
	@echo -n "Are you sure you want to refresh all local services? [Y/n] "
	@read ans && [ $${ans:-N} = Y ] && $(MAKE) confirmed_refresh_all || echo "Aborting."

confirmed_refresh_all:
	$(DC) down
	yes | docker system prune
	docker volume rm backend_mongo-volume backend_rabbitmq-volume
	$(MAKE) confirmed_refresh_db



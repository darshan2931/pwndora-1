.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend lint lint-backend test test-backend clean migrate migrate-generate migrate-upgrade docker-up docker-down docker-logs

help:
	@echo "Commands:"
	@echo "  install          Install all dependencies"
	@echo "  install-backend  Install Python dependencies"
	@echo "  install-frontend Install Node dependencies"
	@echo "  dev              Run backend + frontend dev servers"
	@echo "  dev-backend      Run FastAPI dev server"
	@echo "  dev-frontend     Run Next.js dev server"
	@echo "  lint             Run all linters"
	@echo "  lint-backend     Run Python linter"
	@echo "  test             Run all tests"
	@echo "  test-backend     Run Python tests"
	@echo "  clean            Remove cache files"
	@echo "  migrate          Run Alembic migrations"
	@echo "  migrate-generate Generate a new migration"
	@echo "  migrate-upgrade  Upgrade database to latest"
	@echo "  docker-up        Start Docker services"
	@echo "  docker-down      Stop Docker services"
	@echo "  docker-logs      Follow Docker logs"

install: install-backend install-frontend

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

dev: dev-backend dev-frontend

dev-backend:
	cd backend && uvicorn app.main:app --reload

dev-frontend:
	cd frontend && npm run dev

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

lint-backend:
	cd backend && ruff check .

test:
	cd backend && pytest
	cd frontend && npm test

test-backend:
	cd backend && pytest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	find . -type d -name .next -exec rm -rf {} +
	rm -rf backend/.pytest_cache frontend/.next

migrate:
	cd backend && alembic upgrade head

migrate-generate:
	cd backend && alembic revision --autogenerate -m "$(msg)"

migrate-upgrade:
	cd backend && alembic upgrade head

migrate-downgrade:
	cd backend && alembic downgrade -1

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

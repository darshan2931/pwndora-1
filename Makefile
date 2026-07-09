.PHONY: help backend frontend install-backend install-frontend dev-backend dev-frontend lint test clean

help:
	@echo "Commands:"
	@echo "  install-backend   Install Python dependencies"
	@echo "  install-frontend  Install Node dependencies"
	@echo "  dev-backend       Run FastAPI dev server"
	@echo "  dev-frontend      Run Next.js dev server"
	@echo "  lint              Run all linters"
	@echo "  test              Run all tests"
	@echo "  clean             Remove cache files"

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

dev-backend:
	cd backend && uvicorn app.main:app --reload

dev-frontend:
	cd frontend && npm run dev

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

test:
	cd backend && pytest
	cd frontend && npm test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	find . -type d -name .next -exec rm -rf {} +
	find . -type d -name node_modules -exec rm -rf {} +
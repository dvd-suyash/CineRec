.PHONY: up down db-shell redis-shell install dev test lint

up:
	docker-compose up -d

down:
	docker-compose down

db-shell:
	docker-compose exec postgres psql -U cinerec_user -d cinerec

redis-shell:
	docker-compose exec redis redis-cli

install:
	uv sync
	cd apps/web && npm install

dev-api:
	uv run uvicorn apps.api.app.main:app --reload --port 8000

dev-web:
	cd apps/web && npm run dev

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run pyright
	cd apps/web && npm run lint


e2e:
	bash scripts/e2e_check.sh

load-test:
	uv run locust -f scripts/load_test.py --headless -u 100 -r 10 -t 1m


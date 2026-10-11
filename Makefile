.PHONY: up down test test-backend test-frontend spec lint audit

up:
	docker compose up --build

down:
	docker compose down -v

test: test-backend test-frontend

test-backend:
	cd backend && pytest -q

test-frontend:
	cd frontend && npm test

spec:
	cd backend && SEED_ON_STARTUP=false DATABASE_URL=sqlite:///./tmp-spec.db python -c "import yaml, sys; sys.path.insert(0,'.'); from app.main import app; open('../openapi.yaml','w',encoding='utf-8').write(yaml.safe_dump(app.openapi(), sort_keys=False, allow_unicode=True))" && rm -f backend/tmp-spec.db

lint:
	cd backend && ruff check app tests

audit:
	pip-audit -r backend/requirements.txt
	bandit -q -r backend/app
	cd frontend && npm audit --audit-level=high

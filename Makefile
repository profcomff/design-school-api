run:
	source ./venv/bin/activate && uvicorn --reload --log-level debug design_bot.routes.base:app

db:
	docker compose up -d

migrate:
	alembic upgrade head

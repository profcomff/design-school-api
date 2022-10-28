run:
	source ./venv/bin/activate && uvicorn --reload --log-level debug design_bot.routes.base:app

db:
	docker-compose -f docker-compose.yml up -d --remove-orphans

migrate:
	alembic upgrade head

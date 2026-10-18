IMAGE_BASE := payment-base
IMAGE_API := payment-api
IMAGE_WORKER := payment-worker
IMAGE_MIGRATOR := payment-migrator

.PHONY: build-base build-api build-worker build-migrator build revision up down

build-base:
	docker build -f Dockerfile.base -t $(IMAGE_BASE) .

build-api: build-base
	docker build -f Dockerfile.api -t $(IMAGE_API) .

build-worker: build-base
	docker build -f Dockerfile.worker -t $(IMAGE_WORKER) .

build-migrator: build-base
	docker build -f Dockerfile.migrator -t $(IMAGE_MIGRATOR) .

build: build-api build-worker build-migrator

revision:
	@test -n "$(message)" || (echo "usage: make revision message='describe the change'" && exit 1)
	uv run alembic revision --autogenerate -m "$(message)"

up: build
	docker compose up -d

down:
	docker compose down

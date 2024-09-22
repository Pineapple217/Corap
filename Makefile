DOCKER_TAG ?= latest

docker-build:
	docker build -t ghcr.io/pineapple217/corap-scraper:$(DOCKER_TAG) --build-arg GIT_COMMIT=$(shell git log -1 --format=%h) . 

docker-push:
	docker push ghcr.io/pineapple217/corap-scraper:$(DOCKER_TAG)

docker-update:
	@make --no-print-directory docker-build
	@make --no-print-directory docker-push
PY ?= python3
GROUP ?= all

.PHONY: install data data-daily data-monthly data-yearly analyses dev build test lint e2e lighthouse clean

install:
	$(PY) -m pip install -r requirements.txt
	npm ci

# Hent alle data og kjør analyser (GROUP=daily|monthly|yearly|all)
data:
	$(PY) -m pipeline.run --group $(GROUP)

data-daily:
	$(PY) -m pipeline.run --group daily

data-monthly:
	$(PY) -m pipeline.run --group monthly

data-yearly:
	$(PY) -m pipeline.run --group yearly

# Kjør bare analysene på allerede nedlastede data
analyses:
	$(PY) -m pipeline.run --analyses-only

dev:
	npm run dev

build:
	npm run build

test:
	$(PY) -m pytest -q pipeline/tests
	npm run typecheck
	npm run lint

lint:
	$(PY) -m ruff check pipeline
	npm run lint

e2e: build
	npm run e2e

lighthouse: build
	npm run lighthouse

clean:
	rm -rf dist node_modules/.vite

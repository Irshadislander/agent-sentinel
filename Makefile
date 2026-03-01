install:
	pip install -e .

test:
	pytest -q

lint:
	ruff check .

fmt:
	ruff format .

type:
	mypy src

ci:
	$(MAKE) fmt
	$(MAKE) lint
	$(MAKE) type
	$(MAKE) test

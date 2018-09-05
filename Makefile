unit:
	pytest -v

coverage:
	pytest --cov=antismash_clean --cov-report=html --cov-report=term-missing

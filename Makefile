PYTHON ?= python3
.PHONY: test experiments synthesis check-all skpr_sim independent-commit independent-commit-followup

test:
	$(PYTHON) scripts/run_checks.py core

experiments:
	$(PYTHON) scripts/run_checks.py experiments

synthesis:
	$(PYTHON) scripts/run_checks.py synthesis

check-all:
	$(PYTHON) scripts/run_checks.py all

skpr_sim:
	$(PYTHON) scripts/run_checks.py keeper

independent-commit:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) experiments/bounded_commit/run.py

independent-commit-followup:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) experiments/bounded_commit/followup.py

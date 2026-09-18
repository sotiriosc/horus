PYTHON ?= python3
.PHONY: test experiments synthesis check-all skpr_sim independent-commit independent-commit-followup base-framework-v0 base-framework-v1

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

base-framework-v0:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m experiments.base_framework_v0.run

base-framework-v1:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m experiments.base_framework_v1.run

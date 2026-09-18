PYTHON ?= python3
.PHONY: test experiments synthesis check-all skpr_sim

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

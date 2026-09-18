# Working-directory compatibility: use the same checked root entry points.
PYTHON ?= python3
.PHONY: test skpr_sim experiments synthesis

test skpr_sim experiments synthesis:
	$(MAKE) -C .. $@ PYTHON=$(PYTHON)

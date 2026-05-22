.PHONY: test eval-all eval-env search final-eval report deepdive-report rl-baseline

PYTHON ?= python3
ENV ?= CartPole-v1
POLICY ?= initial
SPLIT ?= dev
MAX_CANDIDATES ?= 32
TRAIN_STEPS ?= 10000
ALGO ?= ppo

test:
	PYTHONPATH=. $(PYTHON) -m pytest tests

eval-all:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.evaluate --all --split $(SPLIT)

eval-env:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.evaluate --env $(ENV) --policy $(POLICY) --split $(SPLIT)

search:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.search --all --split dev --max-candidates $(MAX_CANDIDATES)

final-eval:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.evaluate --all --split holdout

report:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.report

deepdive-report:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.deepdive_report


rl-baseline:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.rl_baseline --env $(ENV) --split $(SPLIT) --algo $(ALGO) --train-steps $(TRAIN_STEPS)

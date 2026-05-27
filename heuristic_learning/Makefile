.PHONY: test verify list-envs check-env-layout check-env check-promotion check-promotions check-envs check-planned-envs scaffold-env scaffold-env-code scaffold-env-tests scaffold-generic-env scaffold-custom-env custom-run custom-verify eval-all eval-env search search-env summary summary-env final-eval report report-env audit-env deepdive-report rl-baseline slimevolley-doctor slimevolley-audit slimevolley-verify slimevolley-eval slimevolley-report slimevolley-performance-report slimevolley-generation-report slimevolley-generation3-report slimevolley-protocol slimevolley-generation3-protocol slimevolley-generation4-protocol slimevolley-generation5-protocol slimevolley-summary slimevolley-contact-diagnostics slimevolley-critic slimevolley-search slimevolley-tournament slimevolley-final-eval

PYTHON ?= python3
ENV ?= CartPole-v1
POLICY ?= initial
OPPONENT ?= builtin
SPLIT ?= dev
MAX_CANDIDATES ?= 32
TRAIN_STEPS ?= 10000
ALGO ?= ppo
PARTICIPANTS ?= random initial improved-v0 improved-v1 improved-v2 improved-v3 improved-v4 improved-v5 improved-v6 improved improved-tuned attack rally-serve post-contact planner teacher-assisted
CUSTOM_COMMAND ?= list
ARGS ?=

test:
	PYTHONPATH=. $(PYTHON) -m pytest tests

verify:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.registry --check-envs
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.registry --check-planned
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.registry --check-artifacts
	PYTHONPATH=. $(PYTHON) -m pytest tests

list-envs:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.registry $(ARGS)

check-env-layout:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.registry --check-artifacts $(ARGS)

check-env:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.registry --check-env $(ENV) $(ARGS)

check-promotion:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.registry --check-promotion $(ENV) $(ARGS)

check-promotions:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.registry --check-promotions $(ARGS)

check-envs:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.registry --check-envs $(ARGS)

check-planned-envs:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.registry --check-planned $(ARGS)

scaffold-env:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.artifacts --scaffold-env $(ENV) $(ARGS)

scaffold-env-code:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.artifacts --scaffold-env-code $(ENV) $(ARGS)

scaffold-env-tests:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.artifacts --scaffold-tests $(ENV) $(ARGS)

scaffold-generic-env:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.artifacts --scaffold-env $(ENV) --scaffold-env-code $(ENV) --scaffold-tests $(ENV) $(ARGS)

scaffold-custom-env:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.artifacts --scaffold-env $(ENV) --scaffold-env-code $(ENV) --custom-registration --scaffold-custom-code $(ENV) --scaffold-tests $(ENV) $(ARGS)

custom-run:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom --env $(ENV) $(CUSTOM_COMMAND) $(ARGS)

custom-verify:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom --env $(ENV) verify

eval-all:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.evaluate --all --split $(SPLIT) $(ARGS)

eval-env:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.evaluate --env $(ENV) --policy $(POLICY) --split $(SPLIT) $(ARGS)

search:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.search --all --split dev --max-candidates $(MAX_CANDIDATES) $(ARGS)

search-env:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.search --env $(ENV) --split dev --max-candidates $(MAX_CANDIDATES) $(ARGS)

summary:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.summarize $(ARGS)

summary-env:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.summarize --env $(ENV) --env-artifacts $(ARGS)

final-eval:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.evaluate --all --split holdout

report:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.report $(ARGS)

report-env:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.report --env $(ENV) --env-artifacts $(ARGS)

audit-env:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.artifact_audit --env $(ENV) --write-latest $(ARGS)

deepdive-report:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.deepdive_report


rl-baseline:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.rl_baseline --env $(ENV) --split $(SPLIT) --algo $(ALGO) --train-steps $(TRAIN_STEPS) $(ARGS)

slimevolley-doctor:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.doctor $(ARGS)

slimevolley-audit:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.audit $(ARGS)

slimevolley-verify:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.registry --check-env SlimeVolley-v0
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.registry --check-envs
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.registry --check-artifacts
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.summarize
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.contact_diagnostics
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.report
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.performance_report
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.generation_report
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.generation_report --generation 3
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.protocol
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.protocol --generation 3
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.protocol --generation 4
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.protocol --generation 5
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.audit --output experiments/slimevolley/results/audit_latest.json

slimevolley-eval:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.evaluate --policy $(POLICY) --opponent $(OPPONENT) --split $(SPLIT) $(ARGS)

slimevolley-report:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.report $(ARGS)

slimevolley-performance-report:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.performance_report $(ARGS)

slimevolley-generation-report:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.generation_report $(ARGS)

slimevolley-generation3-report:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.generation_report --generation 3 $(ARGS)

slimevolley-protocol:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.protocol $(ARGS)

slimevolley-generation3-protocol:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.protocol --generation 3 $(ARGS)

slimevolley-generation4-protocol:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.protocol --generation 4 $(ARGS)

slimevolley-generation5-protocol:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.protocol --generation 5 $(ARGS)

slimevolley-summary:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.summarize $(ARGS)

slimevolley-contact-diagnostics:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.contact_diagnostics $(ARGS)

slimevolley-critic:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.critic $(ARGS)

slimevolley-search:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.search --split dev --max-candidates $(MAX_CANDIDATES) $(ARGS)

slimevolley-tournament:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.tournament --split $(SPLIT) --participants $(PARTICIPANTS) $(ARGS)

slimevolley-final-eval:
	PYTHONPATH=. $(PYTHON) -m hl_benchmark.custom_envs.slimevolley.final_eval $(ARGS)

# Generation-5 Teacher-Serve Macro Probe

Date: 2026-05-27

## Scope

This note records a development-only probe of fixed serve/reset macros inspired
by generation-5 `baseline-rnn` traces. The neural comparator was used only as a
teacher for rule discovery; no maintained heuristic calls the neural policy at
runtime.

No maintained policy/config/test edit was promoted. No canonical ledger row was
appended. No generation-5 holdout seeds `13000..13049` and no generation-5
audit seeds `14000..14049` were used.

Artifacts:

- Probe script: `experiments/slimevolley/probes/g5_teacher_serve_probe.py`
- JSON result: `experiments/slimevolley/results/generation_5_teacher_serve_probe.json`

Seed use:

- Short screen: `12000..12015`
- Full fixed-pool check for `serve_110_10`: `12000..12049`

Cost accounting:

- Observed environment steps: `4,529,047` (`1,828,760` short-screen steps plus `2,700,287` full fixed-pool steps).
- LLM token cost is unavailable.

## Candidate Family

All transient candidates wrapped `net-pressure` and replaced the reset/serve
window with a fixed transparent macro. The main teacher-derived action was
`110`, because baseline-rnn traces showed repeated `110` actions immediately
after reset. Other screened variants mixed `110`, `101`, `111`, and jump-only
beats.

## Short Screen

Seeds: `12000..12015`.

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `net-pressure` reference | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | reference |
| `baseline-rnn` | `0.2500`, `7/3/6` | `4.1875`, `16/0/0` | `3.7500`, `16/0/0` | `2.5625`, `14/0/2` | `2.5625`, `14/0/2` | comparator |
| `serve_110_6` | `-0.3125`, `1/5/10` | `2.8125`, `14/0/2` | `2.3125`, `12/0/4` | `1.4375`, `13/2/1` | `1.4375`, `13/2/1` | reject |
| `serve_110_10` | `-0.1250`, `3/4/9` | `3.0000`, `15/0/1` | `3.1250`, `15/0/1` | `1.8750`, `14/1/1` | `1.8125`, `14/1/1` | full check |
| `serve_110_14` | `-0.3125`, `1/5/10` | `2.8750`, `15/0/1` | `2.8125`, `14/0/2` | `1.6250`, `13/1/2` | `1.6250`, `13/1/2` | reject |
| `serve_110_6_101_4` | `-0.4375`, `0/5/11` | `2.6250`, `14/0/2` | `1.9375`, `12/0/4` | `1.5625`, `13/1/2` | `1.5625`, `13/1/2` | reject |
| `serve_110_3_101_5` | `-0.2500`, `0/4/12` | `3.2500`, `16/0/0` | `2.8750`, `15/0/1` | `1.1875`, `10/2/4` | `1.1875`, `10/2/4` | reject |
| `serve_110_alt_jump` | `-0.2500`, `1/5/10` | `3.3125`, `16/0/0` | `2.8125`, `15/0/1` | `1.5625`, `12/1/3` | `1.5625`, `12/1/3` | reject |

## Full Development Check

Seeds: `12000..12049`. The table shows absolute rows for the only full-checked
macro.

| Opponent | `net-pressure` | `baseline-rnn` | `serve_110_10` | `serve_110_10` minus `net-pressure` | `serve_110_10` minus `baseline-rnn` |
| --- | ---: | ---: | ---: | ---: | ---: |
| `builtin` | `-0.06`, `11/14/25` | `-0.18`, `18/19/13` | `-0.12`, `10/12/28` | `-0.06` | `+0.06` |
| `random` | `4.90`, `50/0/0` | `4.88`, `50/0/0` | `4.90`, `50/0/0` | `0.00` | `+0.02` |
| `initial` | `4.86`, `50/0/0` | `4.86`, `50/0/0` | `4.86`, `50/0/0` | `0.00` | `0.00` |
| `improved-v0` | `4.84`, `50/0/0` | `4.86`, `50/0/0` | `4.84`, `50/0/0` | `0.00` | `-0.02` |
| `improved-v2` | `4.68`, `50/0/0` | `4.80`, `50/0/0` | `4.66`, `50/0/0` | `-0.02` | `-0.14` |
| `improved-v3` | `3.08`, `48/1/1` | `4.24`, `49/0/1` | `3.06`, `48/0/2` | `-0.02` | `-1.18` |
| `improved-v4` | `2.56`, `45/2/3` | `3.70`, `48/0/2` | `2.66`, `46/2/2` | `+0.10` | `-1.04` |
| `improved-v5` | `1.20`, `34/7/9` | `2.38`, `43/1/6` | `1.22`, `36/4/10` | `+0.02` | `-1.16` |
| `improved-v6` | `1.22`, `34/7/9` | `2.40`, `43/1/6` | `1.24`, `36/4/10` | `+0.02` | `-1.16` |

## Failure Analysis

The teacher-derived `110` macro is a real lever, but not a solution. On the
short screen, `serve_110_10` improved every hard archived opponent relative to
`net-pressure`, with the biggest gain on `improved-v4`. The same macro
regressed built-in from `0.0625` to `-0.1250`, so the gain is not a clean
promotion signal.

The full fixed-pool check narrowed the result further. `serve_110_10` still
improved `improved-v4`, `improved-v5`, and `improved-v6` relative to
`net-pressure`, but the gains were small (`+0.10`, `+0.02`, `+0.02`) and came
with regressions on built-in, `improved-v2`, and `improved-v3`. It also stayed
far below `baseline-rnn` on the hard archived rows.

This weakens the idea that copying a fixed reset macro from baseline-rnn traces
will close the gap. The RNN advantage likely depends on context-specific rally
setup after reset, not merely the first few reset actions.

## Decision

Do not promote a maintained policy/config/test edit from this pass. Do not open
generation-5 holdout or audit seeds.

The useful next direction is a context-conditioned reset phase, not a fixed
macro: it should decide whether to brace, jump, or pressure based on ball
height, opponent depth, and whether the previous point ended from low defense
or rear-wall recovery.

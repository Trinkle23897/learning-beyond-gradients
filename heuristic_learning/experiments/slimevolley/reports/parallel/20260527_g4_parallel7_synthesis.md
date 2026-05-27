# SlimeVolley Generation-4 Parallel7 Synthesis

Date: 2026-05-27

Type: development-only parallel worker synthesis

## Protocol

Five independent workers ran or reviewed generation-4 development evidence only.
Short screens used fixed seeds `9000..9015`; full checks used fixed seeds
`9000..9049`. No generation-4 holdout seeds `10000..10049`, audit seeds
`11000..11049`, or final-evaluation commands were used.

Before synthesis, the coordinator checked for SlimeVolley processes. One stale
generation-5 probe was found and stopped because it was clearly obsolete for
this generation-4-only pass:

- PID `1877547`: `.venv/bin/python experiments/slimevolley/probes/g5_rollout_mined_rule_probe.py --phase screen --seed-start 12000 --episodes 8`

No generation-4 worker process remained running at synthesis time.

## Comparison Table

| Worker | Family | Type | Seeds | Best candidate | Key score evidence | Fixed-pool outcome | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | `attack` scalar/config search | scalar/config | screen `9000..9015`; full built-in `9000..9049` | `late_vx_m0.40` | full built-in `-0.2800`, W-L-D `7-17-26`, `150000` steps | not run; failed `baseline-rnn` built-in gate `0.1200` | no promotion |
| B | stacked grounded-low-receive probes | structural/history | screen `9000..9015`; full pool `9000..9049` for one candidate | `stacked_low_101_wide` | full built-in `0.0400`, W-L-D `12-10-28`, `150000` steps | small hard-tail gains but built-in regression; still far behind `baseline-rnn` | no promotion |
| C | rear-wall press probes | structural branch | screen `9000..9015`; full pool `9000..9049` for one inert candidate | no behavioral improvement | `rear_wall_release_forward` full built-in `0.1000`, below `baseline-rnn`; `rear_wall_low_brace_nojump` tied references with no action changes | inert candidate exactly matched `post-contact`; active candidates regressed | no promotion |
| D | attack/rally/RNN trace diagnostics | diagnostic analysis only | trace `9000..9015` | diagnostic only | `rally-serve` and `post-contact` each `0.3125`, W-L-D `4-0-12`; `baseline-rnn` `0.1250`, W-L-D `6-4-6` | not benchmark evidence | use only for hypotheses |
| E | archived-opponent robustness | robustness check | fixed pool `9000..9049` | `rally-serve-low-x52` as scalar reference; `post-contact` as structural reference | `rally-serve-low-x52` built-in `0.1800`, W-L-D `14-8-28`; `post-contact` built-in `0.1400`, W-L-D `13-8-29` | both still trail `baseline-rnn` by about `0.78..0.92` on hard archived opponents | no promotion |

## Decision

Do not make a maintained policy, config, or test edit from this parallel7 pass.
The evidence does not support promotion under the stated rules.

The only candidate that improved the full built-in score over the current
registered family was `rally-serve-low-x52`, but it is scalar/config evidence
from the prior parallel6 search and still loses badly to `baseline-rnn` on the
archived heuristic opponent tail. The structural candidates in this pass either
failed the built-in gate, overfit the short screen, regressed archived rows, or
did not change behavior.

## Failure Analysis

The attack threshold search confirmed that local scalar motion around
`late_contact_attack` is not enough. The best row converted one full-dev loss
into a draw but remained far below both `baseline-rnn` and `rally-serve`.

The grounded-low-receive worker found the clearest short-subset overfit:
`stacked_low_101_wide` looked plausible on `9000..9015`, then fell below both
`post-contact` and `baseline-rnn` on the full built-in development range.

The rear-wall branch probes repeated the earlier pattern: active broad retreat
or release rules can help an archived row locally, but the full built-in row or
another archived row pays for it. The only candidate that survived the protocol
was effectively a no-op relative to `post-contact`.

The trace worker still points at `grounded_low_receive` and low recovery as the
remaining failure family, but the tested stacked-frame rewrites are too broad.
The next useful experiment is not a maintained edit; it is a narrower
development-only probe that separates low-left/net states from low-mid-right
states and keeps rear-wall recovery out of the same rule.

## Next Step

Next single policy/config/test edit: none. Evidence does not support a
maintained edit.

Next experiment direction: a dev-only, no-promotion probe for a narrower
`grounded_low_receive` split, using the same generation-4 development seed
protocol and requiring fixed-pool validation before any maintained change.

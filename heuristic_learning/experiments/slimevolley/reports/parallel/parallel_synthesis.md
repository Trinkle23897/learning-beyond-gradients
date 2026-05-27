# Parallel SlimeVolley Development Synthesis

Date: 2026-05-27

## Protocol

All workers used generation-4 development seeds only. Short screens used fixed subset `9000..9015`; full checks used `9000..9049`. No worker used generation-4 holdout seeds `10000..10049` or audit seeds `11000..11049`. No worker promoted a candidate or wrote formal ledger rows.

## Worker Artifacts

| Worker | Artifact | Family | Best built-in result | Label | Promotion recommendation |
| --- | --- | --- | --- | --- | --- |
| Scalar/config search | `experiments/slimevolley/notes/parallel/scalar_attack_search_worker.md` | scalar search around prior scalar `attack` base | `-0.02`, W/L/D `9/12/29`, `150000` steps on `9000..9049` | scalar/config | Do not promote; still below `baseline-rnn` mean `0.12` and built-in-only evidence. |
| Grounded low receive | `experiments/slimevolley/notes/parallel/grounded_low_receive_worker.md` | structural branch probes and scalar trigger variants | short-screen tie only: `-0.125`, W/L/D `2/4/10`, `48000` steps on `9000..9015` | structural plus scalar/config probes | Do not promote; no short-screen improvement. |
| Rear wall | `experiments/slimevolley/notes/parallel/rear_wall_worker.md` | rear_wall_press / rear-wall losses | full-check tie only: `-0.30`, W/L/D `7/18/25` or `7/19/24`, `150000` steps | structural plus scalar/config probes | Do not promote; no improvement over `attack`. |
| Attack vs RNN traces | `experiments/slimevolley/reports/parallel/trace_attack_vs_rnn_worker.md` | trace diagnostics | `attack -0.30` vs `baseline-rnn 0.12`, both `150000` steps on `9000..9049` | diagnostics only | Do not promote; identifies low-left/net and low own-side failures. |
| Archived-opponent robustness | `experiments/slimevolley/notes/parallel/robustness_worker.md` | fixed dev opponent-pool robustness | prior scalar candidate `-0.10` on built-in but worse/tied on every non-built-in opponent | scalar/config plus structural comparison | Do not promote; built-in-specific and non-robust. |

## Quantitative Decision

| Candidate | Built-in dev mean | Built-in W/L/D | Fixed-pool robustness evidence | Beats `baseline-rnn` built-in mean `0.12`? | Decision |
| --- | ---: | --- | --- | --- | --- |
| `improved-tuned` v2 | -0.44 | 6/23/21 | Stronger than current `improved` across fixed pool, but scalar/config only | No | Keep as scalar/config baseline. |
| `attack` | -0.30 | 7/18/25 | Improves several opponents but regresses `improved-v5` and `improved-v6` | No | Keep as partial structural candidate. |
| Prior scalar attack base | -0.10 | 11/13/26 | Worse or tied on every non-built-in opponent checked | No | Do not promote. |
| New scalar search top: `low_ball_rescue_x_window=0.48` | -0.02 | 9/12/29 | Not checked on fixed pool because it does not beat RNN and is scalar-only | No | Do not promote. |
| Grounded/rear-wall structural probes | <= -0.30 full or no short-screen improvement | no improvement | No robustness trigger | No | Do not promote. |

## Failure Analysis

The parallel pass did not find a heuristic candidate that beats the packaged `baseline-rnn` comparator on built-in generation-4 development seeds. The best scalar candidate narrowed the built-in gap to `0.14`, but the improvement mostly reduced losses into draws and came from a scalar threshold (`low_ball_rescue_x_window=0.48`), not a structural policy change.

The structural branch probes were negative. Direct `grounded_low_receive` changes were sparse or harmful, and broadening low-ball jump suppression removed useful contacts. Rear-wall probes either tied the current `attack` score or made low-far-right losses worse. Trace diagnostics continue to point at low-left/net and low own-side floor-height returns as unresolved, but no tested branch-level rule solved them.

The archived-opponent worker confirmed the important anti-cheating point: built-in-only gains are not enough. The prior scalar attack candidate improved built-in score but regressed or tied every non-built-in opponent. The new scalar candidate should be treated with the same skepticism until it beats the RNN and passes fixed-pool checks; currently it does neither.

## Next Edit Decision

No policy or scalar/config promotion is supported. The only justified edit from this pass is an auditability/test edit: preserve branch-level diagnostics in the transparent heuristic and add a regression test that the `attack` policy records its `late_contact_attack` diagnostic mode on a golden state. This improves future trace interpretation without changing policy behavior or claiming performance progress.

Generation-4 holdout and audit seeds remain sealed.

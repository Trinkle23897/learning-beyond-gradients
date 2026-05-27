# SlimeVolley Generation-4 Parallel6 Synthesis

Date: 2026-05-27

Type: development-only parallel worker synthesis

## Protocol

Five independent workers ran against generation-4 development seeds only. Short
screens used `9000..9015`; full checks used `9000..9049`. No holdout seeds
`10000..10049`, audit seeds `11000..11049`, or final-evaluation commands were
used. The coordinator found no active stale SlimeVolley process before launch
and stopped nothing.

## Comparison Table

| Worker | Family | Type | Seeds | Best candidate | Key score evidence | Fixed-pool outcome | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | rally-serve scalar/config search | scalar/config | screen `9000..9015`; full and pool `9000..9049` | `low_x_0.52` | built-in full dev `0.1800`, W-L-D `14-8-28`, `150000` steps | no obvious regression versus `rally-serve`; still trails `baseline-rnn` on hard archived rows | add as dev-only named scalar candidate; do not claim structural progress |
| B | grounded-low-receive stacked-history probes | structural/history | screen `9000..9015`; full and pool `9000..9049` | no promotable variant | selected probes tied built-in `0.1400`, W-L-D `13-8-29`, `150000` steps | exactly matched `rally-serve` across fixed pool and trailed `baseline-rnn` | no promotion |
| C | rear-wall press probes | structural branch | screen `9000..9015`; full and pool `9000..9049` | `rw_press_grounded_bypass_jump_suppress` | built-in full dev `0.1600`, W-L-D `13-8-29`, `150000` steps | regressed most archived opponents, including added losses on `improved-v3` and `improved-v4` | no promotion |
| D | attack/rally-serve/RNN traces | diagnostics | trace `9000..9015` | diagnostic only | `rally-serve 0.3125`, `4-0-12`; `baseline-rnn 0.1250`, `6-4-6` | not benchmark evidence | use only for hypotheses |
| E | archived-opponent robustness | robustness diagnostics | fixed pool `9000..9049` | `post-contact` as best registered reference | preserves built-in `0.1400`; improves hard tail by `+0.06` versus `rally-serve` | still trails `baseline-rnn` by roughly `0.80..0.90` on hard archived rows | no promotion |

## Decision

The only supported edit is a narrow scalar/config candidate: preserve the
historical `rally-serve` policy unchanged and add a separate development-only
`rally-serve-low-x52` policy name whose only scalar delta is
`low_ball_rescue_x_window=0.52`.

This is not a structural heuristic improvement and not final evidence. It is
worth adding as an auditable candidate because it passed the required fixed
development opponent-pool check after beating `baseline-rnn` and current
`rally-serve` on built-in development seeds. It must not be evaluated on
generation-4 holdout or audit seeds as a tuning action.

## Failure Analysis

The structural probes did not produce a robust branch change. The GLR variants
changed too few decisive frames and tied the reference across the fixed pool.
The rear-wall variant repeated a known pattern: small built-in improvement with
archived-opponent regression. Trace diagnostics show the heuristic family still
uses far fewer jump-heavy conversion actions than the RNN comparator.

The scalar candidate improves the development matrix but weakens the central
heuristic-learning claim if treated as progress by itself. It should be
reported separately from structural policy evolution.

## Next Edit

Add `rally-serve-low-x52` as a named scalar/config candidate, add a focused
sanity test for its config labels, regenerate reports, and run the SlimeVolley
test/audit/report verification commands. No holdout or audit evaluation should
be run.

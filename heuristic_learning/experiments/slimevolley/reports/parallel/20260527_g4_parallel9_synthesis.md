# SlimeVolley Generation-4 Parallel9 Synthesis

Date: 2026-05-27

Type: development-only parallel worker synthesis

## Protocol

Five independent workers ran generation-4 development-only probes or
diagnostics. Short screens used fixed seeds `9000..9015`; full checks used
fixed seeds `9000..9049`. No generation-4 holdout seeds `10000..10049`, audit
seeds `11000..11049`, or final-evaluation commands were used.

Before worker launch, the coordinator checked for active SlimeVolley or
heuristic-learning experiment processes and found none. During the run, the
only visible matching process was the active parallel9 rear-wall worker.

## Comparison Table

| Worker | Family | Type | Seeds | Best candidate | Key score evidence | Fixed-pool outcome | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | `attack` scalar/config search | scalar/config | screen `9000..9015`; full built-in `9000..9049` | `rank1_builtin_combo` | short built-in `0.1875`, W-L-D `4-1-11`; full built-in `-0.1000`, W-L-D `11-13-26`, `150000` steps | not triggered because it did not beat `baseline-rnn` full built-in `0.1200` | no promotion |
| B | stacked `grounded_low_receive` | structural/history | screen `9000..9015` | none; all candidates tied | `parallel9_narrow_low_net_101`, `parallel9_narrow_low_net_110`, and `parallel9_split_front_rear_mode_gated` exactly tied `post_contact_reference` on built-in and `improved-v4/v5/v6` | no full-pool expansion; no screen-row improvement | no promotion |
| C | `rear_wall_press` / rear-wall losses | structural branch | screen `9000..9015`; full built-in/fixed pool `9000..9049` | `rw_press_release_home` on short screen only | short `improved-v4` nudge from `2.7500` to `2.8125`; full built-in fell to `0.1200`, tying `baseline-rnn` but below `post_contact_reference` `0.1400` | rear-wall low-jump rewrites tied hard rows; press variants were inert or regressed built-in | no promotion |
| D | `attack` vs `baseline-rnn` trace | diagnostic only | trace `9000..9015` | diagnostic only | `attack` mean `-0.1250`, W-L-D `2-4-10`; `baseline-rnn` mean `0.1250`, W-L-D `6-4-6`; both `48000` steps | not promotion evidence; confirms `attack` never emits `110/111` and trails on low own-side conversions | no promotion |
| E | archived-opponent robustness | robustness synthesis | fixed pool `9000..9049` from existing dev artifacts | `rally-serve-low-x52` scalar reference; `post-contact` structural reference | `rally-serve-low-x52` built-in `0.18`; `post-contact` built-in `0.14` | both trail `baseline-rnn` on hard archived opponents `improved-v3..v6` by roughly `0.78..0.90` mean | no promotion |

## Decision

Do not make a maintained policy, config, or regression-test edit from this
parallel9 pass. The evidence does not support a single candidate promotion.

No candidate should be promoted based only on built-in opponent score. Worker A
found a short-screen scalar/config row that looked promising, but it regressed
on the full built-in development range. Worker C found a small short-screen
rear-wall nudge, but the full development check either tied or regressed. Worker
B's stacked-frame structural branches fired but did not move outcomes. Worker E
keeps the fixed-pool gap explicit: the strongest current transparent
generation-4 references still trail `baseline-rnn` on the archived hard tail.

## Failure Analysis

The local action-swap direction is near exhaustion for generation-4. Narrow
low-net `101` and `110` rewrites, rear-wall braces, delayed jumps, and
release-home substitutions all changed too few outcome-critical frames or
traded one row for another.

Scalar/config tuning around `attack` can recover part of the built-in gap, but
it remains unstable under the full development seed range and does not clear
the neural comparator. The short-screen-to-full-screen reversal on
`rank1_builtin_combo` is the central anti-overfitting warning from this pass.

Trace diagnostics still point to a real behavioral gap: the RNN uses heavy
`101`/`110` action mass for low near-net conversion, while `attack` remains
movement-heavy and never emits `110` or `111`. The tested structural branches
did not turn that observation into robust score gains.

## Next Single Edit

No maintained policy/config/test edit is supported by this pass.

The only supported repository edit is documentation/report synthesis of the
parallel9 evidence. Any next experiment should avoid another local
single-frame action substitution on generation-4 and should either use a fresh
development protocol or test a broader interpretable state machine for
multi-frame post-contact setup before considering any held-out seeds.

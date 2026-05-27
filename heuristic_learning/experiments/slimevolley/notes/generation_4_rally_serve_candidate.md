# Generation-4 Rally-Serve Candidate

Date: 2026-05-27

## Protocol

This candidate used generation-4 development seeds only:

- Short screens: fixed subset `9000..9015`.
- Full development validation: `9000..9049`.
- Fixed development opponent pool: `builtin`, `random`, `initial`, `improved-v0`, `improved-v2`, `improved-v3`, `improved-v4`, `improved-v5`, `improved-v6`.
- No generation-4 holdout seeds `10000..10049` were used.
- No generation-4 audit seeds `11000..11049` were used.

## Candidate Definition

Policy name: `rally-serve`.

The candidate starts from the `attack` candidate and adds a structural
point-reset serve detector. Earlier policies only used their serve macro during
the first few episode steps; SlimeVolley resets the ball after each point, so
later rallies can enter a serve-like state without the policy re-entering serve
mode.

Structural rule:

- If `abs(ball_x) <= 0.28`, `ball_y >= 1.45`, `abs(ball_vx) <= 0.50`, and the
  last detection was more than `12` policy steps ago, enter `rally_serve` mode.
- For `8` steps, return forward+jump action `101`.

Scalar/config fields layered on the structural rule:

- `high_arc_horizon = 0.95`
- `grounded_low_receive_airborne_margin = 0.16`
- `late_attack_vx = -0.45`
- `landing_horizon = 0.38`
- `late_attack_vy = -0.35`
- `late_attack_y_min = 0.24`
- `low_ball_rescue_x_window = 0.54`
- `overcommit_guard_x = 0.18`

Label: structural policy improvement plus scalar/config tuning. The structural
component is the rally-serve detector; the final score also depends on scalar
fields selected on development seeds.

## Development Results

Built-in opponent comparison on `9000..9049`:

| Policy | Mean | W/L/D | Steps | Status |
| --- | ---: | --- | ---: | --- |
| `baseline-rnn` | `0.12` | `18/12/20` | `150000` | neural comparator |
| `attack` with prior scalar top | `-0.02` | `9/12/29` | `150000` | prior best scalar/structural scratch result |
| `rally-serve` | `0.14` | `13/8/29` | `150000` | beats built-in dev comparator by `0.02` |

The improvement over the RNN is small but positive on the fixed development
range. This is not a final claim because holdout and audit are still sealed.

## Fixed Development Opponent Pool

| Opponent | Mean | W/L/D | Steps |
| --- | ---: | --- | ---: |
| `builtin` | `0.14` | `13/8/29` | `150000` |
| `random` | `4.74` | `50/0/0` | `38217` |
| `initial` | `4.68` | `50/0/0` | `44634` |
| `improved-v0` | `4.70` | `50/0/0` | `43242` |
| `improved-v2` | `4.38` | `49/1/0` | `76391` |
| `improved-v3` | `2.98` | `48/0/2` | `138122` |
| `improved-v4` | `2.34` | `44/0/6` | `143814` |
| `improved-v5` | `1.16` | `32/7/11` | `149716` |
| `improved-v6` | `1.22` | `32/7/11` | `149716` |

Known regression: versus the scalar `improved-tuned` baseline, `rally-serve`
slightly regresses `improved-v5` (`1.16` versus `1.22`) while tying or improving
the other logged comparison points relevant to the candidate. This regression is
recorded and should be considered before any final claim.

## Search and Cost Notes

- Broad macro-policy screen was stopped as obsolete because it was too large and
  produced no useful intermediate output.
- A bounded macro-policy screen showed naive fixed schedules were much worse
  than `attack`.
- A bounded per-point serve-detector screen found `0.08` mean on `9000..9049`.
- A small scalar/config follow-up around the serve detector found the `0.14`
  candidate.
- Formal ledger rows were appended after tests passed.

## Decision

Freeze `rally-serve` as the current generation-4 development candidate. It is
the first transparent heuristic candidate in this SlimeVolley generation to beat
the packaged `baseline-rnn` on built-in development seeds.

Do not tune it further on holdout or audit seeds. The next valid step is a
predeclared final evaluation if the reviewer accepts opening the sealed final
range. Until that happens, the evidence supports development progress but does
not prove final generalization.

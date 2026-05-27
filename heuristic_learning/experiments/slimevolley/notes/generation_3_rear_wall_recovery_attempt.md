# Generation-3 Rear-Wall Recovery Attempt

Status: rolled back after development-seed evidence.

## Diagnosis

Generation-3 built-in-opponent traces on dev seeds `6000..6049` showed most point losses ending with a low, descending ball near the rear wall while the agent was already airborne. The attempted structural hypothesis was that a `rear_wall_recovery` mode could move the agent off the rear wall and suppress late airborne jumps.

## Change

The current `improved` policy was first archived as `improved-v3`. Then a `rear_wall_recovery` structural branch was added to the current policy. The branch targeted low far-right balls and moved toward a safer interior x-position while avoiding another jump if the agent was already above the ball.

## Development Evidence

- Pre-change `improved` vs `builtin`, generation-3 dev seeds `6000..6049`: mean `-4.24`, W/L/D `0/49/1`.
- Post-change `improved` vs `builtin`, generation-3 dev seeds `6000..6049`: mean `-4.24`, W/L/D `0/49/1`.
- Post-change round-robin with `improved-v3` included: `improved-v3` mean `2.402857`; current `improved` mean `2.397143`.

## Decision

The attempt did not improve the built-in-opponent score and slightly underperformed the archived predecessor in the development round-robin. The behavioral branch was therefore rolled back. The failed attempt remains visible in `generation_3_trials.jsonl`; the `improved-v3` archive remains available as a frozen predecessor for future regression checks.

## Next Hypothesis

The built-in gap is probably not solved by a late low-ball rear-wall guard. The next structural attempt should target earlier serve/return shaping or a higher-level built-in-opponent defense mode, and should be evaluated only on generation-3 development seeds until policy, scalar config, tests, and opponent pool are frozen.

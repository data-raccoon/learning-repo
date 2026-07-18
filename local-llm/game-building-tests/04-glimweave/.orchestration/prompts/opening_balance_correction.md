Correct the opening-economy implementation without changing global capacity contracts.
Work only in these exact values across the listed files:

- `data/game-data.json`: restore `baseReservoirCapacity` to 100; set Glimspinner baseCost
  to 45 and Driftcatcher baseCost to 55.
- `data/game-data.js`: make the same three runtime values match the JSON.
- `src/state.js`: change the fresh and post-Retuning priming Reservoir from 135 to 100,
  and change the fresh cumulative captured seed from 135 to 100 so validation remains true.

Do not read whole files. Use targeted reads/grep for only these literals, then edit on the
next turn. Preserve all other data and logic. This yields one deliberate 100-Glim Sky Loom
priming charge that can buy exactly one producer plus one capturer while retaining the
original capacity, upgrade, and Retuning capacity semantics.

Verify JSON parse, matching JSON/runtime values, and all affected state literals. Return
exactly three Markdown bullets: values, files, verification. Do not commit.

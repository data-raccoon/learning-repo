Fix one verified boot failure in `game-building-tests/04-glimweave/data/game-data.js`.
The browser loads this JavaScript artifact, while the previous economy repair changed
`data/game-data.json` baseReservoirCapacity from 100 to 150. Fresh state now starts at 135,
but runtime data still caps it at 100, causing `STATE_VALIDATION_FAILED` during boot.

Read only the beginning/constants region of `game-data.js`, then edit the runtime
`baseReservoirCapacity` to match the authoritative JSON value 150. Do not change any other
balance or generated data. Verify the relevant value in both files and perform a basic JS
syntax/brace check. Return exactly two Markdown bullets: change and verification. Do not
commit.

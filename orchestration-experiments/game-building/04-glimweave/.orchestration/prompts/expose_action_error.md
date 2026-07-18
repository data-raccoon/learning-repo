In `04-glimweave/smoke.js`, make one diagnostic edit only. In the branch
where final Reservoir is not zero, read `#announcer` text and append a sanitized uppercase
version (non-word runs replaced by underscores, capped at 140 characters) directly to the
failure code as `ACTION_MESSAGE_<text>`. Keep the numeric Reservoir failure and every gate.

Use a targeted read and edit, then run the verifier. Return only its exact output. Do not
touch production files or commit.

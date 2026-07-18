Append one compact CSS override block to
`game-building-tests/04-glimweave/styles.css` and do nothing else.

This task explicitly overrides Vibe's read-before-edit and end-to-end-read defaults. The
stylesheet has already been externally verified as the intact committed 705-line file.
Do not read it, grep it, inspect Git, or run exploratory commands. Immediately use one
`bash` call with a quoted heredoc (`cat >> ... <<'EOF'`) to append the override, then use at
most one bash verification call.

The appended CSS must implement all of the following using existing selectors:

- `#gameCanvas { pointer-events: none; }`
- desktop `.main-panels`: three columns consisting of a bounded left rail, a flexible
  central open field of at least 320px when space permits, and a bounded right rail;
- `.left-column` explicitly occupies column 1 and `.right-column` column 3;
- the UI/container may span the page, but the middle grid track must contain no opaque
  panel and must visibly expose the canvas;
- below 760px: `#gameShell` permits vertical scrolling; `#gameCanvas` becomes an absolute
  top playfield band around 38-42dvh with a sensible 260px minimum; `#uiRoot` gets matching
  top padding so controls begin below that band; `.main-panels` becomes one column and both
  side columns return to automatic placement;
- below 420px: reduce safe horizontal padding/gaps without shrinking the field band away;
- do not override component colors, focus, phase backgrounds, or reduced-motion rules.

Use a clearly labeled comment such as `PLAYFIELD LAYOUT OVERRIDES`. Ensure braces balance.
Verification is limited to line count greater than 705, tail output showing the complete
block, and a brace-count check. Return a two-bullet Markdown summary. Do not commit.

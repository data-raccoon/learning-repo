Repair Glimweave's playfield/control layout in
`04-glimweave/styles.css` only. Read the file once, then edit it on a
following turn. Do not change JavaScript or game balance.

The canvas currently fills the shell at z-index 1 while a full-width UI at z-index 10 uses
a two-column `280px 1fr` grid. The second control column consumes the remainder, leaving no
recognizable playfield. The pre-repair 1440x900 screenshot therefore appears to be only a
dashboard.

Re-architect CSS so:

- at desktop widths, the left and right control columns occupy bounded side rails and a
  large, unmistakable central field remains visually open to the canvas;
- the top status bar can span the viewport without hiding the field below it;
- panels remain readable but do not form an opaque full-page blanket;
- the canvas receives no pointer input and controls retain normal pointer/focus behavior;
- at about 360x800, a materially sized playfield band is explicitly reserved above or
  between stacked controls rather than being covered by them;
- the page can scroll on constrained heights without clipping settings, purchases, or
  safe-area padding;
- focus visibility and reduced-motion rules remain intact;
- existing phase canvas backgrounds and visual identity are preserved.

Use clear grid placement for `.left-column` and `.right-column`; do not depend on an empty
DOM placeholder. Add responsive breakpoints as needed. Avoid fixed pixel assumptions that
only work at 1440x900.

After editing, inspect the desktop and mobile rules for contradictions and run a CSS/basic
brace validation if available. Return only a concise Markdown report of layout geometry,
breakpoints, and verification. Do not claim a post-repair screenshot and do not commit.

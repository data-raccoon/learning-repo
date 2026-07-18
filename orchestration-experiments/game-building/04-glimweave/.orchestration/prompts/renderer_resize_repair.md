Fix canvas sizing in `04-glimweave/src/render.js` only. This localized
task overrides end-to-end reading: read approximately lines 1-70, then edit on the next
turn.

Current `init` calls `resize(canvas.width, canvas.height)`, which uses default HTML backing
attributes rather than the canvas's displayed CSS geometry. `resize` also mixes CSS sizes,
device-pixel sizes, and repeated transforms. Implement a coherent DPR-aware approach:

- measure the rendered canvas using `getBoundingClientRect()` or client dimensions;
- keep logical `width`/`height` in CSS pixels;
- set backing dimensions to logical size times current devicePixelRatio, with sensible
  existing caps;
- establish the transform without accumulating scale on repeated resize;
- respond to viewport/container resizing, preferably with `ResizeObserver` plus a window
  fallback, and avoid needless reallocation when dimensions are unchanged;
- retain the existing public Renderer API and rendering coordinate semantics.

Do not change drawing art, simulation, layout CSS, or test fixtures. Inspect the changed
region and run the best available syntax check. Return only a concise Markdown report with
behavior and verification. Do not commit.

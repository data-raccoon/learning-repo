## Fix: DPR-aware canvas resize in `src/render.js`

**Behavior:**
- `init` now measures actual rendered size via `getBoundingClientRect()` instead of default HTML attributes
- `resize` resets transform with `setTransform(1,0,0,1,0,0)` before applying DPR scale to prevent accumulation
- Added `ResizeObserver` on canvas with `window.resize` fallback
- Early-exit in `resize` when dimensions unchanged, avoiding needless reallocation

**Verification:**
- Basic syntax validation passed (balanced braces/brackets/parens)
- Public API unchanged: `init`, `resize`, `setReducedMotion`, `setColorblindMode` preserved

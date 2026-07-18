# Kebab-Case Tic-Tac-Toe

## Title
**Kebab-Case Tic-Tac-Toe**
*(Center-Start Variant)*

## Core Loop
Players take turns marking **X** or **O** in a 3x3 grid. The first to complete a horizontal, vertical, or diagonal line wins. The center cell is initially locked to encourage strategy.

## Controls
- **Keyboard**:
  - `W` (X) or `S` (O) to place a mark in the center.
  - `E` to restart.
- **Mouse**: Click any cell to place a mark.

## Rules
1. Players alternate turns, starting with **X**.
2. Only the center cell is available initially.
3. No cell can be reused.
4. Game ends when a player wins, the grid is full, or the player presses `E` to restart.

## Scoring
- **Win**: +1 point per game.
- **Tie**: 0 points.
- **Restart**: No points deducted.

## Win/Lose/Restart States
- **Win**: A player completes a line (horizontal, vertical, or diagonal).
- **Lose**: Grid is full with no winner.
- **Restart**: Player presses `E` to reset.

## Visual Style
- Minimalist 3x3 grid with numbered cells (1–9).
- Bold `X`/`O` symbols.
- Center cell highlighted on hover/click.
- Score displayed top-right.

## File Plan
- **HTML**: `index.html` (logic + UI).
- **CSS**: `style.css` (styling).
- **JavaScript**: `game.js` (state management).
- **Optional**: `README.md` (instructions).

## Objective
Create a self-contained, strategic Tic-Tac-Toe variant with polished UI and no dependencies. Focus on:
- Turn-based play with center-lock.
- Intuitive controls (keyboard/mouse).
- Clear visual feedback.

## Acceptance Criteria
1. Game runs offline in a single HTML file.
2. Keyboard/mouse controls work as specified.
3. Rules and win conditions enforced.
4. Visual feedback (e.g., win messages, score updates).
5. Restart works seamlessly.
6. No external dependencies.
7. Code is modular and well-commented.

---
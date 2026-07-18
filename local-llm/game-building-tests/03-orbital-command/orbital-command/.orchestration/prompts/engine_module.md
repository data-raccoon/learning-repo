Implement `src/engine.js` for the supplied contract and runtime data. Return JavaScript
only without Markdown fences. Use an IIFE and expose `OC.Engine` as a class.

Constructor: `new OC.Engine(data, state)` stores both. Public methods:
`canBuild(id)`, `build(id)`, `canResearch(id)`, `research(id)`,
`assignCrew(role, delta)`, `chooseEvent(choiceIndex)`, `advanceTurn()`, and `snapshot()`.

Rules:
- build checks costs and required technology, deducts costs, appends module id, logs it;
- research selects an available incomplete technology and resets researchProgress;
- crew assignments stay nonnegative and their total equals world.crew_total;
- advanceTurn does nothing when an event is pending or status is not playing;
- each built module adds its production; engineering crew adds floor(count/3) energy,
  science crew adds floor(count/3) science, operations adds floor(count/4) credits;
- active research gains science crew + 2 progress and completes at its cost;
- clamp all resources to at least zero and morale to at most 100;
- on every third turn, select deterministically `events[(turn/3-1) % events.length]` when
  its min_turn is met, storing it as pendingEvent;
- chooseEvent applies every listed resource effect, logs the choice, clears pendingEvent;
- completed tech effects apply as bonuses during production; unlock effects only unlock;
- update zeroStreak; lose after energy or morale is zero for two consecutive turns;
- win when every mission goal resource reaches its target;
- snapshot returns a deep copy. Do not save automatically and do not access the DOM.

(function () {
  if (!new URLSearchParams(location.search).has('smoke')) return;
  addEventListener('DOMContentLoaded', () => setTimeout(() => {
    const failures = [];
    const check = (value, code) => { if (!value) failures.push(code); };
    let phase = 'BOOT';
    try {
      const test = window.__orbitalTest;
      check(Boolean(test && test.engine && test.render && test.newGame), 'TEST_API');
      if (!test) {
        (window.__bootErrors || []).slice(0, 3).forEach(item => failures.push(item));
        throw new Error('MissingTestAPI');
      }
      const engine = test.engine;
      const initial = engine.snapshot();
      check(initial.turn === 1 && initial.status === 'playing', 'INITIAL_STATE');
      check(Object.values(initial.crew).reduce((a, b) => a + b, 0) === OC_DATA.world.crew_total, 'CREW_TOTAL');

      phase = 'BUILD';
      const module = OC_DATA.modules.find(item => engine.canBuild(item.id));
      check(Boolean(module), 'AFFORDABLE_MODULE');
      const moduleCount = engine.state.modules.length;
      if (module) engine.build(module.id);
      check(engine.state.modules.length === moduleCount + 1, 'BUILD');

      phase = 'RESEARCH';
      const technology = OC_DATA.technologies.find(item => engine.canResearch(item.id));
      check(Boolean(technology), 'AVAILABLE_RESEARCH');
      if (technology) engine.research(technology.id);
      check(engine.state.activeResearch === technology?.id, 'RESEARCH');

      phase = 'CREW';
      const totalBefore = Object.values(engine.state.crew).reduce((a, b) => a + b, 0);
      engine.assignCrew('operations', -1);
      engine.assignCrew('engineering', 1);
      check(Object.values(engine.state.crew).reduce((a, b) => a + b, 0) === totalBefore, 'CREW_REASSIGN');

      phase = 'TURN';
      const turnBefore = engine.state.turn;
      engine.advanceTurn();
      check(engine.state.turn === turnBefore + 1, 'ADVANCE_TURN');

      phase = 'PERSISTENCE';
      OC.saveState(engine.state);
      const loaded = OC.loadState(OC_DATA);
      check(loaded.turn === engine.state.turn && loaded.modules.length === engine.state.modules.length, 'SAVE_LOAD');

      phase = 'RENDER';
      test.render();
      check(document.querySelector('#module-list').children.length === OC_DATA.modules.length, 'MODULE_UI');
      check(document.querySelector('#tech-list').children.length === OC_DATA.technologies.length, 'TECH_UI');
      check(document.querySelector('#crew-list').children.length === OC_DATA.world.roles.length, 'CREW_UI');
      check(document.querySelector('#mission-list').children.length === OC_DATA.world.mission_goals.length, 'MISSION_UI');

      phase = 'RESET';
      const fresh = test.newGame();
      check(Boolean(fresh && fresh.state && fresh.state.turn === 1), 'NEW_GAME');
      check(document.querySelector('#announcer').getAttribute('aria-live') === 'polite', 'ARIA_LIVE');
    } catch (error) {
      failures.push('RUNTIME_' + phase + '_' + error.name + '_' + String(error.message || '').slice(0, 80).replace(/\W+/g, '_').toUpperCase());
    }
    const result = document.querySelector('#smoke-result') || document.body.appendChild(document.createElement('output'));
    result.id = 'smoke-result';
    result.textContent = failures.length ? 'FAIL:' + failures.join(',') : 'PASS';
  }, 50));
})();

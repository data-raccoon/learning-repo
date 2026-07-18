(function () {
  if (!new URLSearchParams(location.search).has('smoke')) return;
  window.addEventListener('load', function () {
    window.setTimeout(function () {
      var failures = [], phase = 'BOOT';
      function check(value, code) { if (!value) failures.push(code); }
      try {
        check(window.__glimweaveBootErrors.length === 0, window.__glimweaveBootErrors[0] || 'BOOT_ERROR');
        check(!!(window.GW && GW.Utils && GW.State && GW.Simulation && GW.Renderer && GW.UI), 'MODULES');
        var test = window.__glimweaveTest;
        check(!!test, 'TEST_API');
        if (!test) throw new Error('MissingTestAPI');
        phase = 'STATE';
        var state = test.createState(12345);
        check(!!state && test.validateState(state), 'VALID_INITIAL_STATE');
        check(test.assertStateInvariants(state) !== false, 'INITIAL_INVARIANTS');
        phase = 'DATA';
        check(Object.keys(GW_DATA.weftlingTypes).length === 5, 'FIVE_CLASSES');
        check(Object.keys(GW_DATA.globalUpgrades).length >= 18, 'UPGRADE_COUNT');
        check(Object.keys(GW_DATA.doctrines).length === 3, 'DOCTRINE_COUNT');
        phase = 'INTEGRATION';
        check(window.GW && GW.Integration && GW.Integration.installed === true, 'INTEGRATION_INSTALLED');
        check(Object.keys(GW_DATA.doctrines).length === 3, 'INTEGRATION_DOCTRINE_KEYS');
        var intState1 = test.createState(12345);
        var intResult1 = GW.Simulation.handleAction(intState1, {type:'CHOOSE_DOCTRINE', doctrineId:'LUMINANCE'});
        check(intResult1 === intState1, 'INTEGRATION_CHOOSE_IDENTICAL');
        check(intState1.upgrades.doctrine === 'Luminance', 'INTEGRATION_DOCTRINE_VALUE');
        check(test.validateState(intState1), 'INTEGRATION_CHOOSE_VALID');
        var intDoctrineRejected = false;
        try {
          GW.Simulation.handleAction(intState1, {type:'CHOOSE_DOCTRINE', doctrineId:'CAPTIVATION'});
        } catch (e) {
          intDoctrineRejected = true;
        }
        check(intDoctrineRejected, 'INTEGRATION_DOCTRINE_REJECT');
        var intState2 = test.createState(12345);
        intState2.iridescence = 3;
        check(test.validateState(intState2), 'INTEGRATION_BUY_INITIAL_VALID');
        var intResult2 = GW.Simulation.handleAction(intState2, {type:'BUY_UPGRADE', upgradeId:'ReservoirBlueprint'});
        check(intResult2 === intState2, 'INTEGRATION_BUY_IDENTICAL');
        check(intState2.iridescence === 1, 'INTEGRATION_BUY_IRIDESCENCE');
        check(intState2.permanentUpgrades && intState2.permanentUpgrades.length === 1 && intState2.permanentUpgrades[0] === 'ReservoirBlueprint', 'INTEGRATION_BUY_OWNED');
        check(intState2.maxCapacity === 200, 'INTEGRATION_BUY_CAPACITY');
        check(test.validateState(intState2), 'INTEGRATION_BUY_VALID');
        intState2.phase = 2;
        intState2.highestPhaseUnlocked = 2;
        intState2.totalGlimCaptured = 1000;
        intState2.totalGlimCapturedThisRun = 1000;
        check(test.validateState(intState2), 'INTEGRATION_RETUNE_INITIAL_VALID');
        var intResult3 = GW.Simulation.handleAction(intState2, {type:'RETUNE'});
        check(intResult3 && intResult3.success === true, 'INTEGRATION_RETUNE_SUCCESS');
        check(intResult3 && intResult3.iridescenceGained > 0, 'INTEGRATION_RETUNE_GAIN');
        check(intState2.phase === 1, 'INTEGRATION_RETUNE_PHASE');
        check(intState2.maxCapacity === 200, 'INTEGRATION_RETUNE_CAPACITY');
        check(intState2.reservoir <= intState2.maxCapacity, 'INTEGRATION_RETUNE_RESERVOIR');
        check(intState2.permanentUpgrades && intState2.permanentUpgrades.length === 1 && intState2.permanentUpgrades[0] === 'ReservoirBlueprint', 'INTEGRATION_RETUNE_BLUEPRINT');
        check(test.validateState(intState2), 'INTEGRATION_RETUNE_VALID');
        phase = 'ECONOMY';
        check(test.testProductionCaptureIndependence() === true, 'PRODUCTION_CAPTURE');
        check(test.testFadeImpact() === true, 'FADE');
        check(test.testOverflow() === true, 'OVERFLOW');
        check(test.testUnitPurchase() === true, 'UNIT_PURCHASE');
        check(test.testUpgradePurchase() === true, 'UPGRADE_PURCHASE');
        phase = 'PROGRESSION';
        check(test.testDoctrineLock() === true, 'DOCTRINE_LOCK');
        check(test.testPhaseProgression() === true, 'PHASE_PROGRESSION');
        check(test.testRetuning() === true, 'RETUNING');
        check(test.testVictory() === true, 'VICTORY');
        phase = 'PERSISTENCE';
        check(test.testOfflineProgress() === true, 'OFFLINE_PROGRESS');
        check(test.testSaveLoad() === true, 'SAVE_LOAD');
        phase = 'UI';
        check(document.querySelector('#uiRoot').children.length > 0, 'UI_RENDERED');
        check(document.querySelector('#gameCanvas').width > 0, 'CANVAS_READY');
        check(document.querySelector('#announcer').getAttribute('aria-live') === 'polite', 'ARIA_LIVE');
        check(getComputedStyle(document.body).backgroundColor !== '', 'CSS_LOADED');
      } catch (error) {
        var trace = String(error.stack || '').split('\n').slice(1, 4).join('_').slice(0, 220).replace(/\W+/g, '_').toUpperCase();
        failures.push('RUNTIME_' + phase + '_' + error.name + '_' + String(error.message || '').slice(0, 320).replace(/\W+/g, '_').toUpperCase() + '_' + trace);
      }
      var output = document.querySelector('#smoke-result');
      output.textContent = failures.length ? 'FAIL:' + failures.join(',') : 'PASS';
    }, 150);
  });
})();

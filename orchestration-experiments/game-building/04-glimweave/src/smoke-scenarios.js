(function() {
  'use strict';
  if (!new URLSearchParams(location.search).has('smoke')) return;
  if (typeof window.__glimweaveTest === 'undefined') return;
  var test = window.__glimweaveTest;
  var DATA = window.GW_DATA;

  function fundState(state, target) {
    if (target > state.maxCapacity) {
      throw new Error('fundState: target ' + target + ' exceeds maxCapacity ' + state.maxCapacity);
    }
    state.reservoir = target;
    if (state.totalGlimCaptured < target) {
      state.totalGlimCaptured = target;
    }
    if (state.totalGlimCapturedThisRun < target) {
      state.totalGlimCapturedThisRun = target;
    }
    test.assertStateInvariants(state);
    return state;
  }

  test.testProductionCaptureIndependence = function() {
    var state = test.createState(42);
    fundState(state, 100);
    test.buyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    fundState(state, 100);
    test.buyWeftling(state, DATA.weftlingTypes.DRIFTCATCHER, 100, 100);
    return test.getProductionRate(state) > 0 && test.getCaptureRate(state) > 0;
  };

  test.testFadeImpact = function() {
    var state = test.createState(42);
    fundState(state, 100);
    test.buyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    test.stepUntil(state, function(s) { return test.getMoteCount(s) > 0; }, 5000);
    if (test.getMoteCount(state) <= 0) return false;
    state.weftlings = [];
    state.ownedClassCount = 0;
    var motes = state.motes;
    var targetMote = null;
    for (var i = 0; i < motes.length; i++) {
      if (typeof motes[i].fadeTime === 'number' && isFinite(motes[i].fadeTime)) {
        targetMote = motes[i];
        break;
      }
    }
    if (!targetMote) return false;
    targetMote.age = 0;
    state.motes = [targetMote];
    test.assertStateInvariants(state);
    GW.Simulation.step(state, targetMote.fadeTime + 1);
    return state.motes.length === 0;
  };

  test.testOverflow = function() {
    var state = test.createState(42);
    fundState(state, state.maxCapacity);
    test.buyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    fundState(state, state.maxCapacity);
    test.step(state, 10);
    return state.reservoir <= state.maxCapacity;
  };

  test.testUnitPurchase = function() {
    var state = test.createState(42);
    fundState(state, 100);
    var initialReservoir = state.reservoir;
    var initialCount = state.weftlings.length;
    test.buyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    return state.reservoir < initialReservoir && state.weftlings.length === initialCount + 1;
  };

  test.testUpgradePurchase = function() {
    var state = test.createState(42);
    fundState(state, 100);
    var initialReservoir = state.reservoir;
    test.buyUpgrade(state, 'WeftlingEfficiency');
    return state.reservoir < initialReservoir && state.upgrades.global.length === 1;
  };

  test.testDoctrineLock = function() {
    var state = test.createState(42);
    fundState(state, 100);
    test.chooseDoctrine(state, 'LUMINANCE');
    try {
      test.chooseDoctrine(state, 'CAPTIVATION');
      return false;
    } catch (e) {
      return true;
    }
  };

  test.testPhaseProgression = function() {
    var state = test.createState(42);
    state.totalGlimCaptured = 500;
    state.totalGlimCapturedThisRun = 500;
    fundState(state, 100);
    test.buyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    test.stepUntil(state, function(s) { return s.phase >= 2; }, 5000);
    return state.phase === 2;
  };

  test.testRetuning = function() {
    var state = test.createState(42);
    state.totalGlimCaptured = 1000;
    state.totalGlimCapturedThisRun = 1000;
    fundState(state, 100);
    test.buyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    test.step(state, 100);
    if (state.phase < 2) {
      test.stepUntil(state, function(s) { return s.phase >= 2; }, 5000);
    }
    var initialIridescence = state.iridescence;
    var iridescenceGained = test.retune(state);
    return typeof iridescenceGained === 'number' && iridescenceGained > 0 &&
           state.iridescence > initialIridescence && state.phase === 1 &&
           state.reservoir === 100 && state.weftlings.length === 0;
  };

  test.testVictory = function() {
    var state = test.createState(42);
    state.phase = 4;
    state.highestPhaseUnlocked = 4;
    state.totalGlimCaptured = 10000;
    state.totalGlimCapturedThisRun = 10000;
    state.ownedClassCount = 5;
    state.weftlings = [
      {id: 'w1', type: DATA.weftlingTypes.GLIMSPINNER, x: 0, y: 0},
      {id: 'w2', type: DATA.weftlingTypes.DRIFTCATCHER, x: 10, y: 10},
      {id: 'w3', type: DATA.weftlingTypes.THREADWEAVER, x: 20, y: 20},
      {id: 'w4', type: DATA.weftlingTypes.HARMONIZER, x: 30, y: 30},
      {id: 'w5', type: DATA.weftlingTypes.LOOMGUARD, x: 40, y: 40}
    ];
    state.upgrades.global = [
      'WeftlingEfficiency', 'ReservoirExpansion', 'DriftReduction',
      'BasicTraining', 'FieldAmplifier', 'ReinforcedField',
      'SwiftCurrent', 'MoteLongevity', 'RapidDeployment',
      'GlimMagnet', 'ProductionSurge', 'CaptureNet'
    ];
    state.maxCapacity = 100 + 50 + 100;
    state.reservoir = state.maxCapacity;
    test.assertStateInvariants(state);
    test.step(state, 60000);
    test.assertStateInvariants(state);
    return state.victory === true;
  };

  test.testOfflineProgress = function() {
    var state = test.createState(42);
    fundState(state, 100);
    test.buyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    state.reservoir = 0;
    test.assertStateInvariants(state);
    var serialized = JSON.stringify(GW.State.toPersistent(state));
    var reconstructed = GW.State.fromPersistent(JSON.parse(serialized));
    if (GW.Simulation.init) {
      reconstructed = GW.Simulation.init(reconstructed);
    }
    test.assertStateInvariants(reconstructed);
    var gained = test.applyOfflineProgress(reconstructed, 3600);
    return gained.glimGained > 0;
  };

  test.testSaveLoad = function() {
    var state = test.createState(42);
    fundState(state, 100);
    test.buyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    test.assertStateInvariants(state);
    var serialized = JSON.stringify(GW.State.toPersistent(state));
    var reconstructed = GW.State.fromPersistent(JSON.parse(serialized));
    if (GW.Simulation.init) {
      reconstructed = GW.Simulation.init(reconstructed);
    }
    test.assertStateInvariants(reconstructed);
    return reconstructed.reservoir === state.reservoir && reconstructed.weftlings.length === state.weftlings.length;
  };
})();

(function() {
  'use strict';

  if (typeof window.GW === 'undefined') {
    window.GW = {};
  }
  if (typeof window.GW.State !== 'undefined') {
    return;
  }

  var SAVE_KEY = "glimweave_save_v2";
  var LEGACY_SAVE_KEYS = ["glimweave_save_v1"];
  var STATE_VERSION = "2.0";
  var MAX_OFFLINE_SECONDS = 3600;
  var OFFLINE_PRODUCTION_MULTIPLIER = 0.5;

  function deepCopy(obj) {
    return JSON.parse(JSON.stringify(obj));
  }

  function generateId() {
    return window.GW.Utils.uuid();
  }

  function getProductionRate(state) {
    var rate = 0;
    var weftlings = state.weftlings;
    var DATA = window.GW.DATA;
    for (var i = 0; i < weftlings.length; i++) {
      var w = weftlings[i];
      var wd = DATA.weftlings[w.type];
      if (wd) {
        rate += wd.baseProduction || 0;
      }
    }
    return rate;
  }

  function computeOwnedClassCount(weftlings) {
    var types = {};
    for (var i = 0; i < weftlings.length; i++) {
      types[weftlings[i].type] = true;
    }
    return Object.keys(types).length;
  }

  function validateState(state) {
    var DATA = window.GW.DATA;
    var errors = [];

    if (typeof state.version !== 'string' || state.version === '') {
      errors.push('version must be a non-empty string');
    }

    if (typeof state.phase !== 'number' || state.phase < 1 || state.phase > 4 || Math.floor(state.phase) !== state.phase) {
      errors.push('phase must be an integer 1-4, got ' + state.phase);
    }

    if (typeof state.highestPhaseUnlocked !== 'number' || state.highestPhaseUnlocked < 1 || state.highestPhaseUnlocked > 4 || Math.floor(state.highestPhaseUnlocked) !== state.highestPhaseUnlocked) {
      errors.push('highestPhaseUnlocked must be an integer 1-4, got ' + state.highestPhaseUnlocked);
    } else if (state.highestPhaseUnlocked < state.phase) {
      errors.push('highestPhaseUnlocked must be >= phase');
    }

    if (typeof state.totalGlimCaptured !== 'number' || !isFinite(state.totalGlimCaptured) || state.totalGlimCaptured < 0) {
      errors.push('totalGlimCaptured must be a non-negative finite number, got ' + state.totalGlimCaptured);
    }

    if (typeof state.totalGlimCapturedThisRun !== 'number' || !isFinite(state.totalGlimCapturedThisRun) || state.totalGlimCapturedThisRun < 0) {
      errors.push('totalGlimCapturedThisRun must be a non-negative finite number, got ' + state.totalGlimCapturedThisRun);
    }

    if (typeof state.reservoir !== 'number' || !isFinite(state.reservoir) || state.reservoir < 0) {
      errors.push('reservoir must be a non-negative finite number, got ' + state.reservoir);
    }

    if (typeof state.maxCapacity !== 'number' || !isFinite(state.maxCapacity) || state.maxCapacity < 100) {
      errors.push('maxCapacity must be >= 100, got ' + state.maxCapacity);
    }

    if (typeof state.baseCapacity !== 'number' || !isFinite(state.baseCapacity) || state.baseCapacity < 100) {
      errors.push('baseCapacity must be >= 100, got ' + state.baseCapacity);
    }

    if (state.reservoir > state.maxCapacity) {
      errors.push('reservoir must be <= maxCapacity');
    }

    if (state.totalGlimCaptured < state.reservoir) {
      errors.push('totalGlimCaptured must be >= reservoir');
    }

    if (typeof state.iridescence !== 'number' || !isFinite(state.iridescence) || state.iridescence < 0) {
      errors.push('iridescence must be a non-negative finite number, got ' + state.iridescence);
    }

    if (!Array.isArray(state.weftlings)) {
      errors.push('weftlings must be an array');
    } else {
      var weftlingIds = {};
      var weftlingTypes = {};
      for (var i = 0; i < state.weftlings.length; i++) {
        var w = state.weftlings[i];
        if (typeof w.id !== 'string' || w.id === '') {
          errors.push('weftling[' + i + '].id must be a non-empty string');
        } else if (weftlingIds[w.id]) {
          errors.push('weftling[' + i + '].id duplicate: ' + w.id);
        }
        weftlingIds[w.id] = true;

        if (typeof w.type !== 'string' || !DATA.weftlings[w.type]) {
          errors.push('weftling[' + i + '].type must be a valid weftling type, got ' + w.type);
        }
        weftlingTypes[w.type] = true;

        if (typeof w.x !== 'number' || !isFinite(w.x) || w.x < 0) {
          errors.push('weftling[' + i + '].x must be a non-negative finite number, got ' + w.x);
        }
        if (typeof w.y !== 'number' || !isFinite(w.y) || w.y < 0) {
          errors.push('weftling[' + i + '].y must be a non-negative finite number, got ' + w.y);
        }
      }
      var actualClassCount = Object.keys(weftlingTypes).length;
      if (typeof state.ownedClassCount !== 'number' || state.ownedClassCount !== actualClassCount) {
        errors.push('ownedClassCount must equal number of unique weftling types, got ' + state.ownedClassCount + ' expected ' + actualClassCount);
      }
    }

    if (typeof state.upgrades !== 'object' || state.upgrades === null) {
      errors.push('upgrades must be an object');
    } else {
      if (!Array.isArray(state.upgrades.global)) {
        errors.push('upgrades.global must be an array');
      } else {
        for (var i = 0; i < state.upgrades.global.length; i++) {
          var gid = state.upgrades.global[i];
          if (typeof gid !== 'string' || !DATA.globalUpgrades[gid]) {
            errors.push('upgrades.global[' + i + '] must be a valid global upgrade ID, got ' + gid);
          }
        }
      }

      if (state.upgrades.doctrine !== null) {
        if (typeof state.upgrades.doctrine !== 'string' || !DATA.doctrines[state.upgrades.doctrine]) {
          errors.push('upgrades.doctrine must be null or a valid doctrine ID, got ' + state.upgrades.doctrine);
        }
      }

      if (!Array.isArray(state.upgrades.doctrineUpgrades)) {
        errors.push('upgrades.doctrineUpgrades must be an array');
      } else {
        var docId = state.upgrades.doctrine;
        var docUpgrades = docId ? DATA.doctrineUpgrades[docId] : null;
        var docUpgradeIds = {};
        if (docUpgrades) {
          for (var j = 0; j < docUpgrades.length; j++) {
            docUpgradeIds[docUpgrades[j].id] = true;
          }
        }
        for (var k = 0; k < state.upgrades.doctrineUpgrades.length; k++) {
          var did = state.upgrades.doctrineUpgrades[k];
          if (typeof did !== 'string' || !docUpgradeIds[did]) {
            errors.push('upgrades.doctrineUpgrades[' + k + '] must be a valid doctrine upgrade ID for doctrine ' + docId + ', got ' + did);
          }
        }
      }
    }

    if (!Array.isArray(state.permanentUpgrades)) {
      errors.push('permanentUpgrades must be an array');
    } else {
      for (var pi = 0; pi < state.permanentUpgrades.length; pi++) {
        var pid = state.permanentUpgrades[pi];
        if (typeof pid !== 'string' || !DATA.permanentUpgrades[pid]) {
          errors.push('permanentUpgrades[' + pi + '] must be a valid permanent upgrade ID, got ' + pid);
        }
      }
    }

    if (typeof state.retuningCount !== 'number' || !isFinite(state.retuningCount) || state.retuningCount < 0) {
      errors.push('retuningCount must be a non-negative finite number, got ' + state.retuningCount);
    }

    if (state.lastRetuningTime !== null) {
      if (typeof state.lastRetuningTime !== 'number' || !isFinite(state.lastRetuningTime)) {
        errors.push('lastRetuningTime must be a finite number or null, got ' + state.lastRetuningTime);
      }
    }

    if (Array.isArray(state.motes)) {
      if (state.motes.length > window.GW.MAX_MOTES) {
        errors.push('motes.length must be <= GW.MAX_MOTES (500), got ' + state.motes.length);
      }
      for (var mi = 0; mi < state.motes.length; mi++) {
        var m = state.motes[mi];
        if (typeof m.id !== 'string' || m.id === '') {
          errors.push('motes[' + mi + '].id must be a non-empty string');
        }
        if (typeof m.x !== 'number' || !isFinite(m.x)) {
          errors.push('motes[' + mi + '].x must be a finite number');
        }
        if (typeof m.y !== 'number' || !isFinite(m.y)) {
          errors.push('motes[' + mi + '].y must be a finite number');
        }
        if (typeof m.vx !== 'number' || !isFinite(m.vx)) {
          errors.push('motes[' + mi + '].vx must be a finite number');
        }
        if (typeof m.vy !== 'number' || !isFinite(m.vy)) {
          errors.push('motes[' + mi + '].vy must be a finite number');
        }
        if (typeof m.age !== 'number' || !isFinite(m.age) || m.age < 0) {
          errors.push('motes[' + mi + '].age must be a non-negative finite number, got ' + m.age);
        }
        if (typeof m.fadeTime !== 'number' || !isFinite(m.fadeTime)) {
          errors.push('motes[' + mi + '].fadeTime must be a finite number');
        } else if (m.age > m.fadeTime) {
          errors.push('motes[' + mi + '].age must be <= fadeTime');
        }
        if (typeof m.value !== 'number' || (m.value !== 1 && m.value !== 2)) {
          errors.push('motes[' + mi + '].value must be 1 or 2, got ' + m.value);
        }
      }
    }

    if (typeof state.pressure !== 'number' || !isFinite(state.pressure) || state.pressure < 0 || state.pressure > 1) {
      errors.push('pressure must be a number between 0 and 1, got ' + state.pressure);
    }

    if (typeof state.bottleneckTimer !== 'number' || !isFinite(state.bottleneckTimer)) {
      errors.push('bottleneckTimer must be a finite number');
    }

    if (typeof state.irradianceActive !== 'boolean') {
      errors.push('irradianceActive must be a boolean');
    }

    if (typeof state.victory !== 'boolean') {
      errors.push('victory must be a boolean');
    }

    if (state.victoryTime !== null) {
      if (typeof state.victoryTime !== 'number' || !isFinite(state.victoryTime)) {
        errors.push('victoryTime must be a finite number or null');
      }
    }

    if (typeof state.settings !== 'object' || state.settings === null) {
      errors.push('settings must be an object');
    } else {
      if (typeof state.settings.reducedMotion !== 'boolean') {
        errors.push('settings.reducedMotion must be a boolean');
      }
      if (typeof state.settings.colorblindMode !== 'string' || !DATA.colorblindModes[state.settings.colorblindMode]) {
        errors.push('settings.colorblindMode must be a valid colorblind mode, got ' + state.settings.colorblindMode);
      }
      if (typeof state.settings.speed !== 'number' || ![0.5, 1, 2, 4].indexOf(state.settings.speed) === -1) {
        errors.push('settings.speed must be one of [0.5, 1, 2, 4], got ' + state.settings.speed);
      }
      if (typeof state.settings.paused !== 'boolean') {
        errors.push('settings.paused must be a boolean');
      }
      if (typeof state.settings.tutorialComplete !== 'boolean') {
        errors.push('settings.tutorialComplete must be a boolean');
      }
      if (typeof state.settings.audioEnabled !== 'boolean') {
        errors.push('settings.audioEnabled must be a boolean');
      }
    }

    if (typeof state.tutorialStep !== 'number' || !isFinite(state.tutorialStep) || state.tutorialStep < 0 || state.tutorialStep > 8 || Math.floor(state.tutorialStep) !== state.tutorialStep) {
      errors.push('tutorialStep must be an integer 0-8, got ' + state.tutorialStep);
    }

    if (typeof state.rngSeed !== 'number' || !isFinite(state.rngSeed)) {
      errors.push('rngSeed must be a finite number');
    }

    if (typeof state.lastUpdate !== 'number' || !isFinite(state.lastUpdate)) {
      errors.push('lastUpdate must be a finite number');
    }

    if (errors.length > 0) {
      throw new Error('State validation failed:\n' + errors.join('\n'));
    }
  }

  function toPersistent(state) {
    var persistent = {
      version: state.version,
      rngSeed: state.rngSeed,
      lastUpdate: state.lastUpdate,
      phase: state.phase,
      highestPhaseUnlocked: state.highestPhaseUnlocked,
      totalGlimCaptured: state.totalGlimCaptured,
      totalGlimCapturedThisRun: state.totalGlimCapturedThisRun,
      reservoir: state.reservoir,
      iridescence: state.iridescence,
      maxCapacity: state.maxCapacity,
      baseCapacity: state.baseCapacity,
      weftlings: deepCopy(state.weftlings),
      ownedClassCount: state.ownedClassCount,
      upgrades: deepCopy(state.upgrades),
      permanentUpgrades: deepCopy(state.permanentUpgrades),
      retuningCount: state.retuningCount,
      lastRetuningTime: state.lastRetuningTime,
      settings: deepCopy(state.settings),
      tutorialStep: state.tutorialStep
    };
    return persistent;
  }

  function fromPersistent(persistentState) {
    var runtime = {
      version: persistentState.version,
      rngSeed: persistentState.rngSeed,
      lastUpdate: persistentState.lastUpdate,
      phase: persistentState.phase,
      highestPhaseUnlocked: persistentState.highestPhaseUnlocked,
      totalGlimCaptured: persistentState.totalGlimCaptured,
      totalGlimCapturedThisRun: persistentState.totalGlimCapturedThisRun,
      reservoir: persistentState.reservoir,
      iridescence: persistentState.iridescence,
      maxCapacity: persistentState.maxCapacity,
      baseCapacity: persistentState.baseCapacity,
      weftlings: deepCopy(persistentState.weftlings || []),
      ownedClassCount: persistentState.ownedClassCount || 0,
      upgrades: deepCopy(persistentState.upgrades || { global: [], doctrine: null, doctrineUpgrades: [] }),
      permanentUpgrades: deepCopy(persistentState.permanentUpgrades || []),
      retuningCount: persistentState.retuningCount || 0,
      lastRetuningTime: persistentState.lastRetuningTime || null,
      motes: [],
      pressure: 0,
      bottleneckTimer: 0,
      irradianceActive: false,
      victory: false,
      victoryTime: null,
      settings: deepCopy(persistentState.settings || {
        reducedMotion: false,
        colorblindMode: 'DEFAULT',
        speed: 1,
        paused: false,
        tutorialComplete: false,
        audioEnabled: true
      }),
      tutorialStep: persistentState.tutorialStep || 0
    };
    return runtime;
  }

  function migrate(state) {
    var s = deepCopy(state);
    if (typeof s.version === 'undefined' || s.version === null || s.version === '') {
      s.version = STATE_VERSION;
    }
    s.version = STATE_VERSION;
    s.ownedClassCount = computeOwnedClassCount(s.weftlings || []);
    return s;
  }

  function compress(data) {
    try {
      if (typeof pako !== 'undefined' && pako.gzip) {
        var str = JSON.stringify(data);
        var binaryString = pako.gzip(str, { to: 'string' });
        return binaryString;
      }
    } catch (e) {
    }
    return null;
  }

  function decompress(data) {
    try {
      if (typeof pako !== 'undefined' && pako.ungzip) {
        var str = pako.ungzip(data, { to: 'string' });
        return JSON.parse(str);
      }
    } catch (e) {
    }
    return null;
  }

  function save(state) {
    try {
      var persistent = toPersistent(state);
      var jsonStr = JSON.stringify(persistent);
      try {
        localStorage.setItem(SAVE_KEY, jsonStr);
      } catch (e) {
      }
    } catch (e) {
    }
  }

  function load() {
    try {
      // Development save compatibility is intentionally disabled. Remove
      // earlier namespaces so stale experimental state cannot affect boot.
      for (var i = 0; i < LEGACY_SAVE_KEYS.length; i++) {
        localStorage.removeItem(LEGACY_SAVE_KEYS[i]);
      }
      var raw = localStorage.getItem(SAVE_KEY);
      if (raw === null || raw === undefined) {
        return null;
      }
      var persistentState = JSON.parse(raw);
      var migrated = migrate(persistentState);
      var runtime = fromPersistent(migrated);
      validateState(runtime);
      return runtime;
    } catch (e) {
      return null;
    }
  }

  function deleteSave() {
    try {
      localStorage.removeItem(SAVE_KEY);
      for (var i = 0; i < LEGACY_SAVE_KEYS.length; i++) {
        localStorage.removeItem(LEGACY_SAVE_KEYS[i]);
      }
    } catch (e) {
    }
  }

  function applyOfflineProgress(state, offlineMs) {
    var cappedMs = Math.min(offlineMs, MAX_OFFLINE_SECONDS * 1000);
    var productionRate = getProductionRate(state);
    var glimGained = productionRate * (cappedMs / 1000) * OFFLINE_PRODUCTION_MULTIPLIER;
    var headroom = state.maxCapacity - state.reservoir;
    var actualGlim = Math.min(glimGained, headroom);
    state.reservoir = Math.min(state.reservoir + actualGlim, state.maxCapacity);
    state.lastUpdate = Date.now();
    return { glimGained: actualGlim, seconds: cappedMs / 1000 };
  }

  function create(seed) {
    var DATA = window.GW.DATA;
    var now = Date.now();
    var rngSeed = seed !== undefined ? seed : now;

    var weftlings = [];
    var ownedClassCount = 0;

    var upgrades = {
      global: [],
      doctrine: null,
      doctrineUpgrades: []
    };

    var permanentUpgrades = [];

    var settings = {
      reducedMotion: false,
      colorblindMode: 'DEFAULT',
      speed: 1,
      paused: false,
      tutorialComplete: false,
      audioEnabled: true
    };

    var state = {
      version: STATE_VERSION,
      rngSeed: rngSeed,
      lastUpdate: now,
      phase: 1,
      highestPhaseUnlocked: 1,
      totalGlimCaptured: 100,
      totalGlimCapturedThisRun: 0,
      reservoir: 100,
      iridescence: 0,
      maxCapacity: DATA.constants.baseReservoirCapacity,
      baseCapacity: DATA.constants.baseReservoirCapacity,
      weftlings: weftlings,
      ownedClassCount: ownedClassCount,
      upgrades: upgrades,
      permanentUpgrades: permanentUpgrades,
      retuningCount: 0,
      lastRetuningTime: null,
      motes: [],
      pressure: 0,
      bottleneckTimer: 0,
      irradianceActive: false,
      victory: false,
      victoryTime: null,
      settings: settings,
      tutorialStep: 0
    };

    validateState(state);
    return state;
  }

  function resetForRetuning(state) {
    var permanentUpgrades = state.permanentUpgrades || [];
    var DATA = window.GW.DATA;

    var extraCapacity = 0;
    var extraSlots = 0;
    for (var i = 0; i < permanentUpgrades.length; i++) {
      var pu = DATA.permanentUpgrades[permanentUpgrades[i]];
      if (pu) {
        if (pu.id === 'ReservoirBlueprint') {
          extraCapacity += 100 * (pu.stackable ? (permanentUpgrades.filter(function(id) { return id === 'ReservoirBlueprint'; }).length) : 1);
        } else if (pu.id === 'WeftlingMemory') {
          extraSlots += 1 * (pu.stackable ? (permanentUpgrades.filter(function(id) { return id === 'WeftlingMemory'; }).length) : 1);
        } else if (pu.id === 'ReservoirReinforcement') {
          extraCapacity += 75;
        }
      }
    }

    var baseCapacity = DATA.constants.baseReservoirCapacity + extraCapacity;
    var iridescence = Math.floor(state.totalGlimCapturedThisRun / 200) + 1;

    var newState = {
      version: STATE_VERSION,
      rngSeed: state.rngSeed,
      lastUpdate: Date.now(),
      phase: 1,
      highestPhaseUnlocked: state.highestPhaseUnlocked,
      totalGlimCaptured: state.totalGlimCaptured,
      totalGlimCapturedThisRun: 0,
      reservoir: 100,
      iridescence: state.iridescence + iridescence,
      maxCapacity: baseCapacity,
      baseCapacity: baseCapacity,
      weftlings: [],
      ownedClassCount: 0,
      upgrades: {
        global: [],
        doctrine: state.upgrades.doctrine,
        doctrineUpgrades: []
      },
      permanentUpgrades: deepCopy(state.permanentUpgrades),
      retuningCount: state.retuningCount + 1,
      lastRetuningTime: Date.now(),
      motes: [],
      pressure: 0,
      bottleneckTimer: 0,
      irradianceActive: false,
      victory: false,
      victoryTime: null,
      settings: deepCopy(state.settings),
      tutorialStep: 0
    };

    validateState(newState);
    return newState;
  }

  window.GW.State = {
    create: create,
    validate: validateState,
    toPersistent: toPersistent,
    fromPersistent: fromPersistent,
    applyOfflineProgress: applyOfflineProgress,
    save: save,
    load: load,
    deleteSave: deleteSave,
    migrate: migrate,
    getVersion: function() { return STATE_VERSION; },
    resetForRetuning: resetForRetuning
  };
})();

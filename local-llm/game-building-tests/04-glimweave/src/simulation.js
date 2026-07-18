(function() {
  'use strict';

  if (typeof window.GW === 'undefined') {
    window.GW = {};
  }
  if (typeof window.GW.Simulation !== 'undefined') {
    return;
  }

  var DATA = window.GW.DATA;
  var Utils = window.GW.Utils;
  var State = window.GW.State;
  var TICK_MS = 100;
  var MAX_MOTES = 500;
  var baseFadeTime = DATA.constants.baseFadeTime;
  var baseDriftSpeed = DATA.constants.baseDriftSpeed;
  var baseReservoirCapacity = DATA.constants.baseReservoirCapacity;

  function getWeftlingCount(state, type) {
    var count = 0;
    for (var i = 0; i < state.weftlings.length; i++) {
      if (state.weftlings[i].type === type) {
        count++;
      }
    }
    return count;
  }

  function countUpgrade(state, upgradeId) {
    var count = 0;
    for (var i = 0; i < state.upgrades.global.length; i++) {
      if (state.upgrades.global[i] === upgradeId) {
        count++;
      }
    }
    return count;
  }

  function countDoctrineUpgrade(state, upgradeId) {
    if (!state.upgrades.doctrineUpgrades) return 0;
    var count = 0;
    for (var i = 0; i < state.upgrades.doctrineUpgrades.length; i++) {
      if (state.upgrades.doctrineUpgrades[i] === upgradeId) {
        count++;
      }
    }
    return count;
  }

  function countPermanentUpgrade(state, upgradeId) {
    var count = 0;
    for (var i = 0; i < state.permanentUpgrades.length; i++) {
      if (state.permanentUpgrades[i] === upgradeId) {
        count++;
      }
    }
    return count;
  }

  function isDoctrineUpgradeUnlocked(state, doctrineId, upgradeId) {
    if (state.upgrades.doctrine !== doctrineId) return false;
    var upgrades = DATA.doctrineUpgrades[doctrineId];
    if (!upgrades) return false;
    var upgradeMap = {};
    for (var i = 0; i < upgrades.length; i++) {
      upgradeMap[upgrades[i].id] = upgrades[i];
    }
    var target = upgradeMap[upgradeId];
    if (!target) return false;
    if (target.requires === null || target.requires === undefined) return true;
    for (var j = 0; j < state.upgrades.doctrineUpgrades.length; j++) {
      if (state.upgrades.doctrineUpgrades[j] === target.requires) {
        return true;
      }
    }
    return false;
  }

  function getUpgradedCost(upgradeId, count) {
    var def = DATA.globalUpgrades[upgradeId] || null;
    var docId = null;
    var docUpgrade = null;
    var doctrineKeys = Object.keys(DATA.doctrineUpgrades);
    for (var d = 0; d < doctrineKeys.length; d++) {
      var docUpgrades = DATA.doctrineUpgrades[doctrineKeys[d]];
      for (var u = 0; u < docUpgrades.length; u++) {
        if (docUpgrades[u].id === upgradeId) {
          docId = doctrineKeys[d];
          docUpgrade = docUpgrades[u];
          break;
        }
      }
      if (docUpgrade) break;
    }
    if (def) {
      return Math.floor(def.startCost * Math.pow(def.scaling, count));
    } else if (docUpgrade) {
      return Math.floor(docUpgrade.startCost * Math.pow(docUpgrade.scaling, count));
    }
    return 0;
  }

  function computeFadeTime(state, x, y) {
    var fadeTime = baseFadeTime;
    var weftlings = state.weftlings;
    var Loomguard = DATA.weftlingTypes.LOOMGUARD;
    for (var i = 0; i < weftlings.length; i++) {
      var w = weftlings[i];
      if (w.type !== Loomguard) continue;
      if (Utils.distance(w.x, w.y, x, y) <= DATA.weftlings.Loomguard.supportRadius) {
        fadeTime *= (1 + DATA.weftlings.Loomguard.baseFadeExtension);
      }
    }
    var driftReduction = countUpgrade(state, 'DriftReduction');
    fadeTime *= Math.pow(1 - 0.15, driftReduction);
    if (state.upgrades.doctrine === DATA.doctrines.RESILIENCE) {
      if (state.upgrades.doctrineUpgrades.indexOf('EnduringGlow') >= 0) {
        fadeTime *= 2;
      }
      if (state.upgrades.doctrineUpgrades.indexOf('SustainedFlow') >= 0 && state.reservoir / state.maxCapacity > 0.5) {
        fadeTime *= 0.75;
      }
    }
    if (state.permanentUpgrades.indexOf('EternalGlow') >= 0) {
      fadeTime *= 1.5;
    }
    if (state.phase >= 3) {
      var pressure = getPressure(state);
      fadeTime *= (1 - pressure * DATA.phaseConstants[state.phase].fadeAccelerationFactor);
      if (fadeTime < 1) fadeTime = 1;
    }
    if (state.upgrades.doctrine === DATA.doctrines.LUMINANCE && state.upgrades.doctrineUpgrades.indexOf('EverflowMatrix') >= 0) {
      fadeTime = Infinity;
    }
    if (state.phase === 4) {
      if (fadeTime !== Infinity) {
        fadeTime /= 3;
      }
    }
    return fadeTime;
  }

  function getFadeRate(state) {
    var totalFadeRate = 0;
    var pressure = getPressure(state);
    var phase = state.phase;
    var phaseFactor = 1;
    if (phase >= 3) {
      phaseFactor *= (1 + pressure * DATA.phaseConstants[phase].fadeAccelerationFactor);
    }
    if (phase === 4) {
      phaseFactor *= 3;
    }
    var everflowActive = state.upgrades.doctrine === DATA.doctrines.LUMINANCE && state.upgrades.doctrineUpgrades.indexOf('EverflowMatrix') >= 0;
    for (var i = 0; i < state.motes.length; i++) {
      var mote = state.motes[i];
      if (mote.age >= mote.fadeTime) continue;
      if (mote.fadeTime === Infinity) continue;
      var baseRate = mote.value / mote.fadeTime;
      totalFadeRate += baseRate * phaseFactor;
    }
    return totalFadeRate;
  }

  function getPressure(state) {
    if (state.phase < 2) return 0;
    var threshold = DATA.phaseConstants[state.phase].pressureThreshold;
    return Math.min(1, state.motes.length / threshold);
  }

  function getProductionRate(state) {
    var rate = getWeftlingCount(state, DATA.weftlingTypes.GLIMSPINNER) * DATA.weftlings.Glimspinner.baseProduction;
    var weftlingEfficiency = countUpgrade(state, 'WeftlingEfficiency');
    var fieldAmplifier = countUpgrade(state, 'FieldAmplifier');
    rate *= (1 + weftlingEfficiency * 0.10);
    rate *= (1 + fieldAmplifier * 0.05);
    if (state.upgrades.doctrine === DATA.doctrines.LUMINANCE) {
      var enhancedSpindles = countDoctrineUpgrade(state, 'EnhancedSpindles');
      rate *= (1 + enhancedSpindles * 0.20);
    }
    var phase = state.phase;
    if (phase >= 2) {
      var pressure = getPressure(state);
      rate *= (1 - pressure * 0.5);
    }
    if (state.reservoir / state.maxCapacity > 0.8 && state.upgrades.doctrine === DATA.doctrines.RESILIENCE && state.upgrades.doctrineUpgrades.indexOf('PressureValve') >= 0) {
      rate *= 1.10;
    }
    var luminousLegacy = countPermanentUpgrade(state, 'LuminousLegacy');
    rate *= (1 + luminousLegacy * 0.10);
    if (state.permanentUpgrades.indexOf('EnduringDesign') >= 0) {
      var pressure = getPressure(state);
      rate *= (1 + pressure * 0.30);
    }
    return rate;
  }

  function getCaptureRate(state) {
    var rate = 0;
    var threadweaverCount = getWeftlingCount(state, DATA.weftlingTypes.THREADWEAVER);
    var threadweaverBonus = Math.min(threadweaverCount * 0.10, 0.50);
    var weftlings = state.weftlings;
    var Driftcatcher = DATA.weftlingTypes.DRIFTCATCHER;
    for (var i = 0; i < weftlings.length; i++) {
      var w = weftlings[i];
      if (w.type !== Driftcatcher) continue;
      var captureRate = DATA.weftlings.Driftcatcher.baseCaptureRate;
      captureRate *= (1 + threadweaverBonus);
      if (state.upgrades.doctrine === DATA.doctrines.CAPTIVATION) {
        if (state.upgrades.doctrineUpgrades.indexOf('VortexLens') >= 0) {
          captureRate *= 1.05;
        }
      }
      var steadyHand = countPermanentUpgrade(state, 'SteadyHand');
      captureRate *= (1 + steadyHand * 0.10);
      var glimMagnet = countUpgrade(state, 'GlimMagnet');
      captureRate *= (1 + glimMagnet * 0.15);
      rate += captureRate;
    }
    var weftlingEfficiency = countUpgrade(state, 'WeftlingEfficiency');
    rate *= (1 + weftlingEfficiency * 0.10);
    var captureNet = countUpgrade(state, 'CaptureNet');
    rate *= (1 + captureNet * 0.12);
    return rate;
  }

  function getDriftSpeed(state) {
    var speed = baseDriftSpeed;
    var swiftCurrent = countUpgrade(state, 'SwiftCurrent');
    speed *= (1 + swiftCurrent * 0.10);
    if (state.upgrades.doctrine === DATA.doctrines.CAPTIVATION) {
      var magneticField = countDoctrineUpgrade(state, 'MagneticField');
      speed *= (1 - magneticField * 0.20);
    }
    return speed;
  }

  function getCaptureRadius(state) {
    var radius = DATA.weftlings.Driftcatcher.captureRadius;
    if (state.upgrades.doctrine === DATA.doctrines.CAPTIVATION) {
      var graspingTendrils = countDoctrineUpgrade(state, 'GraspingTendrils');
      radius *= (1 + graspingTendrils * 0.30);
    }
    var glimMagnet = countUpgrade(state, 'GlimMagnet');
    radius *= (1 + glimMagnet * 0.15);
    var steadyHand = countPermanentUpgrade(state, 'SteadyHand');
    radius *= (1 + steadyHand * 0.10);
    return radius;
  }

  function canSpawnMote(state) {
    return state.motes.length < MAX_MOTES;
  }

  function isWeftlingUnlocked(state, type) {
    var def = DATA.weftlings[type];
    if (!def || !def.unlock) return true;
    if (def.unlock.phase && state.phase < def.unlock.phase) return false;
    if (def.unlock.totalGlimCaptured !== undefined && state.totalGlimCaptured < def.unlock.totalGlimCaptured) return false;
    if (def.unlock.totalGlimSpentOnCapacity !== undefined) {
      var harmonizerCount = getWeftlingCount(state, DATA.weftlingTypes.HARMONIZER);
      var spent = harmonizerCount * DATA.weftlings.Harmonizer.baseCost;
      if (spent < def.unlock.totalGlimSpentOnCapacity) return false;
    }
    return true;
  }

  function getWeftlingCost(type) {
    var def = DATA.weftlings[type];
    if (!def) return 0;
    return def.baseCost;
  }

  function getWeftlingMaxOwned(type) {
    var def = DATA.weftlings[type];
    if (!def) return Infinity;
    return def.maxOwned || Infinity;
  }

  function canBuyWeftling(state, type) {
    if (!isWeftlingUnlocked(state, type)) return false;
    var cost = getWeftlingCost(type);
    if (state.reservoir < cost) return false;
    var currentCount = getWeftlingCount(state, type);
    if (currentCount >= getWeftlingMaxOwned(type)) return false;
    return true;
  }

  function canBuyUpgrade(state, upgradeId) {
    var def = DATA.globalUpgrades[upgradeId];
    if (!def) {
      var found = false;
      var doctrines = Object.keys(DATA.doctrineUpgrades);
      for (var d = 0; d < doctrines.length; d++) {
        var docUpgrades = DATA.doctrineUpgrades[doctrines[d]];
        for (var u = 0; u < docUpgrades.length; u++) {
          if (docUpgrades[u].id === upgradeId) {
            def = docUpgrades[u];
            found = true;
            break;
          }
        }
        if (found) break;
      }
      if (!def) return false;
    }
    var isGlobal = !!DATA.globalUpgrades[upgradeId];
    if (isGlobal) {
      for (var i = 0; i < state.upgrades.global.length; i++) {
        if (state.upgrades.global[i] === upgradeId) {
          var currentCount = countUpgrade(state, upgradeId);
          if (def.cap && currentCount >= def.cap) {
            return false;
          }
        }
      }
      var cost = getUpgradedCost(upgradeId, state.upgrades.global.filter(function(id) { return id === upgradeId; }).length);
      if (state.reservoir < cost) return false;
      return true;
    } else {
      if (state.upgrades.doctrine === null) return false;
      var doctrineId = null;
      var docKeys = Object.keys(DATA.doctrineUpgrades);
      for (var k = 0; k < docKeys.length; k++) {
        var docU = DATA.doctrineUpgrades[docKeys[k]];
        for (var j = 0; j < docU.length; j++) {
          if (docU[j].id === upgradeId) {
            doctrineId = docKeys[k];
            break;
          }
        }
        if (doctrineId) break;
      }
      if (state.upgrades.doctrine !== doctrineId) return false;
      if (!isDoctrineUpgradeUnlocked(state, doctrineId, upgradeId)) return false;
      for (var m = 0; m < state.upgrades.doctrineUpgrades.length; m++) {
        if (state.upgrades.doctrineUpgrades[m] === upgradeId) {
          return false;
        }
      }
      var docDef = null;
      var docUpgrades = DATA.doctrineUpgrades[doctrineId];
      for (var n = 0; n < docUpgrades.length; n++) {
        if (docUpgrades[n].id === upgradeId) {
          docDef = docUpgrades[n];
          break;
        }
      }
      if (!docDef) return false;
      var docCost = getUpgradedCost(upgradeId, state.upgrades.doctrineUpgrades.filter(function(id) { return id === upgradeId; }).length);
      if (state.reservoir < docCost) return false;
      if (docDef.cap) {
        var docCount = countDoctrineUpgrade(state, upgradeId);
        if (docCount >= docDef.cap) return false;
      }
      return true;
    }
  }

  function getUpgradeCost(state, upgradeId) {
    if (DATA.globalUpgrades[upgradeId]) {
      var count = countUpgrade(state, upgradeId);
      return getUpgradedCost(upgradeId, count);
    } else {
      var doctrineId = null;
      var docKeys = Object.keys(DATA.doctrineUpgrades);
      for (var k = 0; k < docKeys.length; k++) {
        var docU = DATA.doctrineUpgrades[docKeys[k]];
        for (var j = 0; j < docU.length; j++) {
          if (docU[j].id === upgradeId) {
            doctrineId = docKeys[k];
            break;
          }
        }
        if (doctrineId) break;
      }
      if (!doctrineId) return 0;
      var docDef = null;
      var docUpgrades = DATA.doctrineUpgrades[doctrineId];
      for (var n = 0; n < docUpgrades.length; n++) {
        if (docUpgrades[n].id === upgradeId) {
          docDef = docUpgrades[n];
          break;
        }
      }
      if (!docDef) return 0;
      var count = countDoctrineUpgrade(state, upgradeId);
      return getUpgradedCost(upgradeId, count);
    }
  }

  function spawnMote(state, x, y, value) {
    if (state.motes.length >= MAX_MOTES) {
      return null;
    }
    if (value !== 1 && value !== 2) {
      value = 1;
    }
    var driftSpeed = getDriftSpeed(state);
    var angle = Utils.RNG.random() * Math.PI * 2;
    var vx = Math.cos(angle) * driftSpeed;
    var vy = Math.sin(angle) * driftSpeed;
    var fadeTime = computeFadeTime(state, x, y);
    var mote = {
      id: Utils.uuid(),
      x: x,
      y: y,
      vx: vx,
      vy: vy,
      age: 0,
      value: value,
      fadeTime: fadeTime
    };
    state.motes.push(mote);
    return mote;
  }

  function removeMote(state, moteId) {
    for (var i = 0; i < state.motes.length; i++) {
      if (state.motes[i].id === moteId) {
        state.motes.splice(i, 1);
        return;
      }
    }
  }

  function tryCaptureMote(state, mote, deltaMs) {
    var captureRadius = getCaptureRadius(state);
    var Driftcatcher = DATA.weftlingTypes.DRIFTCATCHER;
    for (var i = 0; i < state.weftlings.length; i++) {
      var w = state.weftlings[i];
      if (w.type !== Driftcatcher) continue;
      var dx = mote.x - w.x;
      var dy = mote.y - w.y;
      var dist = Math.sqrt(dx * dx + dy * dy);
      if (dist <= captureRadius) {
        var captureRate = getCaptureRate(state) / 10;
        var captureProbability = captureRate * (deltaMs / 1000);
        if (Utils.RNG.random() < captureProbability) {
          if (state.reservoir < state.maxCapacity) {
            var headroom = state.maxCapacity - state.reservoir;
            var actualValue = Math.min(mote.value, headroom);
            state.reservoir += actualValue;
            state.totalGlimCaptured += actualValue;
            state.totalGlimCapturedThisRun += actualValue;
            var vortexLens = state.upgrades.doctrine === DATA.doctrines.CAPTIVATION && state.upgrades.doctrineUpgrades.indexOf('VortexLens') >= 0;
            if (vortexLens) {
              var bonusMultiplier = 0.05 * countDoctrineUpgrade(state, 'VortexLens');
              var bonus = Math.floor(mote.value * bonusMultiplier);
              if (bonus > 0) {
                var bonusHeadroom = state.maxCapacity - state.reservoir;
                if (bonusHeadroom > 0) {
                  var actualBonus = Math.min(bonus, bonusHeadroom);
                  state.reservoir += actualBonus;
                  state.totalGlimCaptured += actualBonus;
                  state.totalGlimCapturedThisRun += actualBonus;
                }
              }
            }
            return true;
          }
        }
      }
    }
    return false;
  }

  function checkTetheredFlightActive(state) {
    if (state.upgrades.doctrine !== DATA.doctrines.CAPTIVATION) return false;
    if (state.upgrades.doctrineUpgrades.indexOf('TetheredFlight') === -1) return false;
    if (typeof state._tetheredFlightActive === 'undefined') {
      state._tetheredFlightActive = false;
      state._tetheredFlightEndTime = 0;
    }
    var now = Date.now();
    if (state._tetheredFlightActive && now < state._tetheredFlightEndTime) {
      return true;
    }
    return false;
  }

  function checkOmniDirectionalCooldown(state) {
    if (state.upgrades.doctrine !== DATA.doctrines.CAPTIVATION) return true;
    if (state.upgrades.doctrineUpgrades.indexOf('OmniDirectional') === -1) return true;
    if (typeof state._omniDirectionalCooldown === 'undefined') {
      state._omniDirectionalCooldown = 0;
    }
    var now = Date.now();
    if (now < state._omniDirectionalCooldown) {
      return true;
    }
    return false;
  }

  function checkRadiantCore(state, deltaMs) {
    if (state.upgrades.doctrine !== DATA.doctrines.LUMINANCE) return 1;
    if (state.upgrades.doctrineUpgrades.indexOf('RadiantCore') === -1) return 1;
    if (typeof state._radiantCoreActive === 'undefined') {
      state._radiantCoreActive = false;
      state._radiantCoreTimer = 0;
      state._radiantCoreCooldown = 0;
    }
    state._radiantCoreTimer += deltaMs;
    if (state._radiantCoreActive) {
      if (state._radiantCoreTimer >= 1000) {
        state._radiantCoreActive = false;
        state._radiantCoreCooldown = 5000;
        state._radiantCoreTimer = 0;
      }
      return 2;
    } else {
      if (state._radiantCoreCooldown > 0) {
        state._radiantCoreCooldown -= deltaMs;
        if (state._radiantCoreCooldown <= 0) {
          state._radiantCoreCooldown = 0;
        }
      } else {
        if (state._radiantCoreTimer >= 5000) {
          state._radiantCoreActive = true;
          state._radiantCoreTimer = 0;
        }
      }
    }
    return 1;
  }

  function checkLuminousSurge(state) {
    if (state.upgrades.doctrine !== DATA.doctrines.LUMINANCE) return 1;
    if (state.upgrades.doctrineUpgrades.indexOf('LuminousSurge') === -1) return 1;
    if (typeof state._luminousSurgeActive === 'undefined') {
      state._luminousSurgeActive = false;
      state._luminousSurgeTimer = 0;
    }
    if (state._luminousSurgeActive) {
      state._luminousSurgeTimer -= TICK_MS;
      if (state._luminousSurgeTimer <= 0) {
        state._luminousSurgeActive = false;
      }
      return 1.15;
    }
    return 1;
  }

  function updateProductionMultiplier(state) {
    var mult = 1;
    mult *= checkRadiantCore(state, TICK_MS);
    mult *= checkLuminousSurge(state);
    return mult;
  }

  function tryAdvancePhase(state) {
    var phase = state.phase;
    if (phase >= 4) return false;
    var thresholds = DATA.phaseThresholds;
    var threshold = thresholds[phase + 1];
    if (!threshold) return false;
    if (state.totalGlimCaptured < threshold.totalGlimCaptured) return false;
    if (threshold.requiredClassCount !== null && state.ownedClassCount < threshold.requiredClassCount) return false;
    state.phase = phase + 1;
    if (state.phase > state.highestPhaseUnlocked) {
      state.highestPhaseUnlocked = state.phase;
    }
    if (state.phase === 4) {
      state.irradianceActive = true;
    }
    if (state.upgrades.doctrine === DATA.doctrines.LUMINANCE && state.upgrades.doctrineUpgrades.indexOf('LuminousSurge') >= 0) {
      state._luminousSurgeActive = true;
      state._luminousSurgeTimer = 10000;
    }
    return true;
  }

  function computeMaxCapacity(state) {
    var capacity = state.baseCapacity;
    var harmonizerCount = getWeftlingCount(state, DATA.weftlingTypes.HARMONIZER);
    capacity += harmonizerCount * DATA.weftlings.Harmonizer.capacityBonus;
    var reservoirExpansion = countUpgrade(state, 'ReservoirExpansion');
    capacity += reservoirExpansion * 100;
    var reservoirReinforcement = countUpgrade(state, 'ReservoirReinforcement');
    capacity += reservoirReinforcement * 75;
    if (state.upgrades.doctrine === DATA.doctrines.RESILIENCE) {
      var sturdyReservoir = countDoctrineUpgrade(state, 'SturdyReservoir');
      capacity += sturdyReservoir * 200;
      if (state.upgrades.doctrineUpgrades.indexOf('UnyieldingFoundation') >= 0) {
        capacity *= 1.5;
      }
    }
    var reservoirBlueprint = countPermanentUpgrade(state, 'ReservoirBlueprint');
    capacity += reservoirBlueprint * 100;
    return Math.floor(capacity);
  }

  function retune(state) {
    var retuneCount = state.retuningCount;
    var minimumInterval = DATA.constants.retuning.minimumIntervalBase * (1 + retuneCount / 10);
    minimumInterval = Math.min(minimumInterval, 3600);
    if (state.lastRetuningTime !== null) {
      var elapsed = (Date.now() - state.lastRetuningTime) / 1000;
      if (elapsed < minimumInterval) {
        throw new Error('Retuning cooldown not elapsed. Wait ' + Math.ceil(minimumInterval - elapsed) + ' more seconds.');
      }
    }
    var conditionsMet = (state.phase >= 2 && state.totalGlimCapturedThisRun >= 1000) || state.phase >= 4;
    if (!conditionsMet) {
      throw new Error('Retuning conditions not met. Need phase >= 2 with 1000+ Glim this run, or phase >= 4.');
    }
    var iridescenceGained = 0;
    if (retuneCount >= 10) {
      var divisor = 200 * (1 + retuneCount / 20);
      iridescenceGained = Math.floor(state.totalGlimCapturedThisRun / divisor) + 1;
    } else {
      iridescenceGained = Math.floor(state.totalGlimCapturedThisRun / 200) + 1;
    }
    var newState = State.resetForRetuning(state);
    State.validate(newState);
    state.version = newState.version;
    state.rngSeed = newState.rngSeed;
    state.lastUpdate = newState.lastUpdate;
    state.phase = newState.phase;
    state.highestPhaseUnlocked = newState.highestPhaseUnlocked;
    state.totalGlimCaptured = newState.totalGlimCaptured;
    state.totalGlimCapturedThisRun = newState.totalGlimCapturedThisRun;
    state.reservoir = newState.reservoir;
    state.iridescence = newState.iridescence;
    state.maxCapacity = newState.maxCapacity;
    state.baseCapacity = newState.baseCapacity;
    state.weftlings = newState.weftlings;
    state.ownedClassCount = newState.ownedClassCount;
    state.upgrades = newState.upgrades;
    state.permanentUpgrades = newState.permanentUpgrades;
    state.retuningCount = newState.retuningCount;
    state.lastRetuningTime = newState.lastRetuningTime;
    state.motes = newState.motes;
    state.pressure = newState.pressure;
    state.bottleneckTimer = newState.bottleneckTimer;
    state.irradianceActive = newState.irradianceActive;
    state.victory = newState.victory;
    state.victoryTime = newState.victoryTime;
    state.tutorialStep = newState.tutorialStep;
    return { success: true, iridescenceGained: iridescenceGained };
  }

  function checkVictory(state) {
    if (state.victory) return true;
    if (state.phase !== 4) return false;
    if (state.ownedClassCount !== 5) return false;
    if (state.reservoir < state.maxCapacity) {
      if (typeof state._fullReservoirTimer !== 'number') {
        state._fullReservoirTimer = 0;
      }
      if (state.reservoir === state.maxCapacity) {
        state._fullReservoirTimer += TICK_MS;
        if (state._fullReservoirTimer >= 60000) {
          state.victory = true;
          state.victoryTime = Date.now();
          return true;
        }
      } else {
        state._fullReservoirTimer = 0;
      }
      return false;
    }
    if (state.totalGlimCaptured < 10000) return false;
    var totalUpgrades = state.upgrades.global.length + state.upgrades.doctrineUpgrades.length;
    if (totalUpgrades < 12) return false;
    state.victory = true;
    state.victoryTime = Date.now();
    return true;
  }

  function applyProduction(state, deltaMs) {
    var rate = getProductionRate(state) * updateProductionMultiplier(state);
    var productionAmount = rate * (deltaMs / 1000);
    if (state.settings.paused) return;
    var glimspinnerCount = getWeftlingCount(state, DATA.weftlingTypes.GLIMSPINNER);
    if (glimspinnerCount === 0) return;
    if (typeof state._productionAccumulator !== 'number' || !isFinite(state._productionAccumulator) || state._productionAccumulator < 0) {
      state._productionAccumulator = 0;
    }
    state._productionAccumulator += productionAmount;
    var wholeMotes = Math.floor(state._productionAccumulator);
    state._productionAccumulator -= wholeMotes;
    if (wholeMotes > 0) {
      var glimspinners = [];
      for (var i = 0; i < state.weftlings.length; i++) {
        if (state.weftlings[i].type === DATA.weftlingTypes.GLIMSPINNER) {
          glimspinners.push(state.weftlings[i]);
        }
      }
      var brilliantSynthesis = state.upgrades.doctrine === DATA.doctrines.LUMINANCE && state.upgrades.doctrineUpgrades.indexOf('BrilliantSynthesis') >= 0;
      for (var j = 0; j < wholeMotes; j++) {
        if (!canSpawnMote(state)) {
          state._productionAccumulator = 0;
          break;
        }
        var spinner = glimspinners[j % glimspinners.length];
        var x = spinner.x + Utils.RNG.integer(-20, 20);
        var y = spinner.y + Utils.RNG.integer(-20, 20);
        var value = 1;
        if (brilliantSynthesis && Utils.RNG.random() < 0.05) {
          value = 2;
        }
        spawnMote(state, x, y, value);
      }
    }
  }

  function updateMotes(state, deltaMs) {
    if (state.settings.paused || state.settings.reducedMotion) {
      return;
    }
    var driftSpeed = getDriftSpeed(state);
    var newMotes = [];
    for (var i = 0; i < state.motes.length; i++) {
      var mote = state.motes[i];
      mote.age += deltaMs;
      if (mote.age > mote.fadeTime) {
        continue;
      }
      if (!state.settings.reducedMotion) {
        mote.x += mote.vx * (deltaMs / 1000);
        mote.y += mote.vy * (deltaMs / 1000);
      }
      var captured = tryCaptureMote(state, mote, deltaMs);
      if (captured) {
        continue;
      }
      newMotes.push(mote);
    }
    state.motes = newMotes;
  }

  function updatePressure(state, deltaMs) {
    var phase = state.phase;
    if (phase < 2) {
      state.pressure = 0;
      state.bottleneckTimer = 0;
      return;
    }
    var pressureThreshold = DATA.phaseConstants[phase].pressureThreshold;
    var production = getProductionRate(state);
    var capture = getCaptureRate(state);
    state.pressure = Math.min(1, state.motes.length / pressureThreshold);
    if (production > capture) {
      state.bottleneckTimer += deltaMs;
      if (state.bottleneckTimer >= 10000 && phase >= 3) {
        state.pressure = Math.min(1, state.pressure * 2);
      }
    } else {
      state.bottleneckTimer = Math.max(0, state.bottleneckTimer - deltaMs);
    }
  }

  function step(state, deltaMs) {
    if (state.settings.paused) {
      return;
    }
    if (state.victory) {
      return;
    }
    deltaMs = deltaMs || TICK_MS;
    var actualDelta = deltaMs * state.settings.speed;
    applyProduction(state, actualDelta);
    updateMotes(state, actualDelta);
    updatePressure(state, actualDelta);
    tryAdvancePhase(state);
    checkVictory(state);
    State.validate(state);
  }

  function handleAction(state, action) {
    if (state.victory && action.type !== 'PAUSE' && action.type !== 'SET_SPEED' && action.type !== 'SET_REDUCED_MOTION' && action.type !== 'SET_COLORBLIND_MODE') {
      throw new Error('Game already won. No more actions allowed.');
    }
    switch (action.type) {
      case 'BUY_WEFTLING':
        if (typeof action.weftlingType !== 'string' || typeof action.x !== 'number' || typeof action.y !== 'number') {
          throw new Error('BUY_WEFTLING: invalid action parameters');
        }
        if (!canBuyWeftling(state, action.weftlingType)) {
          throw new Error('Cannot buy Weftling: not unlocked, insufficient Glim, or max owned reached');
        }
        var cost = getWeftlingCost(action.weftlingType);
        var rapidDeployment = countUpgrade(state, 'RapidDeployment');
        cost = Math.floor(cost * (1 - rapidDeployment * 0.05));
        var prismaticCore = state.permanentUpgrades.indexOf('PrismaticCore') >= 0;
        var doctrinalInsight = countUpgrade(state, 'DoctoralInsight');
        if (prismaticCore) {
          cost = Math.floor(cost * 0.9);
        }
        if (doctrinalInsight > 0) {
          cost = Math.floor(cost * (1 - doctrinalInsight * 0.08));
        }
        if (state.reservoir < cost) {
          throw new Error('Cannot buy Weftling: insufficient Glim');
        }
        state.reservoir -= cost;
        var weftling = {
          id: Utils.uuid(),
          type: action.weftlingType,
          x: action.x,
          y: action.y
        };
        state.weftlings.push(weftling);
        state.ownedClassCount = computeOwnedClassCount(state.weftlings);
        state.maxCapacity = computeMaxCapacity(state);
        State.validate(state);
        return state;
      case 'BUY_UPGRADE':
        if (typeof action.upgradeId !== 'string') {
          throw new Error('BUY_UPGRADE: missing upgradeId');
        }
        if (!canBuyUpgrade(state, action.upgradeId)) {
          throw new Error('Cannot buy upgrade: not available, already owned, or insufficient Glim');
        }
        var upgradeCost = getUpgradeCost(state, action.upgradeId);
        var prismaticCore2 = state.permanentUpgrades.indexOf('PrismaticCore') >= 0;
        var doctrinalInsight2 = countUpgrade(state, 'DoctoralInsight');
        if (prismaticCore2) {
          upgradeCost = Math.floor(upgradeCost * 0.9);
        }
        if (doctrinalInsight2 > 0) {
          upgradeCost = Math.floor(upgradeCost * (1 - doctrinalInsight2 * 0.08));
        }
        if (state.reservoir < upgradeCost) {
          throw new Error('Cannot buy upgrade: insufficient Glim');
        }
        state.reservoir -= upgradeCost;
        if (DATA.globalUpgrades[action.upgradeId]) {
          state.upgrades.global.push(action.upgradeId);
        } else {
          state.upgrades.doctrineUpgrades.push(action.upgradeId);
        }
        state.maxCapacity = computeMaxCapacity(state);
        State.validate(state);
        return state;
      case 'CHOOSE_DOCTRINE':
        if (typeof action.doctrineId !== 'string') {
          throw new Error('CHOOSE_DOCTRINE: missing doctrineId');
        }
        if (state.upgrades.doctrine !== null) {
          throw new Error('Doctrine already chosen');
        }
        if (!DATA.doctrines[action.doctrineId]) {
          throw new Error('Invalid doctrine ID');
        }
        state.upgrades.doctrine = action.doctrineId;
        State.validate(state);
        return state;
      case 'RETUNE':
        return retune(state);
      case 'PAUSE':
        state.settings.paused = !state.settings.paused;
        State.validate(state);
        return state;
      case 'SET_SPEED':
        if (typeof action.speed !== 'number' || [0.5, 1, 2, 4].indexOf(action.speed) === -1) {
          throw new Error('SET_SPEED: speed must be 0.5, 1, 2, or 4');
        }
        state.settings.speed = action.speed;
        State.validate(state);
        return state;
      case 'SET_REDUCED_MOTION':
        if (typeof action.enabled !== 'boolean') {
          throw new Error('SET_REDUCED_MOTION: enabled must be boolean');
        }
        state.settings.reducedMotion = action.enabled;
        State.validate(state);
        return state;
      case 'SET_COLORBLIND_MODE':
        if (typeof action.mode !== 'string' || !DATA.colorblindModes[action.mode]) {
          throw new Error('SET_COLORBLIND_MODE: invalid mode');
        }
        state.settings.colorblindMode = action.mode;
        State.validate(state);
        return state;
      case 'SKIP_TUTORIAL':
        state.settings.tutorialComplete = true;
        state.tutorialStep = 8;
        State.validate(state);
        return state;
      case 'ACTIVATE_ABILITY':
        if (typeof action.abilityId !== 'string') {
          throw new Error('ACTIVATE_ABILITY: missing abilityId');
        }
        if (action.abilityId === 'TetheredFlight') {
          if (state.upgrades.doctrine !== DATA.doctrines.CAPTIVATION || state.upgrades.doctrineUpgrades.indexOf('TetheredFlight') === -1) {
            throw new Error('Tethered Flight ability not available');
          }
          if (typeof state._tetheredFlightCooldown === 'undefined') {
            state._tetheredFlightCooldown = 0;
          }
          var now = Date.now();
          if (now < state._tetheredFlightCooldown) {
            throw new Error('Tethered Flight on cooldown');
          }
          state._tetheredFlightActive = true;
          state._tetheredFlightEndTime = now + 5000;
          state._tetheredFlightCooldown = now + 30000;
          return state;
        }
        if (action.abilityId === 'OmniDirectional') {
          if (state.upgrades.doctrine !== DATA.doctrines.CAPTIVATION || state.upgrades.doctrineUpgrades.indexOf('OmniDirectional') === -1) {
            throw new Error('Omni Directional ability not available');
          }
          if (checkOmniDirectionalCooldown(state)) {
            throw new Error('Omni Directional on cooldown');
          }
          var captureRadius = getCaptureRadius(state);
          var reservoirRadius = Math.sqrt(state.maxCapacity) * 10;
          var capturedCount = 0;
          var newMotes = [];
          for (var i = 0; i < state.motes.length; i++) {
            var mote = state.motes[i];
            var dist = Utils.distance(mote.x, mote.y, 0, 0);
            if (dist <= reservoirRadius) {
              var headroom = state.maxCapacity - state.reservoir;
              if (headroom > 0) {
                var actualValue = Math.min(mote.value, headroom);
                state.reservoir += actualValue;
                state.totalGlimCaptured += actualValue;
                state.totalGlimCapturedThisRun += actualValue;
                capturedCount++;
              }
            } else {
              newMotes.push(mote);
            }
          }
          state.motes = newMotes;
          state._omniDirectionalCooldown = Date.now() + 60000;
          State.validate(state);
          return state;
        }
        throw new Error('Unknown ability: ' + action.abilityId);
      default:
        throw new Error('Unknown action type: ' + action.type);
    }
  }

  function getPhase(state) {
    return state.phase;
  }

  function getMotes(state) {
    return state.motes;
  }

  function computeOwnedClassCount(weftlings) {
    var types = {};
    for (var i = 0; i < weftlings.length; i++) {
      types[weftlings[i].type] = true;
    }
    return Object.keys(types).length;
  }

  function init(state) {
    if (!state) {
      state = State.create();
    }
    if (typeof state._fullReservoirTimer === 'undefined') {
      state._fullReservoirTimer = 0;
    }
    if (typeof state._radiantCoreActive === 'undefined') {
      state._radiantCoreActive = false;
      state._radiantCoreTimer = 0;
      state._radiantCoreCooldown = 0;
    }
    if (typeof state._luminousSurgeActive === 'undefined') {
      state._luminousSurgeActive = false;
      state._luminousSurgeTimer = 0;
    }
    if (typeof state._tetheredFlightActive === 'undefined') {
      state._tetheredFlightActive = false;
      state._tetheredFlightEndTime = 0;
      state._tetheredFlightCooldown = 0;
    }
    if (typeof state._omniDirectionalCooldown === 'undefined') {
      state._omniDirectionalCooldown = 0;
    }
    if (typeof state._productionAccumulator !== 'number' || !isFinite(state._productionAccumulator) || state._productionAccumulator < 0) {
      state._productionAccumulator = 0;
    }
    state.maxCapacity = computeMaxCapacity(state);
    State.validate(state);
    return state;
  }

  function createState(seed) {
    var state = State.create(seed);
    return init(state);
  }

  function cloneState(state) {
    return JSON.parse(JSON.stringify(state));
  }

  function testStep(state, steps) {
    for (var i = 0; i < steps; i++) {
      step(state, TICK_MS);
    }
  }

  function testStepUntil(state, condition, maxSteps) {
    var steps = 0;
    while (steps < maxSteps) {
      step(state, TICK_MS);
      steps++;
      if (condition(state)) {
        return steps;
      }
    }
    return steps;
  }

  function testBuyWeftling(state, type, x, y) {
    handleAction(state, { type: 'BUY_WEFTLING', weftlingType: type, x: x, y: y });
  }

  function testBuyUpgrade(state, upgradeId) {
    handleAction(state, { type: 'BUY_UPGRADE', upgradeId: upgradeId });
  }

  function testChooseDoctrine(state, doctrineId) {
    handleAction(state, { type: 'CHOOSE_DOCTRINE', doctrineId: doctrineId });
  }

  function testRetune(state) {
    var result = handleAction(state, { type: 'RETUNE' });
    return result.iridescenceGained;
  }

  function testActivateAbility(state, abilityId) {
    handleAction(state, { type: 'ACTIVATE_ABILITY', abilityId: abilityId });
  }

  function testGetProductionRate(state) {
    return getProductionRate(state);
  }

  function testGetCaptureRate(state) {
    return getCaptureRate(state);
  }

  function testGetPressure(state) {
    return getPressure(state);
  }

  function testGetMoteCount(state) {
    return state.motes.length;
  }

  function testGetReservoir(state) {
    return state.reservoir;
  }

  function testGetPhase(state) {
    return state.phase;
  }

  function testIsVictory(state) {
    return state.victory;
  }

  function testApplyOfflineProgress(state, seconds) {
    var result = State.applyOfflineProgress(state, seconds * 1000);
    return result.glimGained;
  }

  function testSaveState(state) {
    return State.save(state);
  }

  function testLoadState(json) {
    var persistent = JSON.parse(json);
    var runtime = State.fromPersistent(persistent);
    return init(runtime);
  }

  function testValidateState(state) {
    try {
      State.validate(state);
      return true;
    } catch (e) {
      return false;
    }
  }

  function testAssertStateInvariants(state) {
    State.validate(state);
  }

  function testProductionCaptureIndependence() {
    var state = createState(42);
    state.reservoir = 1000;
    testBuyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    testBuyWeftling(state, DATA.weftlingTypes.DRIFTCATCHER, 200, 200);
    testStep(state, 100);
    var production = getProductionRate(state);
    var capture = getCaptureRate(state);
    return production > 0 && capture > 0;
  }

  function testFadeImpact() {
    var state = createState(42);
    state.reservoir = 1000;
    testBuyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    testStep(state, 50);
    var initialCount = state.motes.length;
    testStep(state, 1000);
    return state.motes.length < initialCount;
  }

  function testOverflow() {
    var state = createState(42);
    state.reservoir = state.maxCapacity;
    testBuyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    testStep(state, 10);
    return state.reservoir === state.maxCapacity;
  }

  function testUnitPurchase() {
    var state = createState(42);
    state.reservoir = 1000;
    var initialReservoir = state.reservoir;
    var initialCount = state.weftlings.length;
    testBuyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    return state.reservoir < initialReservoir && state.weftlings.length === initialCount + 1;
  }

  function testUpgradePurchase() {
    var state = createState(42);
    state.reservoir = 1000;
    var initialReservoir = state.reservoir;
    testBuyUpgrade(state, 'WeftlingEfficiency');
    return state.reservoir < initialReservoir && state.upgrades.global.length === 1;
  }

  function testDoctrineLock() {
    var state = createState(42);
    state.reservoir = 1000;
    testChooseDoctrine(state, DATA.doctrines.LUMINANCE);
    try {
      testChooseDoctrine(state, DATA.doctrines.CAPTIVATION);
      return false;
    } catch (e) {
      return true;
    }
  }

  function testPhaseProgression() {
    var state = createState(42);
    state.reservoir = 1000;
    testBuyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    testStepUntil(state, function(s) { return s.phase >= 2; }, 1000);
    return state.phase === 2;
  }

  function testRetuning() {
    var state = createState(42);
    state.reservoir = 1000;
    testBuyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    testStep(state, 100);
    var initialIridescence = state.iridescence;
    testRetune(state);
    return state.iridescence > initialIridescence && state.phase === 1 && state.reservoir === 0;
  }

  function testOfflineProgress() {
    var state = createState(42);
    state.reservoir = 0;
    testBuyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    var saved = testSaveState(state);
    var loaded = testLoadState(saved);
    var gained = testApplyOfflineProgress(loaded, 3600);
    return gained > 0;
  }

  function testSaveLoad() {
    var state = createState(42);
    state.reservoir = 500;
    testBuyWeftling(state, DATA.weftlingTypes.GLIMSPINNER, 100, 100);
    var saved = testSaveState(state);
    var loaded = testLoadState(saved);
    return loaded.reservoir === 500 && loaded.weftlings.length === 1;
  }

  function testVictory() {
    var state = createState(42);
    state.reservoir = 10000;
    state.phase = 4;
    state.totalGlimCaptured = 10000;
    state.ownedClassCount = 5;
    state.maxCapacity = 1000;
    state.reservoir = state.maxCapacity;
    for (var i = 0; i < 12; i++) {
      testBuyUpgrade(state, 'WeftlingEfficiency');
    }
    testStep(state, 600);
    return state.victory;
  }

  window.GW.Simulation = {
    TICK_MS: TICK_MS,
    init: init,
    step: step,
    handleAction: handleAction,
    getProductionRate: getProductionRate,
    getCaptureRate: getCaptureRate,
    getFadeRate: getFadeRate,
    getPressure: getPressure,
    checkVictory: checkVictory,
    getMotes: getMotes,
    getPhase: getPhase,
    spawnMote: spawnMote,
    removeMote: removeMote,
    tryAdvancePhase: tryAdvancePhase,
    retune: retune
  };

  window.__glimweaveTest = {
    createState: createState,
    cloneState: cloneState,
    step: testStep,
    stepUntil: testStepUntil,
    buyWeftling: testBuyWeftling,
    buyUpgrade: testBuyUpgrade,
    chooseDoctrine: testChooseDoctrine,
    retune: testRetune,
    activateAbility: testActivateAbility,
    getProductionRate: testGetProductionRate,
    getCaptureRate: testGetCaptureRate,
    getFadeRate: getFadeRate,
    getPressure: testGetPressure,
    getMoteCount: testGetMoteCount,
    getReservoir: testGetReservoir,
    getPhase: testGetPhase,
    isVictory: testIsVictory,
    applyOfflineProgress: testApplyOfflineProgress,
    saveState: testSaveState,
    loadState: testLoadState,
    validateState: testValidateState,
    assertStateInvariants: testAssertStateInvariants,
    testProductionCaptureIndependence: testProductionCaptureIndependence,
    testFadeImpact: testFadeImpact,
    testOverflow: testOverflow,
    testUnitPurchase: testUnitPurchase,
    testUpgradePurchase: testUpgradePurchase,
    testDoctrineLock: testDoctrineLock,
    testPhaseProgression: testPhaseProgression,
    testRetuning: testRetuning,
    testOfflineProgress: testOfflineProgress,
    testSaveLoad: testSaveLoad,
    testVictory: testVictory
  };
})();

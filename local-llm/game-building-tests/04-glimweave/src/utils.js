(function() {
  'use strict';

  if (typeof window.GW === 'undefined') {
    window.GW = {};
  }
  if (typeof window.GW.Utils === 'undefined') {
    window.GW.Utils = {};
  }

  (function() {
    var state = 0;
    var RNG = {
      seed: function(seed) {
        if (typeof seed === 'string') {
          var h = 0;
          for (var i = 0; i < seed.length; i++) {
            h = Math.imul(31, h) + seed.charCodeAt(i) | 0;
          }
          state = h >>> 0;
        } else if (typeof seed === 'number') {
          state = seed >>> 0;
        }
        if (state === 0) state = 1;
      },

      random: function() {
        state = (Math.imul(state, 6364136223846793005) + 1) >>> 0;
        var z = state;
        z = (z ^ (z >>> 15)) & 0xFFFFFFFF;
        z = (z * 0x45D9F3B) & 0xFFFFFFFF;
        z = z ^ (z >>> 16);
        return (z >>> 0) / 4294967296;
      },

      integer: function(min, max) {
        if (typeof min !== 'number' || typeof max !== 'number' || !isFinite(min) || !isFinite(max)) {
          throw new Error('RNG.integer: min and max must be finite numbers');
        }
        if (min >= max) {
          throw new Error('RNG.integer: min must be less than max');
        }
        return Math.floor(this.random() * (max - min)) + min;
      },

      choice: function(array) {
        if (!Array.isArray(array) || array.length === 0) {
          throw new Error('RNG.choice: requires non-empty array');
        }
        return array[this.integer(0, array.length)];
      }
    };
    window.GW.Utils.RNG = RNG;
  })();

  window.GW.Utils.formatNumber = function(value, precision) {
    if (typeof value !== 'number' || !isFinite(value)) {
      throw new Error('formatNumber: value must be a finite number');
    }
    if (typeof precision === 'undefined') precision = 1;
    if (value < 1000 && value >= -1000) {
      return Math.floor(value).toString();
    }
    var absValue = Math.abs(value);
    var sign = value < 0 ? '-' : '';
    var tier = Math.floor(Math.log10(absValue) / 3);
    var units = ['', 'K', 'M', 'B'];
    if (tier >= units.length) tier = units.length - 1;
    var scaled = value / Math.pow(1000, tier);
    return sign + scaled.toFixed(precision) + units[tier];
  };

  window.GW.Utils.formatGlim = function(value) {
    return window.GW.Utils.formatNumber(value);
  };

  window.GW.Utils.formatTime = function(seconds) {
    if (typeof seconds !== 'number' || !isFinite(seconds)) {
      throw new Error('formatTime: seconds must be a finite number');
    }
    var totalSeconds = Math.floor(Math.abs(seconds));
    var h = Math.floor(totalSeconds / 3600);
    var m = Math.floor((totalSeconds % 3600) / 60);
    var s = Math.floor(totalSeconds % 60);
    var pad = function(n) {
      return n.toString().padStart(2, '0');
    };
    if (h > 0) {
      return h + ':' + pad(m) + ':' + pad(s);
    }
    return m + ':' + pad(s);
  };

  window.GW.Utils.distance = function(x1, y1, x2, y2) {
    if (typeof x1 !== 'number' || typeof y1 !== 'number' || typeof x2 !== 'number' || typeof y2 !== 'number' ||
        !isFinite(x1) || !isFinite(y1) || !isFinite(x2) || !isFinite(y2)) {
      throw new Error('distance: all arguments must be finite numbers');
    }
    var dx = x2 - x1;
    var dy = y2 - y1;
    return Math.sqrt(dx * dx + dy * dy);
  };

  window.GW.Utils.clamp = function(value, min, max) {
    if (typeof value !== 'number' || typeof min !== 'number' || typeof max !== 'number' ||
        !isFinite(value) || !isFinite(min) || !isFinite(max)) {
      throw new Error('clamp: all arguments must be finite numbers');
    }
    if (min > max) {
      throw new Error('clamp: min must be <= max');
    }
    if (value < min) return min;
    if (value > max) return max;
    return value;
  };

  window.GW.Utils.createSpatialHash = function(cellSize) {
    if (typeof cellSize !== 'number' || cellSize <= 0 || !isFinite(cellSize)) {
      throw new Error('createSpatialHash: cellSize must be a positive finite number');
    }
    var grid = {};
    var cell = cellSize;

    return {
      insert: function(x, y, item) {
        if (typeof x !== 'number' || typeof y !== 'number' || !isFinite(x) || !isFinite(y)) {
          throw new Error('insert: x and y must be finite numbers');
        }
        var cx = Math.floor(x / cell);
        var cy = Math.floor(y / cell);
        var key = cx + ',' + cy;
        if (!grid[key]) {
          grid[key] = [];
        }
        grid[key].push(item);
      },

      query: function(x, y, radius) {
        if (typeof x !== 'number' || typeof y !== 'number' || typeof radius !== 'number' ||
            !isFinite(x) || !isFinite(y) || !isFinite(radius)) {
          throw new Error('query: all arguments must be finite numbers');
        }
        if (radius < 0) {
          throw new Error('query: radius must be non-negative');
        }
        var results = [];
        var minCx = Math.floor((x - radius) / cell);
        var maxCx = Math.floor((x + radius) / cell);
        var minCy = Math.floor((y - radius) / cell);
        var maxCy = Math.floor((y + radius) / cell);
        for (var cx = minCx; cx <= maxCx; cx++) {
          for (var cy = minCy; cy <= maxCy; cy++) {
            var key = cx + ',' + cy;
            if (grid[key]) {
              var cellCenterX = (cx + 0.5) * cell;
              var cellCenterY = (cy + 0.5) * cell;
              if (window.GW.Utils.distance(x, y, cellCenterX, cellCenterY) <= radius + cell * Math.SQRT2 / 2) {
                results = results.concat(grid[key]);
              }
            }
          }
        }
        return results;
      },

      clear: function() {
        grid = {};
      }
    };
  };

  window.GW.Utils.validateGameData = function() {
    var DATA = window.GW.DATA;
    if (typeof DATA === 'undefined') {
      throw new Error('validateGameData: GW.DATA is not loaded');
    }

    var errors = [];

    var collectIds = function(obj) {
      var ids = {};
      for (var key in obj) {
        if (obj.hasOwnProperty(key)) {
          ids[key] = true;
        }
      }
      return ids;
    };

    var checkUniqueIds = function(category, data) {
      var ids = {};
      for (var id in data) {
        if (data.hasOwnProperty(id)) {
          if (ids[id]) {
            errors.push('Duplicate id "' + id + '" in ' + category);
          }
          ids[id] = true;
        }
      }
    };

    var weftlings = DATA.weftlings;
    if (weftlings) {
      checkUniqueIds('weftlings', weftlings);
      for (var wid in weftlings) {
        if (weftlings.hasOwnProperty(wid)) {
          var w = weftlings[wid];
          if (typeof w.unlock !== 'undefined') {
            if (typeof w.unlock.phase !== 'undefined') {
              if (w.unlock.phase < 1 || w.unlock.phase > 4) {
                errors.push('weftling ' + wid + ': unlock.phase must be 1-4, got ' + w.unlock.phase);
              }
            }
            if (typeof w.unlock.totalGlimCaptured !== 'undefined') {
              if (w.unlock.totalGlimCaptured <= 0) {
                errors.push('weftling ' + wid + ': unlock.totalGlimCaptured must be > 0, got ' + w.unlock.totalGlimCaptured);
              }
            }
          }
        }
      }
    }

    var globalUpgrades = DATA.globalUpgrades;
    if (globalUpgrades) {
      checkUniqueIds('globalUpgrades', globalUpgrades);
      for (var gid in globalUpgrades) {
        if (globalUpgrades.hasOwnProperty(gid)) {
          var g = globalUpgrades[gid];
          if (typeof g.startCost !== 'number' || g.startCost <= 0 || !isFinite(g.startCost)) {
            errors.push('globalUpgrade ' + gid + ': startCost must be > 0, got ' + g.startCost);
          }
          if (typeof g.scaling !== 'number' || g.scaling <= 1.0 || !isFinite(g.scaling)) {
            errors.push('globalUpgrade ' + gid + ': scaling must be > 1.0, got ' + g.scaling);
          }
          if (typeof g.cap !== 'number' || g.cap < 0 || !isFinite(g.cap)) {
            errors.push('globalUpgrade ' + gid + ': cap must be >= 0, got ' + g.cap);
          }
        }
      }
    }

    var doctrineUpgrades = DATA.doctrineUpgrades;
    if (doctrineUpgrades) {
      for (var docName in doctrineUpgrades) {
        if (doctrineUpgrades.hasOwnProperty(docName)) {
          var docUpgrades = doctrineUpgrades[docName];
          if (!Array.isArray(docUpgrades)) {
            errors.push('doctrineUpgrades.' + docName + ' must be an array');
            continue;
          }
          var docIds = {};
          for (var i = 0; i < docUpgrades.length; i++) {
            var du = docUpgrades[i];
            if (typeof du.id !== 'string') {
              errors.push('doctrineUpgrades.' + docName + '[' + i + ']: missing or invalid id');
              continue;
            }
            if (docIds[du.id]) {
              errors.push('doctrineUpgrades.' + docName + ': duplicate id "' + du.id + '"');
            }
            docIds[du.id] = true;

            if (typeof du.startCost !== 'number' || du.startCost <= 0 || !isFinite(du.startCost)) {
              errors.push('doctrineUpgrade ' + du.id + ': startCost must be > 0, got ' + du.startCost);
            }
            if (typeof du.scaling !== 'number' || du.scaling <= 1.0 || !isFinite(du.scaling)) {
              errors.push('doctrineUpgrade ' + du.id + ': scaling must be > 1.0, got ' + du.scaling);
            }
            if (typeof du.cap !== 'number' || du.cap < 0 || !isFinite(du.cap)) {
              errors.push('doctrineUpgrade ' + du.id + ': cap must be >= 0, got ' + du.cap);
            }
            if (du.requires !== null && du.requires !== undefined) {
              if (typeof du.requires !== 'string' || !docIds[du.requires]) {
                errors.push('doctrineUpgrade ' + du.id + ': requires must reference another upgrade in the same doctrine, got "' + du.requires + '"');
              }
            }
          }
        }
      }
    }

    var permanentUpgrades = DATA.permanentUpgrades;
    if (permanentUpgrades) {
      checkUniqueIds('permanentUpgrades', permanentUpgrades);
      for (var pid in permanentUpgrades) {
        if (permanentUpgrades.hasOwnProperty(pid)) {
          var p = permanentUpgrades[pid];
          if (typeof p.cost !== 'number' || p.cost < 1 || !isFinite(p.cost)) {
            errors.push('permanentUpgrade ' + pid + ': cost must be >= 1, got ' + p.cost);
          }
        }
      }
    }

    var colorblindModes = DATA.colorblindModes;
    if (colorblindModes) {
      var modeCount = Object.keys(colorblindModes).length;
      if (modeCount !== 3) {
        errors.push('colorblindModes: must have exactly 3 modes, got ' + modeCount);
      }
    }

    var phaseThresholds = DATA.phaseThresholds;
    if (phaseThresholds) {
      var validPhases = { '2': true, '3': true, '4': true };
      var lastThreshold = -1;
      for (var phaseKey in phaseThresholds) {
        if (phaseThresholds.hasOwnProperty(phaseKey)) {
          if (!validPhases[phaseKey]) {
            errors.push('phaseThresholds: invalid phase key "' + phaseKey + '", must be 2, 3, or 4');
          }
          var pt = phaseThresholds[phaseKey];
          if (typeof pt.totalGlimCaptured !== 'number' || !isFinite(pt.totalGlimCaptured)) {
            errors.push('phaseThresholds.' + phaseKey + ': totalGlimCaptured must be a number');
          } else {
            if (pt.totalGlimCaptured <= lastThreshold) {
              errors.push('phaseThresholds: totalGlimCaptured must be monotonically increasing, ' + phaseKey + ' has ' + pt.totalGlimCaptured + ' which is <= ' + lastThreshold);
            }
            lastThreshold = pt.totalGlimCaptured;
          }
        }
      }
    }

    if (errors.length > 0) {
      throw new Error('Game data validation failed:\n' + errors.join('\n'));
    }
  };

  window.GW.Utils.uuid = function() {
    var bytes = new Array(16);
    for (var i = 0; i < 16; i++) {
      bytes[i] = window.GW.Utils.RNG.integer(0, 256);
    }
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    var hex = function(b) {
      return ('0' + b.toString(16)).slice(-2);
    };
    return hex(bytes[0]) + hex(bytes[1]) + hex(bytes[2]) + hex(bytes[3]) + '-' +
           hex(bytes[4]) + hex(bytes[5]) + '-' +
           hex(bytes[6]) + hex(bytes[7]) + '-' +
           hex(bytes[8]) + hex(bytes[9]) + '-' +
           hex(bytes[10]) + hex(bytes[11]) + hex(bytes[12]) + hex(bytes[13]) + hex(bytes[14]) + hex(bytes[15]);
  };

  window.GW.Utils.hashCode = function(str) {
    if (typeof str !== 'string') {
      throw new Error('hashCode: requires a string');
    }
    var hash = 0;
    if (str.length === 0) return hash;
    for (var i = 0; i < str.length; i++) {
      var char = str.charCodeAt(i);
      hash = (Math.imul(hash, 31) + char) | 0;
    }
    return hash;
  };
})();

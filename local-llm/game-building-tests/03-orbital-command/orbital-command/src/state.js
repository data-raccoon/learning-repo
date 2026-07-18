(function () {
  'use strict';
  window.OC = window.OC || {};
  const SAVE_KEY = 'orbital-command-save-v1';
  const clone = value => JSON.parse(JSON.stringify(value));
  function createInitialState(data) {
    const total = Number(data.world.crew_total), engineering = Math.floor(total / 3), science = Math.floor(total / 3);
    return { version: 1, turn: 1, resources: clone(data.world.starting_resources), crew: { engineering, science, operations: total - engineering - science }, modules: [], completedTech: [], activeResearch: null, researchProgress: 0, log: [`Cycle 1: Command transferred to ${data.world.station_name}.`], pendingEvent: null, zeroStreak: { energy: 0, morale: 0 }, status: 'playing' };
  }
  function validateState(value, data) {
    if (!value || value.version !== 1 || !Number.isInteger(value.turn) || value.turn < 1) return false;
    if (!value.resources || !['energy','alloys','science','credits','morale'].every(key => Number.isFinite(value.resources[key]))) return false;
    if (!value.crew || !['engineering','science','operations'].every(key => Number.isInteger(value.crew[key]) && value.crew[key] >= 0)) return false;
    if (Object.values(value.crew).reduce((sum, count) => sum + count, 0) !== data.world.crew_total) return false;
    if (!Array.isArray(value.modules) || !Array.isArray(value.completedTech) || !Array.isArray(value.log)) return false;
    if (value.activeResearch !== null && typeof value.activeResearch !== 'string') return false;
    if (!Number.isFinite(value.researchProgress) || value.researchProgress < 0) return false;
    if (!value.zeroStreak || !['energy','morale'].every(key => Number.isInteger(value.zeroStreak[key]) && value.zeroStreak[key] >= 0)) return false;
    if (!['playing','won','lost'].includes(value.status)) return false;
    return value.pendingEvent === null || (typeof value.pendingEvent === 'object' && Array.isArray(value.pendingEvent.choices));
  }
  function saveState(state) { if (!validateState(state, window.OC_DATA)) return false; try { localStorage.setItem(SAVE_KEY, JSON.stringify(state)); return true; } catch (_) { return false; } }
  function loadState(data) { try { const parsed = JSON.parse(localStorage.getItem(SAVE_KEY)); return validateState(parsed, data) ? parsed : createInitialState(data); } catch (_) { return createInitialState(data); } }
  function clearSave() { try { localStorage.removeItem(SAVE_KEY); return true; } catch (_) { return false; } }
  Object.assign(window.OC, { createInitialState, validateState, saveState, loadState, clearSave });
})();

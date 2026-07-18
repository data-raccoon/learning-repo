(function () {
  'use strict';
  let engine;
  const data = window.OC_DATA, byId = id => document.getElementById(id);
  const node = (tag, className, text) => { const item = document.createElement(tag); if (className) item.className = className; if (text !== undefined) item.textContent = text; return item; };
  const deltaText = values => Object.entries(values).filter(([, value]) => value).map(([key, value]) => `${key} ${value > 0 ? '+' : ''}${value}`).join(' · ');
  function button(label, action, id, disabled, delta) { const item = node('button', 'action-button', label); item.type = 'button'; item.dataset.action = action; item.dataset.id = id; if (delta !== undefined) item.dataset.delta = delta; item.disabled = disabled; return item; }

  function renderModules() {
    const list = byId('module-list'); list.replaceChildren();
    data.modules.forEach(module => {
      const card = node('article', 'game-card module-card');
      card.append(node('h3', '', module.name), node('p', '', module.description), node('small', 'cost', `Cost: ${deltaText(module.cost)}`), node('small', 'production', `Output: ${deltaText(module.production)}`));
      const owned = engine.state.modules.filter(id => id === module.id).length;
      card.append(button(owned ? `Build another (${owned} owned)` : 'Construct', 'build', module.id, !engine.canBuild(module.id))); list.append(card);
    });
  }
  function renderTech() {
    const list = byId('tech-list'); list.replaceChildren();
    data.technologies.forEach(tech => {
      const card = node('article', 'game-card tech-card'), complete = engine.state.completedTech.includes(tech.id), active = engine.state.activeResearch === tech.id;
      card.append(node('h3', '', tech.name), node('p', '', tech.description), node('small', 'research-status', complete ? 'Completed' : active ? `${engine.state.researchProgress}/${tech.cost}` : `Cost: ${tech.cost} progress`));
      card.append(button(active ? 'In progress' : complete ? 'Researched' : 'Research', 'research', tech.id, !engine.canResearch(tech.id))); list.append(card);
    });
  }
  function renderCrew() {
    const list = byId('crew-list'); list.replaceChildren();
    data.world.roles.forEach(role => {
      const card = node('article', 'game-card crew-card'), controls = node('div', 'crew-controls');
      card.append(node('h3', '', role.name), node('p', '', role.description));
      controls.append(button('−', 'crew', role.id, engine.state.crew[role.id] === 0, -1), node('strong', 'crew-count', String(engine.state.crew[role.id])), button('+', 'crew', role.id, false, 1));
      card.append(controls); list.append(card);
    });
  }
  function renderMissions() {
    const list = byId('mission-list'); list.replaceChildren();
    data.world.mission_goals.forEach(goal => { const current = engine.state.resources[goal.resource], card = node('article', 'game-card mission-card'), progress = node('progress'); progress.max = goal.target; progress.value = Math.min(current, goal.target); card.append(node('h3', '', goal.label), node('p', '', `${current} / ${goal.target}`), progress); list.append(card); });
  }
  function renderEvent() {
    const modal = byId('event-modal'), event = engine.state.pendingEvent;
    if (!event) { if (modal.open) modal.close(); return; }
    byId('event-title').textContent = event.title; byId('event-text').textContent = event.text;
    const choices = byId('event-choices'); choices.replaceChildren();
    event.choices.forEach((choice, index) => { const item = button(choice.label, 'event', String(index), false); item.append(node('small', '', deltaText(choice.effects))); choices.append(item); });
    if (!modal.open) modal.showModal();
  }
  function render() {
    byId('turn').textContent = engine.state.turn;
    ['energy','alloys','science','credits','morale'].forEach(key => { byId(key).textContent = engine.state.resources[key]; });
    byId('subtitle').textContent = `${data.copy.subtitle} — ${data.world.station_name}`; byId('help').textContent = data.copy.help_text;
    renderModules(); renderTech(); renderCrew(); renderMissions();
    const log = byId('event-log'); log.replaceChildren(...engine.state.log.slice(0, 10).map(entry => node('li', '', entry))); renderEvent();
    const banner = byId('game-banner'); banner.hidden = engine.state.status === 'playing'; banner.textContent = engine.state.status === 'won' ? data.copy.victory_message : engine.state.status === 'lost' ? data.copy.loss_message : '';
    byId('advance-turn').disabled = engine.state.status !== 'playing' || Boolean(engine.state.pendingEvent);
  }
  function commit(message) { window.OC.saveState(engine.state); render(); byId('announcer').textContent = message; }
  function newGame() { window.OC.clearSave(); engine = new window.OC.Engine(data, window.OC.createInitialState(data)); render(); byId('announcer').textContent = 'New campaign started.'; return engine; }
  function handleAction(event) {
    const control = event.target.closest('[data-action]'); if (!control) return;
    const { action, id } = control.dataset; let changed = false;
    if (action === 'build') changed = engine.build(id); else if (action === 'research') changed = engine.research(id); else if (action === 'crew') changed = engine.assignCrew(id, Number(control.dataset.delta)); else if (action === 'event') changed = engine.chooseEvent(Number(id));
    if (changed) commit('Station state updated.');
  }
  addEventListener('DOMContentLoaded', () => {
    engine = new window.OC.Engine(data, window.OC.loadState(data));
    document.querySelector('main').addEventListener('click', handleAction); byId('event-choices').addEventListener('click', handleAction);
    byId('advance-turn').addEventListener('click', () => { if (engine.advanceTurn()) commit('Cycle advanced.'); }); byId('reset-game').addEventListener('click', newGame);
    window.__orbitalTest = { get engine() { return engine; }, render, newGame }; render();
  });
})();

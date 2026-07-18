(function () {
  'use strict';
  window.OC = window.OC || {};

  const resourceKeys = ['energy', 'alloys', 'science', 'credits', 'morale'];
  const clone = value => JSON.parse(JSON.stringify(value));

  class Engine {
    constructor(data, state) {
      this.data = data;
      this.state = state;
    }

    moduleById(id) { return this.data.modules.find(item => item.id === id); }
    techById(id) { return this.data.technologies.find(item => item.id === id); }
    log(message) {
      this.state.log.unshift(`Cycle ${this.state.turn}: ${message}`);
      this.state.log = this.state.log.slice(0, 40);
    }

    canBuild(id) {
      const module = this.moduleById(id);
      if (!module || this.state.status !== 'playing' || this.state.pendingEvent) return false;
      if (module.required_tech && !this.state.completedTech.includes(module.required_tech)) return false;
      return Object.entries(module.cost).every(([key, value]) => (this.state.resources[key] || 0) >= value);
    }

    build(id) {
      if (!this.canBuild(id)) return false;
      const module = this.moduleById(id);
      Object.entries(module.cost).forEach(([key, value]) => { this.state.resources[key] -= value; });
      this.state.modules.push(id);
      this.log(`Constructed ${module.name}.`);
      return true;
    }

    canResearch(id) {
      const tech = this.techById(id);
      if (!tech || this.state.status !== 'playing' || this.state.pendingEvent) return false;
      if (this.state.completedTech.includes(id) || this.state.activeResearch) return false;
      return !tech.prerequisite || this.state.completedTech.includes(tech.prerequisite);
    }

    research(id) {
      if (!this.canResearch(id)) return false;
      this.state.activeResearch = id;
      this.state.researchProgress = 0;
      this.log(`Research started: ${this.techById(id).name}.`);
      return true;
    }

    assignCrew(role, delta) {
      if (!Object.hasOwn(this.state.crew, role) || !Number.isInteger(delta) || Math.abs(delta) !== 1) return false;
      const others = Object.keys(this.state.crew).filter(key => key !== role);
      if (delta > 0) {
        const donor = others.sort((a, b) => this.state.crew[b] - this.state.crew[a])[0];
        if (!donor || this.state.crew[donor] < 1) return false;
        this.state.crew[donor] -= 1;
        this.state.crew[role] += 1;
      } else {
        if (this.state.crew[role] < 1) return false;
        const receiver = others.sort((a, b) => this.state.crew[a] - this.state.crew[b])[0];
        this.state.crew[role] -= 1;
        this.state.crew[receiver] += 1;
      }
      this.log('Crew assignments adjusted.');
      return true;
    }

    productionForTurn() {
      const totals = Object.fromEntries(resourceKeys.map(key => [key, 0]));
      this.state.modules.forEach(id => {
        const module = this.moduleById(id);
        if (module) resourceKeys.forEach(key => { totals[key] += Number(module.production[key] || 0); });
      });
      totals.energy += Math.floor(this.state.crew.engineering / 3);
      totals.science += Math.floor(this.state.crew.science / 3);
      totals.credits += Math.floor(this.state.crew.operations / 4);
      this.state.completedTech.forEach(id => {
        const effect = this.techById(id)?.effect;
        if (effect && effect.type === 'production_bonus' && Object.hasOwn(totals, effect.resource)) {
          totals[effect.resource] += Number(effect.amount || 0);
        }
        if (effect && effect.type === 'morale_bonus') totals.morale += Number(effect.amount || 0);
      });
      resourceKeys.forEach(key => { this.state.resources[key] += totals[key]; });
    }

    progressResearch() {
      if (!this.state.activeResearch) return;
      const tech = this.techById(this.state.activeResearch);
      if (!tech) { this.state.activeResearch = null; return; }
      this.state.researchProgress += this.state.crew.science + 2;
      if (this.state.researchProgress >= tech.cost) {
        this.state.completedTech.push(tech.id);
        this.state.activeResearch = null;
        this.state.researchProgress = 0;
        this.log(`Research completed: ${tech.name}.`);
      }
    }

    chooseEvent(choiceIndex) {
      const event = this.state.pendingEvent;
      const choice = event?.choices?.[choiceIndex];
      if (!choice) return false;
      resourceKeys.forEach(key => { this.state.resources[key] += Number(choice.effects[key] || 0); });
      this.log(`${event.title}: ${choice.label}.`);
      this.state.pendingEvent = null;
      this.clampAndEvaluate();
      return true;
    }

    clampAndEvaluate() {
      resourceKeys.forEach(key => { this.state.resources[key] = Math.max(0, Number(this.state.resources[key] || 0)); });
      this.state.resources.morale = Math.min(100, this.state.resources.morale);
      ['energy', 'morale'].forEach(key => {
        this.state.zeroStreak[key] = this.state.resources[key] === 0 ? this.state.zeroStreak[key] + 1 : 0;
      });
      if (this.state.zeroStreak.energy >= 2 || this.state.zeroStreak.morale >= 2) {
        this.state.status = 'lost';
        this.log(this.data.copy.loss_message);
        return;
      }
      const won = this.data.world.mission_goals.every(goal => this.state.resources[goal.resource] >= goal.target);
      if (won) { this.state.status = 'won'; this.log(this.data.copy.victory_message); }
    }

    advanceTurn() {
      if (this.state.status !== 'playing' || this.state.pendingEvent) return false;
      this.state.turn += 1;
      this.productionForTurn();
      this.progressResearch();
      this.clampAndEvaluate();
      if (this.state.status === 'playing' && this.state.turn % 3 === 0) {
        const index = (this.state.turn / 3 - 1) % this.data.events.length;
        const event = this.data.events[index];
        if (event && this.state.turn >= event.min_turn) this.state.pendingEvent = clone(event);
      }
      this.log('Cycle advanced.');
      return true;
    }

    snapshot() { return clone(this.state); }
  }

  window.OC.Engine = Engine;
})();

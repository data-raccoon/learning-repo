(function() {
  'use strict';
  if (typeof window.GW === 'undefined') return;
  var GW = window.GW;
  if (GW.Integration && GW.Integration.installed) return;
  GW.Integration = { installed: true };

  var d = GW_DATA.doctrines;
  var ok = Object.keys(d);
  var oha = GW.Simulation.handleAction;
  var pu = GW_DATA.permanentUpgrades;
  var brc = GW_DATA.constants.baseReservoirCapacity;

  ok.forEach(function(k) {
    var dv = d[k];
    Object.defineProperty(d, dv, { value: dv, enumerable: false, configurable: false, writable: false });
  });

  GW.Simulation.handleAction = function(s, a) {
    if (a.type === 'CHOOSE_DOCTRINE') {
      var ca = { type: a.type, doctrineId: a.doctrineId };
      if (ok.indexOf(ca.doctrineId) >= 0) ca.doctrineId = d[ca.doctrineId];
      return oha(s, ca);
    }

    if (a.type === 'BUY_UPGRADE' && pu[a.upgradeId]) {
      var ud = pu[a.upgradeId];
      if (typeof ud.cost !== 'number' || !isFinite(ud.cost) || ud.cost < 0 || ud.cost !== Math.floor(ud.cost)) throw new Error('Invalid cost');
      if (typeof s.iridescence !== 'number' || !isFinite(s.iridescence) || s.iridescence < 0 || s.iridescence < ud.cost) throw new Error('Insufficient iridescence');
      var o = s.permanentUpgrades || [];
      if (!ud.stackable && o.indexOf(a.upgradeId) >= 0) throw new Error('Already owned non-stackable upgrade');
      s.iridescence -= ud.cost;
      s.permanentUpgrades = o.concat(a.upgradeId);
      if (a.upgradeId === 'ReservoirBlueprint') {
        var oc = o.filter(function(id) { return id === 'ReservoirBlueprint'; }).length;
        var nc = oc + 1;
        var cm = s.maxCapacity || brc;
        var bg = cm - oc * 100;
        if (bg < brc) bg = brc;
        s.maxCapacity = bg + nc * 100;
        if (s.reservoir > s.maxCapacity) s.reservoir = s.maxCapacity;
      }
      GW.State.validate(s);
      return s;
    }

    if (a.type === 'RETUNE') {
      var r = oha(s, a);
      if (r && r.success) {
        s.maxCapacity = s.baseCapacity;
        if (s.reservoir > s.maxCapacity) s.reservoir = s.maxCapacity;
        GW.State.validate(s);
      }
      return r;
    }

    return oha(s, a);
  };
})();

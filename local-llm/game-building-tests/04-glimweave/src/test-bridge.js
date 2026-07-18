(function() {
  if (!/[?&]smoke(=|&|$)/.test(location.search)) return;
  var gw = window.GW;
  if (!gw || 'object' !== typeof gw) gw = window.GW = {};
  if (Object.prototype.hasOwnProperty.call(gw, '__glimweaveTestBackup')) {
    window.__glimweaveTest = gw.__glimweaveTestBackup;
  } else if (window.__glimweaveTest) {
    gw.__glimweaveTestBackup = window.__glimweaveTest;
  }
})()

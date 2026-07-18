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
        check(document.querySelector('#announcer').getAttribute('aria-live') === 'polite', 'ARIA_LIVE');
        check(getComputedStyle(document.body).backgroundColor !== '', 'CSS_LOADED');
      } catch (error) {
        var trace = String(error.stack || '').split('\n').slice(1, 4).join('_').slice(0, 220).replace(/\W+/g, '_').toUpperCase();
        failures.push('RUNTIME_' + phase + '_' + error.name + '_' + String(error.message || '').slice(0, 320).replace(/\W+/g, '_').toUpperCase() + '_' + trace);
      }
      window.setTimeout(function () {
        try {
          phase = 'UI_PROFILE';
          var canvas = document.querySelector('#gameCanvas');
          var rect = canvas.getBoundingClientRect();
          check(rect.width > 0 && rect.height > 0, 'CANVAS_DIMENSIONS');
          check(getComputedStyle(canvas).display !== 'none', 'CANVAS_DISPLAYED');

          var leftCol = document.querySelector('.left-column');
          var rightCol = document.querySelector('.right-column');
          check(!!leftCol && !!rightCol, 'COLUMNS_EXIST');
          if (leftCol && rightCol) {
            var leftRect = leftCol.getBoundingClientRect();
            var rightRect = rightCol.getBoundingClientRect();
            var canvasRect = canvas.getBoundingClientRect();
            var leftRightEdge = leftRect.right;
            var rightLeftEdge = rightRect.left;
            var gap = rightLeftEdge - leftRightEdge;
            check(gap >= 300, 'CENTRAL_GAP_300PX');
            var gapLeft = Math.max(leftRightEdge, canvasRect.left);
            var gapRight = Math.min(rightLeftEdge, canvasRect.right);
            check(gapRight > gapLeft, 'GAP_OVERLAPS_CANVAS');
          }

          var reservoirEl = document.querySelector('[data-testid="reservoir-display"]') || document.querySelector('#reservoirValue') || Array.from(document.querySelectorAll('*')).find(function(el) { return String(el.textContent || '').trim().match(/(?:Reservoir|reservoir):\s*100/); });
          check(!!reservoirEl, 'RESERVOIR_ELEMENT');
          var initialReservoir = parseInt(String(reservoirEl.textContent || '').replace(/\D/g, ''), 10);
          check(initialReservoir === 100, 'RESERVOIR_INITIAL_100');

          var glimspinnerBtn = document.querySelector('#purchaseList button[aria-label^="Buy Glimspinner"]');
          var driftcatcherBtn = document.querySelector('#purchaseList button[aria-label^="Buy Driftcatcher"]');
          check(!!glimspinnerBtn && !!driftcatcherBtn, 'PURCHASE_BUTTONS_EXIST');
          check(glimspinnerBtn && !glimspinnerBtn.disabled && driftcatcherBtn && !driftcatcherBtn.disabled, 'PURCHASE_BUTTONS_ENABLED');

          var fnvHash = function(imageData) {
            var hash = 2166136261;
            for (var i = 0; i < imageData.data.length; i += 16) {
              hash ^= (imageData.data[i] + (imageData.data[i+1] << 8) + (imageData.data[i+2] << 16) + (imageData.data[i+3] << 24)) >>> 0;
              hash = Math.imul(hash, 16777619);
            }
            return hash >>> 0;
          };

          var canvasCtx = canvas.getContext('2d');
          var hashBefore = 0;
          if (canvasCtx) {
            var width = canvas.width;
            var height = canvas.height;
            var sampleImageData = canvasCtx.getImageData(0, 0, width, height);
            hashBefore = fnvHash(sampleImageData);
          }

          glimspinnerBtn.click();
          window.setTimeout(function () {
            try {
              var reservoirAfterGlimspinner = parseInt(String((document.querySelector('[data-testid="reservoir-display"]') || document.querySelector('#reservoirValue') || reservoirEl).textContent || '').replace(/\D/g, ''), 10);
              check(reservoirAfterGlimspinner === 55, 'RESERVOIR_AFTER_GLIMSPINNER_55');

              var driftcatcherBtnAfter = document.querySelector('#purchaseList button[aria-label^="Buy Driftcatcher"]');
              if (!driftcatcherBtnAfter) failures.push('DRIFTCATCHER_BTN_MISSING');
              else if (driftcatcherBtnAfter.disabled) failures.push('DRIFTCATCHER_BTN_DISABLED');
              else driftcatcherBtnAfter.click();
              window.setTimeout(function () {
                try {
                  var reservoirAfterDriftcatcher = parseInt(String((document.querySelector('[data-testid="reservoir-display"]') || document.querySelector('#reservoirValue') || reservoirEl).textContent || '').replace(/\D/g, ''), 10);
                  if (reservoirAfterDriftcatcher !== 0) {
                    var announcer = document.querySelector('#announcer');
                    var announcerText = String(announcer && announcer.textContent || '').replace(/\W+/g, '_').toUpperCase().slice(0, 140);
                    failures.push('RESERVOIR_AFTER_DRIFTCATCHER_' + reservoirAfterDriftcatcher + '_ACTION_MESSAGE_' + announcerText);
                    check(!!announcer && String(announcer.textContent || '').toLowerCase().includes('rejected'), 'ANNOUNCER_REJECTED_ACTION');
                  } else {
                    check(true, 'RESERVOIR_AFTER_DRIFTCATCHER_0');
                  }

                  var ownedGlimspinner = document.querySelector('[data-testid="owned-glimspinner"]') || Array.from(document.querySelectorAll('*')).find(function(el) { return String(el.textContent || '').toLowerCase().match(/glimspinner.*1/); });
                  var ownedDriftcatcher = document.querySelector('[data-testid="owned-driftcatcher"]') || Array.from(document.querySelectorAll('*')).find(function(el) { return String(el.textContent || '').toLowerCase().match(/driftcatcher.*1/); });
                  check(!!ownedGlimspinner || String(document.body.textContent || '').toLowerCase().includes('glimspinner') && String(document.body.textContent || '').toLowerCase().includes('1'), 'OWNED_GLIMSPINNER_VISIBLE');
                  check(!!ownedDriftcatcher || String(document.body.textContent || '').toLowerCase().includes('driftcatcher') && String(document.body.textContent || '').toLowerCase().includes('1'), 'OWNED_DRIFTCATCHER_VISIBLE');

                  window.setTimeout(function () {
                    try {
                      var hashAfter = 0;
                      if (canvasCtx) {
                        var width = canvas.width;
                        var height = canvas.height;
                        var sampleImageDataAfter = canvasCtx.getImageData(0, 0, width, height);
                        hashAfter = fnvHash(sampleImageDataAfter);
                      }
                      check(hashAfter !== hashBefore, 'CANVAS_PIXEL_CHANGED');
                    } catch (e) {
                      failures.push('PIXEL_CHECK_ERR');
                    }
                    var output = document.querySelector('#smoke-result');
                    output.textContent = failures.length ? 'FAIL:' + failures.join(',') : 'PASS';
                  }, 500);
                } catch (e) {
                  failures.push('AFTER_DRIFTCATCHER_ERR');
                  var output = document.querySelector('#smoke-result');
                  output.textContent = failures.length ? 'FAIL:' + failures.join(',') : 'PASS';
                }
              }, 200);
            } catch (e) {
              failures.push('AFTER_GLIMSPINNER_ERR');
              var output = document.querySelector('#smoke-result');
              output.textContent = failures.length ? 'FAIL:' + failures.join(',') : 'PASS';
            }
          }, 200);
        } catch (error) {
          var trace = String(error.stack || '').split('\n').slice(1, 4).join('_').slice(0, 220).replace(/\W+/g, '_').toUpperCase();
          failures.push('RUNTIME_' + phase + '_' + error.name + '_' + String(error.message || '').slice(0, 320).replace(/\W+/g, '_').toUpperCase() + '_' + trace);
          var output = document.querySelector('#smoke-result');
          output.textContent = failures.length ? 'FAIL:' + failures.join(',') : 'PASS';
        }
      }, 150);
    }, 150);
  });
})();

(function() {
  'use strict';

  if (window.GW) {
    window.GW.UI = window.GW.UI || {};
    window.GW.init = window.GW.init || function() {};
  } else {
    window.GW = { UI: {}, Utils: {}, State: {}, Simulation: {}, Renderer: {}, DATA: {}, VERSION: '1.0', TICK_MS: 100, FPS: 60, MAX_MOTES: 500, init: function() {} };
  }

  var UI = window.GW.UI;
  var GW = window.GW;
  var DATA = GW.DATA;
  var State = GW.State;
  var Simulation = GW.Simulation;
  var Utils = GW.Utils;
  var Renderer = GW.Renderer;

  var actionHandler = null;
  var rootElement = null;
  var state = null;
  var modalStack = [];
  var notificationQueue = [];
  var activeNotification = null;
  var lastAutoSave = 0;
  var lastRenderTime = 0;
  var simInterval = null;
  var renderId = null;
  var isInitialized = false;
  var visibilityState = true;
  var offlineReportShown = false;
  var tutorialElement = null;

  var speedMap = { 0.5: 0.5, 1: 1, 2: 2, 4: 4 };
  var speedKeys = [0.5, 1, 2, 4];
  var phaseNames = DATA.phases;
  var colorblindModes = DATA.colorblindModes;
  var colorblindModeOrder = ['default', 'high-contrast', 'deuteranopia-protanopia'];

  function getColorblindNext(current) {
    var idx = colorblindModeOrder.indexOf(current);
    return colorblindModeOrder[(idx + 1) % colorblindModeOrder.length];
  }

  function formatNumber(value) {
    if (value < 1000) return Math.floor(value).toString();
    var units = ['', 'K', 'M', 'B'];
    var tier = Math.floor(Math.log10(Math.abs(value)) / 3);
    var scaled = value / Math.pow(1000, tier);
    return scaled.toFixed(1) + units[tier];
  }

  function formatTime(seconds) {
    var h = Math.floor(seconds / 3600);
    var m = Math.floor((seconds % 3600) / 60);
    var s = Math.floor(seconds % 60);
    return h > 0
      ? h + ':' + m.toString().padStart(2, '0') + ':' + s.toString().padStart(2, '0')
      : m + ':' + s.toString().padStart(2, '0');
  }

  function formatGlim(value) {
    return formatNumber(value);
  }

  function formatRate(value) {
    if (value < 1) return value.toFixed(1);
    return formatNumber(value);
  }

  function createElement(tag, className, text) {
    var el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = text;
    return el;
  }

  function createButton(text, className, clickHandler, ariaLabel) {
    var btn = createElement('button', className || 'btn', text);
    btn.tabIndex = 0;
    if (ariaLabel) btn.setAttribute('aria-label', ariaLabel);
    if (clickHandler) btn.addEventListener('click', clickHandler);
    btn.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        clickHandler && clickHandler();
      }
    });
    return btn;
  }

  function createIconButton(icon, ariaLabel, clickHandler) {
    var btn = createElement('button', 'icon-btn');
    btn.innerHTML = '<span class="icon">' + icon + '</span>';
    btn.tabIndex = 0;
    btn.setAttribute('aria-label', ariaLabel);
    if (clickHandler) btn.addEventListener('click', clickHandler);
    btn.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        clickHandler && clickHandler();
      }
    });
    return btn;
  }

  function dispatchAction(action) {
    if (actionHandler && typeof actionHandler === 'function') {
      actionHandler(action);
    }
  }

  function notify(message, type) {
    notificationQueue.push({ message: message, type: type || 'info' });
    showNextNotification();
  }

  function showNextNotification() {
    if (activeNotification || notificationQueue.length === 0) return;
    var n = notificationQueue.shift();
    activeNotification = n;
    var notifyEl = document.getElementById('notification');
    if (!notifyEl) {
      notifyEl = createElement('div', 'notification', '');
      notifyEl.id = 'notification';
      notifyEl.setAttribute('aria-live', 'polite');
      rootElement.appendChild(notifyEl);
    }
    notifyEl.textContent = n.message;
    notifyEl.className = 'notification notification-' + n.type;
    notifyEl.style.display = 'block';
    setTimeout(function() {
      notifyEl.style.display = 'none';
      activeNotification = null;
      showNextNotification();
    }, 4000);
  }

  function announce(message) {
    var announcer = document.getElementById('announcer');
    if (announcer) {
      announcer.textContent = message;
    }
  }

  function showModal(title, message, buttons) {
    var modal = createElement('div', 'modal-overlay');
    modal.setAttribute('aria-label', title);
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');

    var content = createElement('div', 'modal');
    var header = createElement('div', 'modal-header');
    var titleEl = createElement('h2', '', title);
    header.appendChild(titleEl);
    content.appendChild(header);

    var body = createElement('div', 'modal-body');
    var msgEl = createElement('p', '', message);
    body.appendChild(msgEl);
    content.appendChild(body);

    var footer = createElement('div', 'modal-footer');
    buttons = buttons || [{ text: 'OK', callback: function() {} }];
    buttons.forEach(function(btn) {
      var btnEl = createButton(btn.text, 'btn', btn.callback);
      footer.appendChild(btnEl);
    });
    content.appendChild(footer);

    modal.appendChild(content);
    rootElement.appendChild(modal);

    modalStack.push(modal);

    var focusable = modal.querySelectorAll('[tabindex="0"]');
    if (focusable.length > 0) focusable[0].focus();

    var close = function() {
      var idx = modalStack.indexOf(modal);
      if (idx > -1) modalStack.splice(idx, 1);
      rootElement.removeChild(modal);
      if (modalStack.length > 0) {
        var last = modalStack[modalStack.length - 1];
        var lastFocusable = last.querySelectorAll('[tabindex="0"]');
        if (lastFocusable.length > 0) lastFocusable[0].focus();
      }
    };

    buttons.forEach(function(btn, i) {
      var btnEl = footer.children[i];
      btnEl.onclick = function() {
        btn.callback();
        close();
      };
    });

    modal.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        e.preventDefault();
        if (buttons.length === 0 || buttons[0].callback) {
          buttons[0].callback();
        }
        close();
      }
    });

    return close;
  }

  function hideModal() {
    if (modalStack.length > 0) {
      var modal = modalStack[modalStack.length - 1];
      rootElement.removeChild(modal);
      modalStack.pop();
    }
  }

  function showTutorialStep(stepId) {
    if (!tutorialElement) createTutorialOverlay();
    tutorialElement.style.display = 'flex';
    var stepEl = document.getElementById('tutorial-step-' + stepId);
    if (stepEl) {
      Array.prototype.forEach.call(tutorialElement.querySelectorAll('.tutorial-step'), function(el) {
        el.style.display = 'none';
      });
      stepEl.style.display = 'block';
    }
    announce('Tutorial: Step ' + stepId);
  }

  function hideTutorial() {
    if (tutorialElement) {
      tutorialElement.style.display = 'none';
      if (state) {
        state.tutorialStep = DATA.constants.tutorial.steps;
        state.settings.tutorialComplete = true;
      }
    }
  }

  function createTutorialOverlay() {
    tutorialElement = createElement('div', 'tutorial-overlay');
    tutorialElement.id = 'tutorial';
    tutorialElement.setAttribute('aria-label', 'Tutorial');
    tutorialElement.style.display = 'none';

    var container = createElement('div', 'tutorial-container');

    for (var i = 0; i <= DATA.constants.tutorial.steps; i++) {
      var step = createElement('div', 'tutorial-step');
      step.id = 'tutorial-step-' + i;
      step.style.display = i === 0 ? 'block' : 'none';

      var title = 'Welcome to Glimweave';
      var desc = '';
      switch(i) {
        case 0:
          title = 'Welcome to Glimweave';
          desc = 'Weave the Sky Loom to capture drifting Glim. Your first Weftling awaits.';
          break;
        case 1:
          title = 'Glimspinner';
          desc = 'The Glimspinner produces Glim. Purchase one to begin.';
          break;
        case 2:
          title = 'Driftcatcher';
          desc = 'Driftcatchers capture loose Glim. Buy one to prevent loss.';
          break;
        case 3:
          title = 'Balance';
          desc = 'Keep production and capture in balance to avoid overflow.';
          break;
        case 4:
          title = 'Phase Progression';
          desc = 'Capture Glim to unlock new phases and Weftling types.';
          break;
        case 5:
          title = 'Upgrades';
          desc = 'Permanent upgrades improve all your Weftlings.';
          break;
        case 6:
          title = 'Doctrines';
          desc = 'Choose a doctrine to specialize your strategy.';
          break;
        case 7:
          title = 'Retuning';
          desc = 'Reset for permanent bonuses while keeping some progress.';
          break;
        case 8:
          title = 'Victory';
          desc = 'Achieve all victory conditions to complete the game.';
          break;
      }

      var h = createElement('h2', '', title);
      var p = createElement('p', '', desc);
      step.appendChild(h);
      step.appendChild(p);

      if (i > 0) {
        var backBtn = createButton('Back', 'btn btn-secondary', function() {
          if (state) state.tutorialStep = i - 1;
          showTutorialStep(i - 1);
        });
        step.appendChild(backBtn);
      }

      if (i < DATA.constants.tutorial.steps) {
        var nextBtn = createButton('Next', 'btn btn-primary', function() {
          if (state) state.tutorialStep = i + 1;
          showTutorialStep(i + 1);
        });
        step.appendChild(nextBtn);
      } else {
        var doneBtn = createButton('Begin', 'btn btn-primary', function() {
          hideTutorial();
          if (state) {
            state.settings.tutorialComplete = true;
          }
        });
        step.appendChild(doneBtn);
      }

      container.appendChild(step);
    }

    var closeBtn = createButton('Close Tutorial', 'btn tutorial-close', function() {
      hideTutorial();
    });
    container.appendChild(closeBtn);

    tutorialElement.appendChild(container);
    rootElement.appendChild(tutorialElement);
  }

  function createStatsPanel() {
    var stats = createElement('section', 'stats-panel');

    var reservoirRow = createElement('div', 'stat-row');
    var reservoirLabel = createElement('span', 'stat-label', 'Reservoir:');
    var reservoirValue = createElement('span', 'stat-value');
    reservoirValue.id = 'reservoirValue';
    var reservoirMax = createElement('span', 'stat-max', '');
    reservoirMax.id = 'reservoirMax';
    reservoirRow.appendChild(reservoirLabel);
    reservoirRow.appendChild(reservoirValue);
    reservoirRow.appendChild(createElement('span', '', '/'));
    reservoirRow.appendChild(reservoirMax);
    stats.appendChild(reservoirRow);

    var reservoirBarContainer = createElement('div', 'stat-bar-container');
    var reservoirBar = createElement('div', 'stat-bar');
    reservoirBar.id = 'reservoirBar';
    var reservoirBarFill = createElement('div', 'stat-bar-fill');
    reservoirBarFill.id = 'reservoirBarFill';
    reservoirBar.appendChild(reservoirBarFill);
    reservoirBarContainer.appendChild(reservoirBar);
    stats.appendChild(reservoirBarContainer);

    var iridescenceRow = createElement('div', 'stat-row');
    var iridescenceLabel = createElement('span', 'stat-label', 'Iridescence:');
    var iridescenceValue = createElement('span', 'stat-value');
    iridescenceValue.id = 'iridescenceValue';
    iridescenceRow.appendChild(iridescenceLabel);
    iridescenceRow.appendChild(iridescenceValue);
    stats.appendChild(iridescenceRow);

    var productionRow = createElement('div', 'stat-row');
    var productionLabel = createElement('span', 'stat-label', 'Production:');
    var productionValue = createElement('span', 'stat-value');
    productionValue.id = 'productionValue';
    productionRow.appendChild(productionLabel);
    productionRow.appendChild(productionValue);

    var captureRow = createElement('div', 'stat-row');
    var captureLabel = createElement('span', 'stat-label', 'Capture:');
    var captureValue = createElement('span', 'stat-value');
    captureValue.id = 'captureValue';
    captureRow.appendChild(captureLabel);
    captureRow.appendChild(captureValue);

    var fadeRow = createElement('div', 'stat-row');
    var fadeLabel = createElement('span', 'stat-label', 'Fade:');
    var fadeValue = createElement('span', 'stat-value');
    fadeValue.id = 'fadeValue';
    fadeRow.appendChild(fadeLabel);
    fadeRow.appendChild(fadeValue);

    stats.appendChild(productionRow);
    stats.appendChild(captureRow);
    stats.appendChild(fadeRow);

    var phaseRow = createElement('div', 'stat-row');
    var phaseLabel = createElement('span', 'stat-label', 'Phase:');
    var phaseValue = createElement('span', 'stat-value');
    phaseValue.id = 'phaseValue';
    phaseRow.appendChild(phaseLabel);
    phaseRow.appendChild(phaseValue);
    stats.appendChild(phaseRow);

    var pressureRow = createElement('div', 'stat-row');
    var pressureLabel = createElement('span', 'stat-label', 'Pressure:');
    var pressureValue = createElement('span', 'stat-value');
    pressureValue.id = 'pressureValue';
    pressureRow.appendChild(pressureLabel);
    pressureRow.appendChild(pressureValue);
    stats.appendChild(pressureRow);

    return stats;
  }

  function createPurchasePanel() {
    var panel = createElement('section', 'panel purchase-panel');
    var header = createElement('h3', 'panel-header', 'Weftlings');
    panel.appendChild(header);

    var list = createElement('div', 'purchase-list');
    list.id = 'purchaseList';

    panel.appendChild(list);
    return panel;
  }

  function createUpgradesPanel() {
    var panel = createElement('section', 'panel upgrades-panel');
    var header = createElement('h3', 'panel-header', 'Global Upgrades');
    panel.appendChild(header);

    var list = createElement('div', 'upgrade-list');
    list.id = 'globalUpgradesList';
    panel.appendChild(list);
    return panel;
  }

  function createDoctrinePanel() {
    var panel = createElement('section', 'panel doctrine-panel');
    var header = createElement('h3', 'panel-header', 'Doctrine');
    panel.appendChild(header);

    var desc = createElement('p', 'panel-desc', 'Choose a doctrine to specialize your strategy. This cannot be undone.');
    panel.appendChild(desc);

    var list = createElement('div', 'doctrine-list');
    list.id = 'doctrineList';
    panel.appendChild(list);
    return panel;
  }

  function createDoctrineUpgradesPanel() {
    var panel = createElement('section', 'panel doctrine-upgrades-panel');
    var header = createElement('h3', 'panel-header', 'Doctrine Upgrades');
    panel.appendChild(header);

    var list = createElement('div', 'upgrade-list');
    list.id = 'doctrineUpgradesList';
    panel.appendChild(list);
    return panel;
  }

  function createPermanentUpgradesPanel() {
    var panel = createElement('section', 'panel permanent-upgrades-panel');
    var header = createElement('h3', 'panel-header', 'Permanent Upgrades');
    panel.appendChild(header);

    var list = createElement('div', 'upgrade-list');
    list.id = 'permanentUpgradesList';
    panel.appendChild(list);
    return panel;
  }

  function createRetunePanel() {
    var panel = createElement('section', 'panel retune-panel');
    var header = createElement('h3', 'panel-header', 'Retuning');
    panel.appendChild(header);

    var desc = createElement('p', 'panel-desc', 'Reset your progress for permanent bonuses.');
    panel.appendChild(desc);

    var infoRow = createElement('div', 'info-row');
    var countLabel = createElement('span', 'info-label', 'Retunings:');
    var countValue = createElement('span', 'info-value');
    countValue.id = 'retuneCount';
    infoRow.appendChild(countLabel);
    infoRow.appendChild(countValue);
    panel.appendChild(infoRow);

    var cooldownRow = createElement('div', 'info-row');
    var cooldownLabel = createElement('span', 'info-label', 'Cooldown:');
    var cooldownValue = createElement('span', 'info-value');
    cooldownValue.id = 'retuneCooldown';
    cooldownRow.appendChild(cooldownLabel);
    cooldownRow.appendChild(cooldownValue);
    panel.appendChild(cooldownRow);

    var iridescenceRow = createElement('div', 'info-row');
    var iridLabel = createElement('span', 'info-label', 'Next Iridescence:');
    var iridValue = createElement('span', 'info-value');
    iridValue.id = 'nextIridescence';
    iridescenceRow.appendChild(iridLabel);
    iridescenceRow.appendChild(iridValue);
    panel.appendChild(iridescenceRow);

    var retuneBtn = createButton('Retune', 'btn btn-retune btn-primary', function() {
      dispatchAction({ type: 'RETUNE' });
    });
    retuneBtn.id = 'retuneBtn';
    panel.appendChild(retuneBtn);

    return panel;
  }

  function createSettingsPanel() {
    var panel = createElement('section', 'panel settings-panel');
    var header = createElement('h3', 'panel-header', 'Settings');
    panel.appendChild(header);

    var speedRow = createElement('div', 'setting-row');
    var speedLabel = createElement('span', 'setting-label', 'Speed:');
    var speedValue = createElement('span', 'setting-value');
    speedValue.id = 'speedValue';
    speedRow.appendChild(speedLabel);
    speedRow.appendChild(speedValue);
    panel.appendChild(speedRow);

    var speedBtn = createButton('Cycle Speed', 'btn btn-small', function() {
      var currentSpeed = state.settings.speed;
      var currentIndex = speedKeys.indexOf(currentSpeed);
      var nextIndex = (currentIndex + 1) % speedKeys.length;
      dispatchAction({ type: 'SET_SPEED', speed: speedKeys[nextIndex] });
    });
    speedRow.appendChild(speedBtn);

    var pauseBtn = createButton('Pause', 'btn btn-small', function() {
      dispatchAction({ type: 'PAUSE' });
    });
    pauseBtn.id = 'pauseBtn';
    speedRow.appendChild(pauseBtn);

    var motionRow = createElement('div', 'setting-row');
    var motionLabel = createElement('span', 'setting-label', 'Reduced Motion:');
    var motionToggle = createButton('Toggle', 'btn btn-small', function() {
      dispatchAction({ type: 'SET_REDUCED_MOTION', enabled: !state.settings.reducedMotion });
    });
    motionRow.appendChild(motionLabel);
    motionRow.appendChild(motionToggle);
    panel.appendChild(motionRow);

    var colorblindRow = createElement('div', 'setting-row');
    var colorblindLabel = createElement('span', 'setting-label', 'Colorblind:');
    var colorblindValue = createElement('span', 'setting-value');
    colorblindValue.id = 'colorblindValue';
    var colorblindBtn = createButton('Cycle', 'btn btn-small', function() {
      var nextMode = getColorblindNext(state.settings.colorblindMode);
      dispatchAction({ type: 'SET_COLORBLIND_MODE', mode: nextMode });
    });
    colorblindRow.appendChild(colorblindLabel);
    colorblindRow.appendChild(colorblindValue);
    colorblindRow.appendChild(colorblindBtn);
    panel.appendChild(colorblindRow);

    var exportRow = createElement('div', 'setting-row');
    var exportBtn = createButton('Export Save', 'btn btn-small', function() {
      try {
        var saveStr = State.save(state);
        var blob = new Blob([saveStr], { type: 'application/json' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'glimweave-save.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        notify('Save exported successfully', 'success');
      } catch (e) {
        showModal('Export Error', e.message, [{ text: 'OK' }]);
      }
    });
    exportRow.appendChild(exportBtn);
    panel.appendChild(exportRow);

    var importFile = createElement('input', 'hidden');
    importFile.type = 'file';
    importFile.id = 'importFile';
    importFile.accept = '.json,application/json';
    importFile.addEventListener('change', function(e) {
      var file = e.target.files[0];
      if (file) {
        var reader = new FileReader();
        reader.onload = function(e) {
          try {
            var content = e.target.result;
            var importedState = State.load(content);
            if (importedState) {
              notify('Save imported successfully', 'success');
              location.reload();
            }
          } catch (err) {
            showModal('Import Error', err.message, [{ text: 'OK' }]);
          }
        };
        reader.readAsText(file);
      }
      importFile.value = '';
    });
    panel.appendChild(importFile);

    var importRow = createElement('div', 'setting-row');
    var importBtn = createButton('Import Save', 'btn btn-small', function() {
      importFile.click();
    });
    importRow.appendChild(importBtn);
    panel.appendChild(importRow);

    var resetRow = createElement('div', 'setting-row');
    var resetBtn = createButton('Reset Game', 'btn btn-small btn-danger', function() {
      showModal('Reset Game', 'Are you sure you want to reset all progress? This cannot be undone.', [
        { text: 'Cancel' },
        { text: 'Reset', callback: function() {
          localStorage.removeItem('glimweave_save_v1');
          location.reload();
        }}
      ]);
    });
    resetRow.appendChild(resetBtn);
    panel.appendChild(resetRow);

    return panel;
  }

  function createVictoryPanel() {
    var panel = createElement('section', 'panel victory-panel');
    panel.id = 'victoryPanel';
    panel.style.display = 'none';

    var header = createElement('h2', 'victory-header', 'Victory Achieved!');
    panel.appendChild(header);

    var message = createElement('p', 'victory-message', 'You have mastered the Sky Loom.');
    panel.appendChild(message);

    var statsHeader = createElement('h3', '', 'Final Statistics');
    panel.appendChild(statsHeader);

    var statsList = createElement('div', 'victory-stats');
    statsList.id = 'victoryStats';
    panel.appendChild(statsList);

    var scoreRow = createElement('div', 'victory-score');
    var scoreLabel = createElement('span', 'score-label', 'Score:');
    var scoreValue = createElement('span', 'score-value');
    scoreValue.id = 'victoryScore';
    scoreRow.appendChild(scoreLabel);
    scoreRow.appendChild(scoreValue);
    panel.appendChild(scoreRow);

    var newGameBtn = createButton('New Game', 'btn btn-primary btn-large', function() {
      localStorage.removeItem('glimweave_save_v1');
      location.reload();
    });
    panel.appendChild(newGameBtn);

    return panel;
  }

  function createOfflineReport() {
    var report = createElement('div', 'offline-report');
    report.id = 'offlineReport';
    report.style.display = 'none';

    var header = createElement('h3', '', 'You were offline');
    report.appendChild(header);

    var message = createElement('p', '', '');
    message.id = 'offlineMessage';
    report.appendChild(message);

    var closeBtn = createButton('Continue', 'btn btn-primary', function() {
      report.style.display = 'none';
      offlineReportShown = true;
    });
    report.appendChild(closeBtn);

    return report;
  }

  function buildUI() {
    rootElement.innerHTML = '';

    var container = createElement('div', 'ui-container');

    var topBar = createElement('div', 'top-bar');
    topBar.appendChild(createStatsPanel());
    container.appendChild(topBar);

    var mainPanels = createElement('div', 'main-panels');

    var leftColumn = createElement('div', 'panel-column left-column');
    leftColumn.appendChild(createPurchasePanel());
    leftColumn.appendChild(createRetunePanel());
    leftColumn.appendChild(createSettingsPanel());
    mainPanels.appendChild(leftColumn);

    var rightColumn = createElement('div', 'panel-column right-column');
    rightColumn.appendChild(createUpgradesPanel());
    rightColumn.appendChild(createDoctrinePanel());
    rightColumn.appendChild(createDoctrineUpgradesPanel());
    rightColumn.appendChild(createPermanentUpgradesPanel());
    mainPanels.appendChild(rightColumn);

    container.appendChild(mainPanels);
    container.appendChild(createVictoryPanel());
    container.appendChild(createOfflineReport());

    rootElement.appendChild(container);
    createTutorialOverlay();
  }

  function updatePurchaseButtons() {
    var list = document.getElementById('purchaseList');
    if (!list) return;

    list.innerHTML = '';
    var phase = state.phase;
    var reservoir = state.reservoir;
    var purchasedTypes = {};
    state.weftlings.forEach(function(w) { purchasedTypes[w.type] = true; });

    Object.keys(DATA.weftlings).forEach(function(typeId) {
      var weftling = DATA.weftlings[typeId];
      var unlock = weftling.unlock;
      var isUnlocked = true;

      if (unlock.phase && phase < unlock.phase) isUnlocked = false;
      if (unlock.totalGlimCaptured && state.totalGlimCaptured < unlock.totalGlimCaptured) isUnlocked = false;
      if (unlock.totalGlimSpentOnCapacity && state.baseCapacity < unlock.totalGlimSpentOnCapacity + 100) isUnlocked = false;

      if (!isUnlocked) return;

      var ownedCount = 0;
      state.weftlings.forEach(function(w) { if (w.type === typeId) ownedCount++; });
      var atMax = ownedCount >= weftling.maxOwned;

      var cost = Math.floor(weftling.baseCost * (atMax ? 1 : Math.pow(1.15, ownedCount)));

      var item = createElement('div', 'purchase-item' + (atMax ? ' disabled' : ''));
      var name = createElement('span', 'purchase-name', weftling.id + ': ');
      var desc = createElement('span', 'purchase-desc', weftling.description);
      var costSpan = createElement('span', 'purchase-cost', ' - ' + cost + ' Glim');
      var btn = createButton('Buy', 'btn btn-buy', function() {
        var canvas = document.getElementById('gameCanvas');
        var rect = canvas.getBoundingClientRect();
        var x = rect.width / 2 + Math.random() * 100 - 50;
        var y = rect.height / 2 + Math.random() * 100 - 50;
        dispatchAction({ type: 'BUY_WEFTLING', weftlingType: typeId, x: x, y: y });
      });
      btn.disabled = reservoir < cost || atMax;
      btn.setAttribute('aria-label', 'Buy ' + weftling.id + ' for ' + cost + ' Glim');

      if (atMax) {
        var maxSpan = createElement('span', 'max-label', ' (MAX)');
        btn = createElement('span', 'disabled-label', 'MAX');
        item.appendChild(name);
        item.appendChild(desc);
        item.appendChild(costSpan);
        item.appendChild(maxSpan);
      } else {
        item.appendChild(name);
        item.appendChild(desc);
        item.appendChild(costSpan);
        item.appendChild(btn);
      }

      list.appendChild(item);
    });
  }

  function updateUpgradeButtons() {
    var globalList = document.getElementById('globalUpgradesList');
    if (!globalList) return;

    globalList.innerHTML = '';
    Object.keys(DATA.globalUpgrades).forEach(function(upgradeId) {
      var upgrade = DATA.globalUpgrades[upgradeId];
      var owned = state.upgrades.global && state.upgrades.global.indexOf(upgradeId) >= 0;
      var purchaseCount = owned ? state.upgrades.global.filter(function(u) { return u === upgradeId; }).length : 0;
      var cost = Math.floor(upgrade.startCost * Math.pow(upgrade.scaling, purchaseCount));
      var atCap = purchaseCount >= upgrade.cap;

      var item = createElement('div', 'upgrade-item' + (owned && atCap ? ' disabled' : ''));
      var name = createElement('span', 'upgrade-name', upgrade.name + ': ');
      var desc = createElement('span', 'upgrade-desc', upgrade.effect);
      var costSpan = createElement('span', 'upgrade-cost', ' - ' + cost + ' Glim');
      var levelSpan = createElement('span', 'upgrade-level', owned ? ' (Level ' + purchaseCount + ')' : '');
      var btn = createButton('Buy', 'btn btn-buy', function() {
        dispatchAction({ type: 'BUY_UPGRADE', upgradeId: upgradeId });
      });
      btn.disabled = state.reservoir < cost || atCap;
      btn.setAttribute('aria-label', 'Buy ' + upgrade.name + ' for ' + cost + ' Glim');

      if (owned && atCap) {
        var maxSpan = createElement('span', 'max-label', ' (MAX)');
        item.appendChild(name);
        item.appendChild(desc);
        item.appendChild(levelSpan);
        item.appendChild(maxSpan);
      } else {
        item.appendChild(name);
        item.appendChild(desc);
        item.appendChild(levelSpan);
        item.appendChild(costSpan);
        item.appendChild(btn);
      }

      globalList.appendChild(item);
    });
  }

  function updateDoctrineSelection() {
    var list = document.getElementById('doctrineList');
    if (!list) return;

    list.innerHTML = '';
    var chosen = state.upgrades.doctrine;

    Object.keys(DATA.doctrines).forEach(function(doctrineId) {
      var doctrine = DATA.doctrines[doctrineId];
      var item = createElement('div', 'doctrine-item');

      var btn = createButton(doctrine, 'btn btn-doctrine', chosen ? null : function() {
        showModal('Choose Doctrine', 'Are you sure you want to choose ' + doctrine + '? This cannot be undone.', [
          { text: 'Cancel' },
          { text: 'Confirm', callback: function() {
            dispatchAction({ type: 'CHOOSE_DOCTRINE', doctrineId: doctrineId });
          }}
        ]);
      });
      btn.setAttribute('aria-label', 'Choose ' + doctrine + ' doctrine');

      if (chosen) {
        if (chosen === doctrineId) {
          btn.disabled = true;
          btn.className = 'btn btn-doctrine chosen';
          btn.textContent = doctrine + ' (Chosen)';
        } else {
          btn.disabled = true;
          btn.className = 'btn btn-doctrine disabled';
          btn.textContent = doctrine + ' (Locked)';
        }
      }

      var desc = createElement('p', 'doctrine-desc', doctrine);
      item.appendChild(btn);
      item.appendChild(desc);
      list.appendChild(item);
    });
  }

  function updateDoctrineUpgrades() {
    var list = document.getElementById('doctrineUpgradesList');
    if (!list) return;

    list.innerHTML = '';
    var doctrine = state.upgrades.doctrine;
    if (!doctrine) {
      var noDoctrine = createElement('p', 'no-doctrine', 'Choose a doctrine first');
      list.appendChild(noDoctrine);
      return;
    }

    var doctrineUpgrades = DATA.doctrineUpgrades[doctrine];
    if (!doctrineUpgrades) return;

    doctrineUpgrades.forEach(function(upgrade) {
      var owned = state.upgrades.doctrineUpgrades && state.upgrades.doctrineUpgrades.indexOf(upgrade.id) >= 0;
      var purchaseCount = owned ? state.upgrades.doctrineUpgrades.filter(function(u) { return u === upgrade.id; }).length : 0;
      var cost = Math.floor(upgrade.startCost * Math.pow(upgrade.scaling, purchaseCount));
      var atCap = upgrade.cap && purchaseCount >= upgrade.cap;
      var meetsRequirements = true;

      if (upgrade.requires) {
        meetsRequirements = state.upgrades.doctrineUpgrades && state.upgrades.doctrineUpgrades.indexOf(upgrade.requires) >= 0;
      }

      if (!meetsRequirements) {
        var item = createElement('div', 'upgrade-item disabled');
        var name = createElement('span', 'upgrade-name', upgrade.name);
        var reqSpan = createElement('span', 'requirement', ' (Requires: ' + upgrade.requires + ')');
        item.appendChild(name);
        item.appendChild(reqSpan);
        list.appendChild(item);
        return;
      }

      var item = createElement('div', 'upgrade-item' + (atCap ? ' disabled' : ''));
      var name = createElement('span', 'upgrade-name', upgrade.name + ': ');
      var desc = createElement('span', 'upgrade-desc', upgrade.effect);
      var costSpan = createElement('span', 'upgrade-cost', ' - ' + cost + ' Glim');
      var levelSpan = createElement('span', 'upgrade-level', owned ? ' (Level ' + purchaseCount + ')' : '');
      var btn = createButton('Buy', 'btn btn-buy', function() {
        dispatchAction({ type: 'BUY_UPGRADE', upgradeId: upgrade.id });
      });
      btn.disabled = state.reservoir < cost || atCap;
      btn.setAttribute('aria-label', 'Buy ' + upgrade.name + ' for ' + cost + ' Glim');

      if (atCap) {
        var maxSpan = createElement('span', 'max-label', ' (MAX)');
        item.appendChild(name);
        item.appendChild(desc);
        item.appendChild(levelSpan);
        item.appendChild(maxSpan);
      } else {
        item.appendChild(name);
        item.appendChild(desc);
        item.appendChild(levelSpan);
        item.appendChild(costSpan);
        item.appendChild(btn);
      }

      list.appendChild(item);
    });
  }

  function updatePermanentUpgrades() {
    var list = document.getElementById('permanentUpgradesList');
    if (!list) return;

    list.innerHTML = '';
    var iridescence = state.iridescence;

    Object.keys(DATA.permanentUpgrades).forEach(function(upgradeId) {
      var upgrade = DATA.permanentUpgrades[upgradeId];
      var owned = state.permanentUpgrades && state.permanentUpgrades.indexOf(upgradeId) >= 0;

      var item = createElement('div', 'upgrade-item' + (owned ? ' owned' : ''));
      var name = createElement('span', 'upgrade-name', upgrade.name + ': ');
      var desc = createElement('span', 'upgrade-desc', upgrade.effect);
      var costSpan = createElement('span', 'upgrade-cost', ' - ' + upgrade.cost + ' Iridescence');
      var btn = createButton(owned ? 'Owned' : 'Buy', 'btn btn-buy', owned ? null : function() {
        dispatchAction({ type: 'BUY_UPGRADE', upgradeId: upgradeId });
      });
      btn.disabled = owned || iridescence < upgrade.cost;
      btn.setAttribute('aria-label', (owned ? 'Already owned: ' : 'Buy ') + upgrade.name + ' for ' + upgrade.cost + ' Iridescence');

      item.appendChild(name);
      item.appendChild(desc);
      item.appendChild(costSpan);
      item.appendChild(btn);
      list.appendChild(item);
    });
  }

  function updateRetunePanel() {
    var countEl = document.getElementById('retuneCount');
    var cooldownEl = document.getElementById('retuneCooldown');
    var nextIridescenceEl = document.getElementById('nextIridescence');
    var btn = document.getElementById('retuneBtn');

    if (countEl) countEl.textContent = state.retuningCount;

    if (cooldownEl) {
      var now = Date.now();
      var lastRetune = state.lastRetuningTime || 0;
      var cooldown = Math.floor(DATA.constants.retuning.minimumIntervalBase * (1 + state.retuningCount / DATA.constants.retuning.diminishingReturnsThreshold) * 1000);
      var remaining = Math.max(0, lastRetune + cooldown - now);
      if (remaining > 0) {
        cooldownEl.textContent = formatTime(remaining / 1000) + ' remaining';
        if (btn) btn.disabled = true;
      } else {
        cooldownEl.textContent = 'Ready';
        if (btn) btn.disabled = false;
      }
    }

    if (nextIridescenceEl) {
      var formula = DATA.constants.retuning.iridescenceFormula;
      var nextIrid = '?';
      try {
        var thisRun = state.totalGlimCapturedThisRun;
        var calc = Math.floor(thisRun / 200) + 1;
        nextIrid = calc;
      } catch (e) {
        nextIrid = '?';
      }
      nextIridescenceEl.textContent = nextIrid + ' Iridescence';
    }
  }

  function updateStats() {
    var reservoirEl = document.getElementById('reservoirValue');
    var reservoirMaxEl = document.getElementById('reservoirMax');
    var reservoirBarFill = document.getElementById('reservoirBarFill');
    var iridescenceEl = document.getElementById('iridescenceValue');
    var productionEl = document.getElementById('productionValue');
    var captureEl = document.getElementById('captureValue');
    var fadeEl = document.getElementById('fadeValue');
    var phaseEl = document.getElementById('phaseValue');
    var pressureEl = document.getElementById('pressureValue');
    var speedEl = document.getElementById('speedValue');
    var pauseBtn = document.getElementById('pauseBtn');
    var colorblindEl = document.getElementById('colorblindValue');

    if (reservoirEl) reservoirEl.textContent = formatGlim(state.reservoir);
    if (reservoirMaxEl) reservoirMaxEl.textContent = formatGlim(state.maxCapacity);
    if (reservoirBarFill) {
      var pct = (state.reservoir / state.maxCapacity) * 100;
      reservoirBarFill.style.width = pct + '%';
      reservoirBarFill.setAttribute('aria-valuenow', pct);
      reservoirBarFill.setAttribute('aria-valuemin', '0');
      reservoirBarFill.setAttribute('aria-valuemax', '100');
    }
    if (iridescenceEl) iridescenceEl.textContent = formatGlim(state.iridescence);

    var prodRate = Simulation.getProductionRate(state);
    var captureRate = Simulation.getCaptureRate(state);
    var fadeRate = Simulation.getFadeRate(state);

    if (productionEl) productionEl.textContent = formatRate(prodRate) + '/s';
    if (captureEl) captureEl.textContent = formatRate(captureRate) + '/s';
    if (fadeEl) fadeEl.textContent = formatRate(fadeRate) + '/s';
    if (phaseEl) phaseEl.textContent = phaseNames[Object.keys(phaseNames)[state.phase - 1]] + ' (' + state.phase + ')';
    if (pressureEl) pressureEl.textContent = (state.pressure * 100).toFixed(0) + '%';

    if (speedEl) speedEl.textContent = state.settings.speed + 'x';
    if (pauseBtn) {
      pauseBtn.textContent = state.settings.paused ? 'Resume' : 'Pause';
      pauseBtn.setAttribute('aria-label', state.settings.paused ? 'Resume game' : 'Pause game');
    }
    if (colorblindEl) colorblindEl.textContent = state.settings.colorblindMode;

    var victoryPanel = document.getElementById('victoryPanel');
    if (victoryPanel) {
      if (state.victory) {
        victoryPanel.style.display = 'block';
        updateVictoryStats();
      } else {
        victoryPanel.style.display = 'none';
      }
    }
  }

  function updateVictoryStats() {
    var statsList = document.getElementById('victoryStats');
    if (!statsList) return;

    statsList.innerHTML = '';

    var addStat = function(label, value) {
      var row = createElement('div', 'victory-stat');
      var labelEl = createElement('span', 'stat-label', label + ': ');
      var valueEl = createElement('span', 'stat-value', value);
      row.appendChild(labelEl);
      row.appendChild(valueEl);
      statsList.appendChild(row);
    };

    addStat('Total Glim Captured', formatGlim(state.totalGlimCaptured));
    addStat('Iridescence', formatGlim(state.iridescence));
    addStat('Retunings', state.retuningCount);
    addStat('Highest Phase', state.highestPhaseUnlocked);
    addStat('Weftlings Owned', state.weftlings.length);
    addStat('Global Upgrades', state.upgrades.global ? state.upgrades.global.length : 0);
    addStat('Doctrine Upgrades', state.upgrades.doctrineUpgrades ? state.upgrades.doctrineUpgrades.length : 0);
    addStat('Permanent Upgrades', state.permanentUpgrades ? state.permanentUpgrades.length : 0);

    var doctrineBonus = DATA.constants.victory.doctrineBonus[state.upgrades.doctrine || 'Luminance'] || 0;
    var score = Math.floor(state.totalGlimCaptured * (1 + state.iridescence / 100) * (1 + doctrineBonus));
    var scoreEl = document.getElementById('victoryScore');
    if (scoreEl) scoreEl.textContent = formatGlim(score);
  }

  function updateOfflineReport() {
    if (offlineReportShown) return;
    if (!state || !state._offlineGlim) return;

    var report = document.getElementById('offlineReport');
    var message = document.getElementById('offlineMessage');
    if (report && message) {
      message.textContent = 'You gained ' + formatGlim(state._offlineGlim) + ' Glim while offline.';
      report.style.display = 'block';
    }
    state._offlineGlim = 0;
  }

  function updateTutorial() {
    if (!state || state.settings.tutorialComplete || state.tutorialStep >= DATA.constants.tutorial.steps) {
      hideTutorial();
      return;
    }

    if (state.tutorialStep >= 0 && tutorialElement && tutorialElement.style.display !== 'flex') {
      showTutorialStep(state.tutorialStep);
    }
  }

  function updateUI() {
    if (!state) return;

    updateStats();
    updatePurchaseButtons();
    updateUpgradeButtons();
    updateDoctrineSelection();
    updateDoctrineUpgrades();
    updatePermanentUpgrades();
    updateRetunePanel();
    updateOfflineReport();
    updateTutorial();

    var phase = state.phase;
    var leftColumn = rootElement.querySelector('.left-column');
    var rightColumn = rootElement.querySelector('.right-column');

    if (leftColumn && rightColumn) {
      leftColumn.style.display = '';
      rightColumn.style.display = '';

      if (phase < 2) {
        var doctrinePanel = rootElement.querySelector('.doctrine-panel');
        var doctrineUpgradesPanel = rootElement.querySelector('.doctrine-upgrades-panel');
        if (doctrinePanel) doctrinePanel.style.display = 'none';
        if (doctrineUpgradesPanel) doctrineUpgradesPanel.style.display = 'none';
      }
    }
  }

  function checkOfflineProgress() {
    if (!state || !state.lastUpdate) return;
    var now = Date.now();
    var elapsed = now - state.lastUpdate;
    var maxOffline = DATA.constants.offline.maxSeconds * 1000;
    var cappedElapsed = Math.min(elapsed, maxOffline);

    if (cappedElapsed >= 1000) {
      var offlineGlim = State.applyOfflineProgress(state, cappedElapsed / 1000);
      state.lastUpdate = now;
      if (offlineGlim > 0) {
        state._offlineGlim = offlineGlim;
      }
    } else {
      state.lastUpdate = now;
    }
  }

  function saveState() {
    try {
      State.save(state);
    } catch (e) {
      console.error('Failed to save state:', e);
    }
  }

  function loadState() {
    try {
      var saved = State.load();
      if (saved) {
        state = saved;
        state.lastUpdate = Date.now();
        checkOfflineProgress();
        return true;
      }
    } catch (e) {
      console.error('Failed to load state:', e);
    }
    return false;
  }

  function startSimLoop() {
    if (simInterval) clearInterval(simInterval);
    simInterval = setInterval(function() {
      if (!visibilityState || state.settings.paused) return;
      var now = Date.now();
      var elapsed = now - lastAutoSave;
      if (elapsed >= 30000) {
        saveState();
        lastAutoSave = now;
      }
      Simulation.step(state, GW.TICK_MS);
      updateUI();
    }, GW.TICK_MS);
  }

  function startRenderLoop() {
    if (renderId) cancelAnimationFrame(renderId);
    function renderLoop(timestamp) {
      if (!lastRenderTime) lastRenderTime = timestamp;
      var delta = timestamp - lastRenderTime;
      if (delta >= 1000 / GW.FPS) {
        lastRenderTime = timestamp;
        Renderer.render(state, delta);
      }
      renderId = requestAnimationFrame(renderLoop);
    }
    renderId = requestAnimationFrame(renderLoop);
  }

  function setupKeyboard() {
    document.addEventListener('keydown', function(e) {
      if (modalStack.length > 0) return;
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

      switch(e.key) {
        case ' ':
          if (e.target.tagName !== 'BUTTON') {
            e.preventDefault();
            dispatchAction({ type: 'PAUSE' });
          }
          break;
        case '1':
          dispatchAction({ type: 'SET_SPEED', speed: 1 });
          break;
        case '2':
          dispatchAction({ type: 'SET_SPEED', speed: 2 });
          break;
        case '3':
          dispatchAction({ type: 'SET_SPEED', speed: 4 });
          break;
        case '4':
          dispatchAction({ type: 'SET_SPEED', speed: 0.5 });
          break;
        case 't':
        case 'T':
          if (!state.settings.tutorialComplete && state.tutorialStep < DATA.constants.tutorial.steps) {
            showTutorialStep(state.tutorialStep);
          }
          break;
        case 'm':
        case 'M':
          dispatchAction({ type: 'SET_REDUCED_MOTION', enabled: !state.settings.reducedMotion });
          break;
        case 'c':
        case 'C':
          var nextMode = getColorblindNext(state.settings.colorblindMode);
          dispatchAction({ type: 'SET_COLORBLIND_MODE', mode: nextMode });
          break;
        case 'Escape':
          hideModal();
          hideTutorial();
          break;
      }
    });
  }

  function setupVisibility() {
    document.addEventListener('visibilitychange', function() {
      visibilityState = !document.hidden;
      if (visibilityState) {
        checkOfflineProgress();
        updateUI();
        state.lastUpdate = Date.now();
        saveState();
      }
    });
  }

  function setupBeforeUnload() {
    window.addEventListener('beforeunload', function() {
      if (state && !state.victory) {
        saveState();
      }
    });
  }

  UI.init = function(root) {
    if (isInitialized) return;
    rootElement = root;
    isInitialized = true;

    buildUI();
    setupKeyboard();
    setupVisibility();
    setupBeforeUnload();

    var loaded = loadState();
    if (!loaded) {
      Utils.RNG.seed((navigator.userAgent || '').split('').reduce(function(a, b) { return a + b.charCodeAt(0); }, 0) || Date.now());
      state = State.create();
    }

    if (!actionHandler) {
      actionHandler = function(action) {
        try {
          Simulation.handleAction(state, action);
          saveState();
          updateUI();
          // Paint state-changing actions synchronously so the playfield never
          // depends on the next animation-frame callback becoming available.
          Renderer.render(state, 0);
        } catch (e) {
          var reason = e.message || String(e);
          announce('Action rejected: ' + reason);
          UI.showNotification('Cannot perform action: ' + reason, 'error');
        }
      };
      UI.onAction(actionHandler);
    }

    GW.Renderer.init(document.getElementById('gameCanvas'), state);
    startSimLoop();
    startRenderLoop();

    updateUI();
    // Establish a real first frame immediately. Browsers may defer animation
    // frames for background tabs and automation, which previously left the
    // central playfield transparent until an rAF happened to run.
    Renderer.render(state, 0);

    if (!loaded) {
      setTimeout(function() {
        if (state && state.tutorialStep === 0 && !state.settings.tutorialComplete) {
          showTutorialStep(0);
        }
      }, 1000);
    }

    checkOfflineProgress();
    updateOfflineReport();
  };

  UI.update = function(newState) {
    state = newState;
    updateUI();
    Renderer.render(state, 0);
  };

  UI.onAction = function(handler) {
    actionHandler = handler;
  };

  UI.showTutorialStep = showTutorialStep;
  UI.hideTutorial = hideTutorial;
  UI.showModal = showModal;
  UI.hideModal = hideModal;
  UI.showNotification = notify;

  GW.init = function() {
    var root = document.getElementById('uiRoot');
    if (root) {
      UI.init(root);
    }
  };

  window.__glimweaveTest = (function() {
    var TEST = {};

    TEST.createState = function(seed) {
      if (seed !== undefined) {
        Utils.RNG.seed(seed);
      } else {
        Utils.RNG.seed(42);
      }
      return State.create();
    };

    TEST.cloneState = function(s) {
      return JSON.parse(JSON.stringify(s));
    };

    TEST.step = function(s, steps) {
      for (var i = 0; i < steps; i++) {
        Simulation.step(s, GW.TICK_MS);
      }
    };

    TEST.stepUntil = function(s, condition, maxSteps) {
      var steps = 0;
      while (steps < maxSteps) {
        Simulation.step(s, GW.TICK_MS);
        steps++;
        if (condition(s)) return steps;
      }
      return steps;
    };

    TEST.buyWeftling = function(s, type, x, y) {
      Simulation.handleAction(s, { type: 'BUY_WEFTLING', weftlingType: type, x: x || 100, y: y || 100 });
    };

    TEST.buyUpgrade = function(s, upgradeId) {
      Simulation.handleAction(s, { type: 'BUY_UPGRADE', upgradeId: upgradeId });
    };

    TEST.chooseDoctrine = function(s, doctrineId) {
      Simulation.handleAction(s, { type: 'CHOOSE_DOCTRINE', doctrineId: doctrineId });
    };

    TEST.retune = function(s) {
      var before = s.iridescence;
      Simulation.handleAction(s, { type: 'RETUNE' });
      return s.iridescence - before;
    };

    TEST.activateAbility = function(s, abilityId) {
      Simulation.handleAction(s, { type: 'ACTIVATE_ABILITY', abilityId: abilityId });
    };

    TEST.getProductionRate = function(s) {
      return Simulation.getProductionRate(s);
    };

    TEST.getCaptureRate = function(s) {
      return Simulation.getCaptureRate(s);
    };

    TEST.getPressure = function(s) {
      return s.pressure;
    };

    TEST.getMoteCount = function(s) {
      return s.motes ? s.motes.length : 0;
    };

    TEST.getReservoir = function(s) {
      return s.reservoir;
    };

    TEST.getPhase = function(s) {
      return s.phase;
    };

    TEST.isVictory = function(s) {
      return s.victory;
    };

    TEST.applyOfflineProgress = function(s, seconds) {
      return State.applyOfflineProgress(s, seconds);
    };

    TEST.saveState = function(s) {
      return State.save(s);
    };

    TEST.loadState = function(json) {
      return State.load(json);
    };

    TEST.validateState = function(s) {
      try {
        State.validate(s);
        return true;
      } catch (e) {
        return false;
      }
    };

    TEST.assertStateInvariants = function(s) {
      State.validate(s);
    };

    TEST.testProductionCaptureIndependence = function() {
      var s = TEST.createState(1);
      s.weftlings = [{ id: 'w1', type: 'Glimspinner', x: 100, y: 100 }];
      var prod1 = TEST.getProductionRate(s);
      TEST.step(s, 10);
      var prod2 = TEST.getProductionRate(s);
      return prod1 === prod2;
    };

    TEST.testFadeImpact = function() {
      var s = TEST.createState(1);
      s.weftlings = [];
      s.reservoir = 100;
      TEST.step(s, 100);
      var count1 = TEST.getMoteCount(s);
      TEST.step(s, 1000);
      var count2 = TEST.getMoteCount(s);
      return count2 < count1;
    };

    TEST.testOverflow = function() {
      var s = TEST.createState(1);
      s.reservoir = s.maxCapacity;
      s.weftlings = [{ id: 'w1', type: 'Glimspinner', x: 100, y: 100 }];
      var before = s.reservoir;
      TEST.step(s, 10);
      return s.reservoir <= s.maxCapacity;
    };

    TEST.testUnitPurchase = function() {
      var s = TEST.createState(1);
      s.reservoir = 100;
      var countBefore = s.weftlings.length;
      var reservoirBefore = s.reservoir;
      TEST.buyWeftling(s, 'Glimspinner', 100, 100);
      return s.weftlings.length === countBefore + 1 && s.reservoir < reservoirBefore;
    };

    TEST.testUpgradePurchase = function() {
      var s = TEST.createState(1);
      s.reservoir = 200;
      var countBefore = s.upgrades.global ? s.upgrades.global.length : 0;
      TEST.buyUpgrade(s, 'WeftlingEfficiency');
      return (s.upgrades.global ? s.upgrades.global.length : 0) === countBefore + 1;
    };

    TEST.testDoctrineLock = function() {
      var s = TEST.createState(1);
      s.reservoir = 1000;
      TEST.chooseDoctrine(s, 'Luminance');
      try {
        TEST.chooseDoctrine(s, 'Captivation');
        return false;
      } catch (e) {
        return true;
      }
    };

    TEST.testPhaseProgression = function() {
      var s = TEST.createState(1);
      s.reservoir = 1000;
      s.weftlings = [];
      for (var i = 0; i < 10; i++) {
        TEST.buyWeftling(s, 'Glimspinner', i * 20, i * 20);
      }
      TEST.stepUntil(s, function(st) { return st.totalGlimCaptured >= 500; }, 5000);
      return s.phase >= 2;
    };

    TEST.testRetuning = function() {
      var s = TEST.createState(1);
      s.weftlings = [{ id: 'w1', type: 'Glimspinner', x: 100, y: 100 }];
      s.reservoir = 100;
      s.totalGlimCaptured = 2000;
      s.totalGlimCapturedThisRun = 2000;
      s.retuningCount = 0;
      s.iridescence = 0;
      s.phase = 2;
      s.highestPhaseUnlocked = 2;
      TEST.retune(s);
      return s.weftlings.length === 0 && s.reservoir === 100 && s.totalGlimCapturedThisRun === 0 && s.iridescence > 0;
    };

    TEST.testOfflineProgress = function() {
      var s = TEST.createState(1);
      s.reservoir = 50;
      s.maxCapacity = 100;
      s.lastUpdate = Date.now() - 4000;
      s.weftlings = [{ id: 'w1', type: 'Glimspinner', x: 100, y: 100 }];
      var offlineSec = 3600;
      var gained = TEST.applyOfflineProgress(s, offlineSec);
      return gained.glimGained > 0;
    };

    TEST.testSaveLoad = function() {
      var s = TEST.createState(1);
      s.reservoir = 500;
      s.weftlings = [{ id: 'w1', type: 'Glimspinner', x: 100, y: 100 }];
      var saved = TEST.saveState(s);
      var loaded = TEST.loadState(saved);
      return loaded.reservoir === 500 && loaded.weftlings.length === 1;
    };

    TEST.testVictory = function() {
      var s = TEST.createState(1);
      s.phase = 4;
      s.highestPhaseUnlocked = 4;
      s.reservoir = s.maxCapacity;
      s.totalGlimCaptured = 10000;
      s.ownedClassCount = 5;
      s.upgrades.global = ['u1', 'u2', 'u3', 'u4', 'u5', 'u6', 'u7', 'u8', 'u9', 'u10', 'u11', 'u12'];
      TEST.step(s, 60);
      return s.victory;
    };

    return TEST;
  })();

})();

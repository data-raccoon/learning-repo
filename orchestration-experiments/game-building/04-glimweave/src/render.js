(function() {
  'use strict';

  if (typeof window.GW === 'undefined') {
    window.GW = {};
  }
  if (typeof window.GW.Renderer !== 'undefined') {
    return;
  }

  var DATA = window.GW.DATA;
  var CANVAS_WIDTH = 800;
  var CANVAS_HEIGHT = 600;
  var MOTE_RADIUS = 8;
  var AURORA_OPACITY = 0.3;

  var canvas = null;
  var ctx = null;
  var dpr = 1;
  var width = 0;
  var height = 0;
  var reducedMotion = false;
  var colorblindMode = 'DEFAULT';
  var resizeObserver = null;

  var motePool = [];
  var weftlingPool = [];
  var lastState = null;
  var lastRenderTime = 0;

  function init(canvasElement) {
    canvas = canvasElement;
    ctx = canvas.getContext('2d');
    dpr = window.devicePixelRatio || 1;

    var rect = canvas.getBoundingClientRect();
    resize(Math.floor(rect.width), Math.floor(rect.height));

    resizeObserver = new ResizeObserver(function(entries) {
      var entry = entries[0];
      if (entry && entry.contentRect) {
        var newWidth = Math.floor(entry.contentRect.width);
        var newHeight = Math.floor(entry.contentRect.height);
        if (newWidth !== width || newHeight !== height) {
          resize(newWidth, newHeight);
        }
      }
    });
    resizeObserver.observe(canvas);

    window.addEventListener('resize', function() {
      var rect = canvas.getBoundingClientRect();
      var newWidth = Math.floor(rect.width);
      var newHeight = Math.floor(rect.height);
      if (newWidth !== width || newHeight !== height) {
        resize(newWidth, newHeight);
      }
    });

    reducedMotion = false;
    colorblindMode = 'DEFAULT';
    lastState = null;
    lastRenderTime = 0;
    motePool = [];
    weftlingPool = [];
    for (var i = 0; i < 500; i++) {
      motePool.push({ x: 0, y: 0, radius: 0, color: '', shape: '' });
      weftlingPool.push({ x: 0, y: 0, type: '', size: 0, color: '' });
    }
  }

  function resize(w, h) {
    if (!canvas) return;
    var newWidth = w;
    var newHeight = h;
    if (newWidth === width && newHeight === height) return;

    width = newWidth;
    height = newHeight;

    dpr = window.devicePixelRatio || 1;

    var displayWidth = Math.max(1, Math.floor(width * dpr));
    var displayHeight = Math.max(1, Math.floor(height * dpr));
    if (displayWidth > 2000) displayWidth = 2000;
    if (displayHeight > 1500) displayHeight = 1500;

    canvas.width = displayWidth;
    canvas.height = displayHeight;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';

    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
  }

  function setReducedMotion(enabled) {
    reducedMotion = enabled;
  }

  function setColorblindMode(mode) {
    if (DATA.colorblindModes[mode]) {
      colorblindMode = mode;
    }
  }

  function getMoteColor(value) {
    if (colorblindMode === 'HIGH_CONTRAST') {
      return value === 1 ? '#00FF00' : '#FFFF00';
    } else if (colorblindMode === 'DEUTERANOPIA') {
      return '#FFFFFF';
    }
    return value === 1 ? '#7FFFD4' : '#00FFFF';
  }

  function getAuroraGradient(pressure) {
    if (colorblindMode === 'HIGH_CONTRAST') {
      return 'black';
    }
    if (colorblindMode === 'DEUTERANOPIA') {
      return '#404040';
    }
    var p = Math.min(1, Math.max(0, pressure));
    var r1 = Math.floor(30 + p * 80);
    var g1 = Math.floor(50 + p * 100);
    var b1 = Math.floor(100 + p * 155);
    var r2 = Math.floor(100 + p * 55);
    var g2 = Math.floor(150 + p * 55);
    var b2 = Math.floor(50 + p * 100);
    return 'linear-gradient(to bottom, rgb(' + r1 + ',' + g1 + ',' + b1 + '), rgb(' + r2 + ',' + g2 + ',' + b2 + '))';
  }

  function render(state, deltaMs) {
    if (!canvas || !ctx) return;
    if (canvas.width === 0 || canvas.height === 0) return;
    if (state === null || typeof state !== 'object') return;

    lastState = state;
    lastRenderTime = deltaMs;

    ctx.clearRect(0, 0, width, height);

    drawSkyLoom(state);
    drawReservoir(state);
    drawPhaseIndicator(state);
    drawPressure(state);
    drawWeftlings(state);
    drawMotes(state, deltaMs);
    if (state.victory) drawVictoryOverlay(state);
    if (state.settings.paused) drawPauseOverlay(state);
  }

  function drawSkyLoom(state) {
    ctx.save();
    if (colorblindMode === 'HIGH_CONTRAST') {
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, width, height);
      ctx.restore();
      return;
    }
    if (colorblindMode === 'DEUTERANOPIA') {
      ctx.fillStyle = '#404040';
      ctx.fillRect(0, 0, width, height);
      ctx.restore();
      return;
    }
    var gradient = ctx.createLinearGradient(0, 0, 0, height);
    var phase = state.phase || 1;
    var p = Math.min(1, Math.max(0, state.pressure || 0));
    var hue1, hue2;
    if (phase === 1) {
      hue1 = 200; hue2 = 240;
    } else if (phase === 2) {
      hue1 = 220; hue2 = 260;
    } else if (phase === 3) {
      hue1 = 240; hue2 = 280;
    } else {
      hue1 = 260; hue2 = 300;
    }
    hue1 = hue1 + p * 20;
    hue2 = hue2 + p * 20;
    gradient.addColorStop(0, 'hsl(' + hue1 + ', 70%, 20%)');
    gradient.addColorStop(0.5, 'hsl(' + ((hue1 + hue2) / 2) + ', 80%, 30%)');
    gradient.addColorStop(1, 'hsl(' + hue2 + ', 70%, 20%)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    ctx.globalAlpha = AURORA_OPACITY;
    var patternSize = Math.max(100, width / 8, height / 6);
    var offsetX = (state.totalGlimCaptured || 0) * 0.01 % patternSize;
    var offsetY = (state.totalGlimCaptured || 0) * 0.015 % patternSize;
    if (!reducedMotion) {
      ctx.save();
      ctx.globalCompositeOperation = 'lighter';
      for (var y = -patternSize; y < height + patternSize; y += patternSize) {
        for (var x = -patternSize; x < width + patternSize; x += patternSize) {
          var sx = x + offsetX;
          var sy = y + offsetY;
          var angle = (sx * 0.01 + sy * 0.015 + (state.lastUpdate || 0) * 0.001) % (Math.PI * 2);
          var sx2 = sx + Math.cos(angle) * patternSize * 0.3;
          var sy2 = sy + Math.sin(angle) * patternSize * 0.3;
          var sx3 = sx + Math.cos(angle + Math.PI * 2 / 3) * patternSize * 0.3;
          var sy3 = sy + Math.sin(angle + Math.PI * 2 / 3) * patternSize * 0.3;
          var sx4 = sx + Math.cos(angle + Math.PI * 4 / 3) * patternSize * 0.3;
          var sy4 = sy + Math.sin(angle + Math.PI * 4 / 3) * patternSize * 0.3;
          ctx.beginPath();
          ctx.moveTo(sx, sy);
          ctx.lineTo(sx2, sy2);
          ctx.lineTo(sx3, sy3);
          ctx.lineTo(sx4, sy4);
          ctx.closePath();
          ctx.fillStyle = 'hsl(' + ((hue1 + hue2) / 2) + ', 90%, ' + (50 + p * 20) + '%)';
          ctx.globalAlpha = 0.05 + p * 0.15;
          ctx.fill();
        }
      }
      ctx.restore();
    }
    ctx.globalAlpha = 1;
    ctx.restore();
  }

  function drawReservoir(state) {
    if (typeof state.reservoir !== 'number' || typeof state.maxCapacity !== 'number') return;
    var fillRatio = state.reservoir / state.maxCapacity;
    var phase = state.phase || 1;
    var centerX = width * 0.5;
    var centerY = height * 0.9;
    var radius = Math.min(width * 0.35, height * 0.25);
    var innerRadius = radius * 0.7;
    ctx.save();
    ctx.translate(centerX, centerY);
    if (colorblindMode === 'HIGH_CONTRAST') {
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.arc(0, 0, radius, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(0, 0, innerRadius, 0, Math.PI * 2);
      ctx.stroke();
      var segments = 30;
      for (var i = 0; i < segments; i++) {
        var angle1 = (i / segments) * Math.PI * 2 - Math.PI / 2;
        var angle2 = ((i + 1) / segments) * Math.PI * 2 - Math.PI / 2;
        var fillSegment = false;
        if (fillRatio > i / segments) {
          fillSegment = true;
        }
        ctx.beginPath();
        ctx.moveTo(Math.cos(angle1) * innerRadius, Math.sin(angle1) * innerRadius);
        ctx.arc(0, 0, innerRadius, angle1, angle2);
        ctx.lineTo(Math.cos(angle2) * radius, Math.sin(angle2) * radius);
        ctx.arc(0, 0, radius, angle2, angle1, true);
        ctx.closePath();
        if (fillSegment) {
          ctx.fillStyle = i % 2 === 0 ? '#00FF00' : '#00CC00';
          ctx.fill();
        }
        ctx.strokeStyle = '#888888';
        ctx.stroke();
      }
    } else if (colorblindMode === 'DEUTERANOPIA') {
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.arc(0, 0, radius, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(0, 0, innerRadius, 0, Math.PI * 2);
      ctx.stroke();
      ctx.fillStyle = '#000000';
      ctx.beginPath();
      ctx.moveTo(0, -innerRadius);
      for (var j = 0; j <= 30; j++) {
        var angle = (j / 30) * Math.PI * 2 - Math.PI / 2;
        var r = innerRadius + (radius - innerRadius) * (j / 30);
        if (j / 30 > fillRatio) r = innerRadius;
        ctx.lineTo(Math.cos(angle) * r, Math.sin(angle) * r);
      }
      ctx.closePath();
      ctx.fill();
      var textRatio = Math.floor(fillRatio * 100) + '%';
      ctx.fillStyle = '#FFFFFF';
      ctx.font = (radius * 0.4) + 'px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(textRatio, 0, 0);
    } else {
      var hueBase = phase === 1 ? 200 : phase === 2 ? 220 : phase === 3 ? 240 : 260;
      var bgColor = 'hsl(' + (hueBase - 30) + ', 40%, 15%)';
      var fgColor = 'hsl(' + hueBase + ', 80%, 50%)';
      var fgColorDark = 'hsl(' + hueBase + ', 80%, 30%)';
      ctx.fillStyle = bgColor;
      ctx.beginPath();
      ctx.arc(0, 0, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = 'rgba(255,255,255,0.2)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(0, 0, radius, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(0, 0, innerRadius, 0, Math.PI * 2);
      ctx.stroke();
      if (fillRatio > 0) {
        ctx.beginPath();
        ctx.moveTo(Math.cos(-Math.PI / 2) * innerRadius, Math.sin(-Math.PI / 2) * innerRadius);
        var endAngle = -Math.PI / 2 + fillRatio * Math.PI * 2;
        ctx.arc(0, 0, innerRadius, -Math.PI / 2, endAngle);
        ctx.lineTo(Math.cos(endAngle) * radius, Math.sin(endAngle) * radius);
        ctx.arc(0, 0, radius, endAngle, -Math.PI / 2, true);
        ctx.closePath();
        ctx.fillStyle = fgColor;
        ctx.fill();
        ctx.strokeStyle = fgColorDark;
        ctx.lineWidth = 1;
        ctx.stroke();
      }
      var pressure = state.pressure || 0;
      if (pressure > 0.5) {
        ctx.globalAlpha = 0.3 + (pressure - 0.5) * 1.4;
        ctx.fillStyle = 'rgba(255, 100, 100, 0.5)';
        ctx.beginPath();
        ctx.arc(0, 0, radius + 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
      }
      var text = Math.floor(fillRatio * 100) + '%';
      ctx.fillStyle = '#FFFFFF';
      ctx.font = (radius * 0.3) + 'px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, 0, 0);
    }
    ctx.restore();
  }

  function drawPhaseIndicator(state) {
    var phase = state.phase || 1;
    var phaseNames = ['Awakening', 'Resonance', 'Convergence', 'Radiance'];
    var name = phaseNames[phase - 1] || 'Unknown';
    var x = width * 0.05;
    var y = height * 0.05;
    ctx.save();
    ctx.font = (width * 0.04) + 'px sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    if (colorblindMode === 'HIGH_CONTRAST') {
      ctx.fillStyle = '#FFFFFF';
    } else if (colorblindMode === 'DEUTERANOPIA') {
      ctx.fillStyle = '#FFFFFF';
      ctx.fillStyle = phase === 1 ? '#00FFFF' : phase === 2 ? '#FF00FF' : phase === 3 ? '#FFFF00' : '#FF0000';
      ctx.font = (width * 0.045) + 'px sans-serif';
      ctx.fillText(name, x, y);
      ctx.fillStyle = '#FFFFFF';
      ctx.font = (width * 0.035) + 'px sans-serif';
      ctx.fillText('Phase ' + phase, x, y + width * 0.05);
    } else {
      var hue = phase === 1 ? 200 : phase === 2 ? 280 : phase === 3 ? 320 : 360;
      ctx.fillStyle = 'hsl(' + hue + ', 100%, 60%)';
      ctx.fillText(name, x, y);
      ctx.fillStyle = 'rgba(255,255,255,0.7)';
      ctx.font = (width * 0.03) + 'px sans-serif';
      ctx.fillText('Phase ' + phase, x, y + width * 0.04);
    }
    ctx.restore();
  }

  function drawPressure(state) {
    var pressure = state.pressure || 0;
    if (pressure <= 0) return;
    var barWidth = width * 0.4;
    var barHeight = height * 0.03;
    var x = width * 0.5 - barWidth * 0.5;
    var y = height * 0.05;
    ctx.save();
    ctx.globalAlpha = 0.6;
    ctx.fillStyle = colorblindMode === 'HIGH_CONTRAST' ? '#FF0000' : colorblindMode === 'DEUTERANOPIA' ? '#FF0000' : 'rgba(255, ' + Math.floor(100 + pressure * 155) + ', 100, 0.8)';
    ctx.fillRect(x, y, barWidth * pressure, barHeight);
    ctx.globalAlpha = 1;
    ctx.strokeStyle = colorblindMode === 'HIGH_CONTRAST' ? '#FFFFFF' : 'rgba(255,255,255,0.5)';
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, barWidth, barHeight);
    ctx.restore();
  }

  function drawWeftlings(state) {
    if (!state.weftlings || !Array.isArray(state.weftlings)) return;
    var now = Date.now();
    var scale = Math.min(width / CANVAS_WIDTH, height / CANVAS_HEIGHT);
    for (var i = 0; i < state.weftlings.length; i++) {
      var w = state.weftlings[i];
      if (typeof w.x !== 'number' || typeof w.y !== 'number') continue;
      var wx = w.x * scale;
      var wy = w.y * scale;
      var size = 24 * scale;
      var type = w.type || '';
      var hue = 0;
      if (colorblindMode === 'DEUTERANOPIA') {
        drawWeftlingShape(ctx, wx, wy, size, type, now);
        continue;
      }
      if (type === DATA.weftlingTypes.GLIMSPINNER) {
        hue = 200;
      } else if (type === DATA.weftlingTypes.DRIFTCATCHER) {
        hue = 120;
      } else if (type === DATA.weftlingTypes.THREADWEAVER) {
        hue = 300;
      } else if (type === DATA.weftlingTypes.HARMONIZER) {
        hue = 60;
      } else if (type === DATA.weftlingTypes.LOOMGUARD) {
        hue = 0;
      }
      var saturation = 80;
      var lightness = 45;
      if (colorblindMode === 'HIGH_CONTRAST') {
        saturation = 100;
        lightness = 50;
      }
      var color = 'hsl(' + hue + ',' + saturation + '%,' + lightness + '%)';
      ctx.fillStyle = color;
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 2 * scale;
      if (type === DATA.weftlingTypes.GLIMSPINNER) {
        ctx.beginPath();
        ctx.arc(wx, wy, size * 0.4, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        for (var j = 0; j < 8; j++) {
          var angle = (j / 8) * Math.PI * 2;
          var r1 = size * 0.5;
          var r2 = size * 0.7;
          if (!reducedMotion) {
            angle += (now * 0.002 + i) % (Math.PI * 2);
          }
          ctx.beginPath();
          ctx.moveTo(wx + Math.cos(angle) * r1, wy + Math.sin(angle) * r1);
          ctx.lineTo(wx + Math.cos(angle) * r2, wy + Math.sin(angle) * r2);
          ctx.stroke();
        }
      } else if (type === DATA.weftlingTypes.DRIFTCATCHER) {
        ctx.beginPath();
        ctx.arc(wx, wy, size * 0.4, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(wx, wy, size * 0.65, 0, Math.PI * 2);
        ctx.stroke();
        var angles = [0, Math.PI / 2, Math.PI, Math.PI * 1.5];
        for (var k = 0; k < angles.length; k++) {
          var ra = size * 0.75;
          ctx.beginPath();
          ctx.moveTo(wx + Math.cos(angles[k]) * ra, wy + Math.sin(angles[k]) * ra);
          ctx.lineTo(wx + Math.cos(angles[k]) * (ra * 1.2), wy + Math.sin(angles[k]) * (ra * 1.2));
          ctx.stroke();
        }
      } else if (type === DATA.weftlingTypes.THREADWEAVER) {
        ctx.beginPath();
        for (var a = 0; a < 5; a++) {
          var angle1 = (a / 5) * Math.PI * 2 + (reducedMotion ? 0 : (now * 0.001) % (Math.PI * 2));
          var r = size * 0.4;
          if (a === 0) {
            ctx.moveTo(wx + Math.cos(angle1) * r, wy + Math.sin(angle1) * r);
          } else {
            ctx.lineTo(wx + Math.cos(angle1) * r, wy + Math.sin(angle1) * r);
          }
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      } else if (type === DATA.weftlingTypes.HARMONIZER) {
        ctx.beginPath();
        ctx.arc(wx, wy, size * 0.45, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(wx, wy, size * 0.25, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255,255,255,0.3)';
        ctx.fill();
        ctx.fillStyle = color;
      } else if (type === DATA.weftlingTypes.LOOMGUARD) {
        ctx.beginPath();
        ctx.moveTo(wx + size * 0.4, wy - size * 0.3);
        ctx.lineTo(wx - size * 0.4, wy - size * 0.3);
        ctx.lineTo(wx - size * 0.3, wy + size * 0.3);
        ctx.lineTo(wx + size * 0.3, wy + size * 0.3);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      }
    }
  }

  function drawWeftlingShape(ctx, x, y, size, type, now) {
    ctx.fillStyle = '#FFFFFF';
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 2 * (size / 24);
    if (type === DATA.weftlingTypes.GLIMSPINNER) {
      ctx.beginPath();
      ctx.arc(x, y, size * 0.4, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      for (var j = 0; j < 8; j++) {
        var angle = (j / 8) * Math.PI * 2;
        var r1 = size * 0.5;
        var r2 = size * 0.7;
        if (!reducedMotion) {
          angle += (now * 0.002 + j) % (Math.PI * 2);
        }
        ctx.beginPath();
        ctx.moveTo(x + Math.cos(angle) * r1, y + Math.sin(angle) * r1);
        ctx.lineTo(x + Math.cos(angle) * r2, y + Math.sin(angle) * r2);
        ctx.stroke();
      }
    } else if (type === DATA.weftlingTypes.DRIFTCATCHER) {
      ctx.beginPath();
      ctx.arc(x, y, size * 0.4, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(x, y, size * 0.65, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(x - size * 0.75, y);
      ctx.lineTo(x - size * 1.2, y - size * 0.3);
      ctx.lineTo(x - size * 1.2, y + size * 0.3);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    } else if (type === DATA.weftlingTypes.THREADWEAVER) {
      ctx.beginPath();
      ctx.moveTo(x, y - size * 0.4);
      ctx.lineTo(x + size * 0.3, y + size * 0.2);
      ctx.lineTo(x - size * 0.3, y + size * 0.2);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    } else if (type === DATA.weftlingTypes.HARMONIZER) {
      ctx.beginPath();
      ctx.rect(x - size * 0.4, y - size * 0.4, size * 0.8, size * 0.8);
      ctx.fill();
      ctx.stroke();
      ctx.beginPath();
      ctx.rect(x - size * 0.25, y - size * 0.25, size * 0.5, size * 0.5);
      ctx.fillStyle = '#000000';
      ctx.fill();
      ctx.fillStyle = '#FFFFFF';
    } else if (type === DATA.weftlingTypes.LOOMGUARD) {
      ctx.beginPath();
      ctx.moveTo(x - size * 0.4, y - size * 0.3);
      ctx.lineTo(x + size * 0.4, y - size * 0.3);
      ctx.lineTo(x + size * 0.2, y + size * 0.3);
      ctx.lineTo(x - size * 0.2, y + size * 0.3);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    }
  }

  function drawMotes(state, deltaMs) {
    if (!state.motes || !Array.isArray(state.motes)) return;
    var scale = Math.min(width / CANVAS_WIDTH, height / CANVAS_HEIGHT);
    var now = Date.now();
    var maxMotes = Math.min(state.motes.length, 500);
    for (var i = 0; i < maxMotes; i++) {
      var mote = state.motes[i];
      if (typeof mote.x !== 'number' || typeof mote.y !== 'number') continue;
      if (mote.age > mote.fadeTime) continue;
      var mx = mote.x * scale;
      var my = mote.y * scale;
      var ageRatio = mote.age / mote.fadeTime;
      var radius = MOTE_RADIUS * scale;
      if (colorblindMode === 'DEUTERANOPIA') {
        drawMoteShape(ctx, mx, my, radius, mote, ageRatio, now);
        continue;
      }
      var color = getMoteColor(mote.value || 1);
      if (colorblindMode === 'HIGH_CONTRAST') {
        color = getMoteColor(mote.value || 1);
      }
      var alpha = 1;
      if (ageRatio > 0.8) {
        alpha = 1 - (ageRatio - 0.8) / 0.2;
      }
      if (mote.age < 500) {
        alpha = mote.age / 500;
      }
      if (reducedMotion) {
        radius = MOTE_RADIUS * scale * 1.2;
        ctx.globalAlpha = alpha;
        if (colorblindMode === 'HIGH_CONTRAST') {
          ctx.fillStyle = color;
          ctx.strokeStyle = '#FFFFFF';
        } else {
          ctx.fillStyle = color;
          ctx.strokeStyle = '#FFFFFF';
        }
        ctx.lineWidth = 2 * scale;
        ctx.beginPath();
        ctx.arc(mx, my, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.globalAlpha = 1;
        continue;
      }
      ctx.globalAlpha = alpha;
      if (colorblindMode === 'HIGH_CONTRAST') {
        ctx.fillStyle = color;
        ctx.strokeStyle = '#FFFFFF';
      } else {
        var hue = mote.value === 1 ? 180 : 150;
        var saturation = 80;
        var lightness = mote.value === 1 ? 70 : 80;
        if (ageRatio > 0.8) {
          hue = 0;
          saturation = 100;
          lightness = 50 + (1 - (ageRatio - 0.8) / 0.2) * 50;
        }
        ctx.fillStyle = 'hsl(' + hue + ',' + saturation + '%,' + lightness + '%)';
        ctx.strokeStyle = 'hsl(' + hue + ',' + saturation + '%,' + (lightness + 30) + '%)';
      }
      ctx.lineWidth = 2 * scale;
      var glowRadius = radius * 1.5;
      var gradient = ctx.createRadialGradient(mx, my, 0, mx, my, glowRadius);
      gradient.addColorStop(0, ctx.fillStyle);
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(mx, my, glowRadius, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(mx, my, radius, 0, Math.PI * 2);
      ctx.fill();
      if (colorblindMode !== 'HIGH_CONTRAST') {
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    }
  }

  function drawMoteShape(ctx, x, y, radius, mote, ageRatio, now) {
    ctx.globalAlpha = 1;
    if (ageRatio > 0.8) {
      ctx.fillStyle = '#FFFF00';
      ctx.beginPath();
      ctx.moveTo(x, y - radius * 1.5);
      ctx.lineTo(x - radius * 1.2, y);
      ctx.lineTo(x, y + radius * 1.5);
      ctx.lineTo(x + radius * 1.2, y);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 2;
      ctx.stroke();
      return;
    }
    if (mote.value === 1) {
      ctx.fillStyle = '#FFFFFF';
      ctx.beginPath();
      ctx.arc(x, y, radius * 1.2, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 2;
      ctx.stroke();
    } else {
      ctx.fillStyle = '#FFFFFF';
      ctx.beginPath();
      ctx.rect(x - radius * 1.2, y - radius * 1.2, radius * 2.4, radius * 2.4);
      ctx.fill();
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 2;
      ctx.stroke();
    }
  }

  function drawVictoryOverlay(state) {
    ctx.save();
    ctx.globalAlpha = 0.7;
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.fillRect(0, 0, width, height);
    ctx.globalAlpha = 1;
    var text = 'VICTORY';
    ctx.font = (width * 0.1) + 'px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    if (colorblindMode === 'HIGH_CONTRAST') {
      ctx.fillStyle = '#00FF00';
    } else if (colorblindMode === 'DEUTERANOPIA') {
      ctx.fillStyle = '#FFFFFF';
    } else {
      ctx.fillStyle = '#FFD700';
    }
    ctx.fillText(text, width * 0.5, height * 0.5);
    ctx.restore();
  }

  function drawPauseOverlay(state) {
    ctx.save();
    ctx.globalAlpha = 0.5;
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, width, height);
    ctx.globalAlpha = 1;
    var text = 'PAUSED';
    ctx.font = (width * 0.08) + 'px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    if (colorblindMode === 'HIGH_CONTRAST') {
      ctx.fillStyle = '#FFFFFF';
    } else if (colorblindMode === 'DEUTERANOPIA') {
      ctx.fillStyle = '#FFFFFF';
    } else {
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    }
    ctx.fillText(text, width * 0.5, height * 0.5);
    ctx.restore();
  }

  window.GW.Renderer = {
    CANVAS_WIDTH: CANVAS_WIDTH,
    CANVAS_HEIGHT: CANVAS_HEIGHT,
    MOTE_RADIUS: MOTE_RADIUS,
    AURORA_OPACITY: AURORA_OPACITY,
    init: init,
    render: render,
    setReducedMotion: setReducedMotion,
    setColorblindMode: setColorblindMode,
    resize: resize,
    getMoteColor: getMoteColor,
    getAuroraGradient: getAuroraGradient
  };
})();

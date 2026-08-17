(() => {
  const base = {
    buildUnitElement,
    renderFieldUnits,
    resetCombatState,
    assignActive,
    assignBench,
    quickLineup,
    syncElement,
    selectPlayer,
    startBattle,
    finishBattle,
    resetAll,
  };

  let simRunningV3 = false;
  let simTimerV3 = null;
  let auraTimerV3 = null;
  let cooldownTimerV3 = null;

  const isHotV3 = (p) => !!p && p.alive && ((p.matchPct || 0) + (p.burstPct || 0) >= 25);
  const ensureSetupV3 = (p, i) => {
    if (!p) return;
    if (p.setupX == null) p.setupX = playerSlots[i]?.x ?? .5;
    if (p.setupY == null) p.setupY = playerSlots[i]?.y ?? .75;
  };

  function installUIV3() {
    const titleSpan = document.querySelector('.title span');
    if (titleSpan) titleSpan.textContent = 'Pick 5 starters + 1 bench, position them, then let them handle the violence.';
    const hint = $('setupHint');
    if (hint) hint.textContent = 'Drag five players onto the field, then drag them anywhere in your half to position them. Put one more on the bench.';
    const label = document.querySelector('.benchWrap .labelBox span');
    if (label) label.textContent = 'During battle: drag the bench card onto any active player. The player you pull becomes the new bench.';
    const labelBox = document.querySelector('.benchWrap .labelBox');
    if (labelBox && !$('swapCooldownV3')) labelBox.insertAdjacentHTML('beforeend','<span id="swapCooldownV3" class="cooldown"></span>');

    const feed = [...document.querySelectorAll('.panel')].find(p => p.querySelector('h2')?.textContent.includes('LIVE NFL'));
    if (feed) {
      feed.querySelector('h2').textContent = 'SIMULATED LIVE NFL GAME';
      const box = feed.querySelector('.eventSelected');
      if (box) {
        box.querySelector('b').textContent = 'Click one of your players to focus';
        box.querySelector('span').textContent = 'Fake NFL plays will accumulate heat on that player while you watch.';
        if (!$('simBtnV3')) box.insertAdjacentHTML('afterend', '<div class="simRow"><button class="btn" id="simBtnV3">Start TV plays</button><span class="simState" id="simStateV3">TV mode paused</span></div><div class="focusNote">TV action should be low-attention: choose who you want exposure to and watch the game. Start the autobattle yourself during a commercial, timeout, halftime, or other downtime.</div>');
      }
      feed.querySelectorAll('[data-event] b').forEach(el => { if (!el.textContent.startsWith('TEST')) el.textContent = 'TEST ' + el.textContent; });
    }
    if ($('rematchBtn')) $('rematchBtn').textContent = 'Back to TV / Setup';
    $('simBtnV3')?.addEventListener('click', toggleSimulatorV3);
  }

  buildUnitElement = function(p) {
    const el = base.buildUnitElement(p);
    if (!running && p.team === 'you') {
      el.classList.add('setup');
      el.draggable = true;
      el.ondragstart = (e) => {
        e.dataTransfer.setData('text/plain', p.id);
        e.dataTransfer.setData('source', 'field');
      };
    }
    return el;
  };

  renderFieldUnits = function() {
    clearUnits();
    if (!running) {
      enemy.forEach((p,i) => {
        const sp = pxPos(enemySpawns[i].x, enemySpawns[i].y);
        p.x = sp.x; p.y = sp.y;
        buildUnitElement(p); syncElement(p);
      });
      active.forEach((id,i) => {
        if (!id) return;
        const p = unitById(id); ensureSetupV3(p,i);
        const sp = pxPos(p.setupX,p.setupY);
        p.x = sp.x; p.y = sp.y;
        buildUnitElement(p); syncElement(p);
      });
    } else {
      enemy.forEach(p => { buildUnitElement(p); syncElement(p); });
      activeUnits().forEach(p => { buildUnitElement(p); syncElement(p); });
    }
  };

  assignActive = function(id, slotIndex) {
    const wasActive = active.includes(id);
    base.assignActive(id, slotIndex);
    const p = unitById(id);
    if (p && (!wasActive || p.setupX == null)) {
      p.setupX = playerSlots[slotIndex].x;
      p.setupY = playerSlots[slotIndex].y;
    }
    renderFieldUnits();
  };

  quickLineup = function() {
    base.quickLineup();
    active.forEach((id,i) => { const p = unitById(id); if (p) { p.setupX = playerSlots[i].x; p.setupY = playerSlots[i].y; } });
    renderAll();
  };

  resetCombatState = function() {
    roster.forEach(p => {
      p.currentHp = p.maxHp; p.alive = true; p.lastAttack = 0; p.lastAuraV3 = 0;
      p.burstPct = p.queuedPct; p.queuedPct = 0; p.element = null;
    });
    enemy = enemyTemplates.map(t => cloneTemplate(t,'enemy'));
    active.forEach((id,i) => {
      const p = unitById(id); ensureSetupV3(p,i);
      const sp = pxPos(p.setupX,p.setupY);
      p.x = sp.x; p.y = sp.y; p.homeX = sp.x; p.homeY = sp.y;
    });
    enemy.forEach((p,i) => {
      const sp = pxPos(enemySpawns[i].x,enemySpawns[i].y);
      p.x = sp.x; p.y = sp.y; p.homeX = sp.x; p.homeY = sp.y;
    });
  };

  syncElement = function(p) {
    base.syncElement(p);
    if (p.element) p.element.classList.toggle('onfire', isHotV3(p));
  };

  selectPlayer = function(id) {
    base.selectPlayer(id);
    const p = unitById(id);
    if (simRunningV3 && p?.team === 'you' && $('simStateV3')) $('simStateV3').textContent = `LIVE · focusing ${p.name}`;
  };

  field.addEventListener('dragover', (e) => { if (!running) e.preventDefault(); });
  field.addEventListener('drop', (e) => {
    if (running || e.dataTransfer.getData('source') !== 'field') return;
    e.preventDefault();
    const id = e.dataTransfer.getData('text/plain');
    const p = unitById(id);
    if (!p || p.team !== 'you' || !active.includes(id)) return;
    const r = field.getBoundingClientRect();
    p.setupX = Math.max(.07, Math.min(.93, (e.clientX-r.left)/r.width));
    p.setupY = Math.max(.54, Math.min(.89, (e.clientY-r.top)/r.height));
    renderFieldUnits();
    log(`📍 ${p.name} repositioned.`);
  });

  swapBenchWith = function(activeId) {
    if (!running || Date.now() < swapLockUntil || !benchId) return;
    const incoming = unitById(benchId), outgoing = unitById(activeId);
    if (!incoming || !outgoing || !incoming.alive) return;
    const idx = active.indexOf(activeId); if (idx < 0) return;
    const oldBench = benchId;
    const pos = {x:outgoing.x,y:outgoing.y,homeX:outgoing.homeX,homeY:outgoing.homeY};
    active[idx] = oldBench; benchId = activeId;
    incoming.x = pos.x; incoming.y = pos.y; incoming.homeX = pos.homeX; incoming.homeY = pos.homeY; incoming.element = null;
    outgoing.element?.remove(); outgoing.element = null;
    buildUnitElement(incoming); syncElement(incoming);
    swapLockUntil = Date.now() + 6000;
    log(`🔁 <b>${incoming.name}</b> comes off the bench for ${outgoing.name}. ${outgoing.alive ? 'Pulled player is now the bench.' : 'KO slot filled; the knocked-out player is now stuck on the bench.'}`);
    selectedId = incoming.id; renderBench(); renderRoster(); updateCooldownV3();
  };

  function updateCooldownV3() {
    const el = $('swapCooldownV3'); if (!el) return;
    const cd = running && Date.now() < swapLockUntil ? Math.ceil((swapLockUntil-Date.now())/1000) : 0;
    el.textContent = running ? (cd ? `Bench swap ready in ${cd}s` : 'Bench swap ready') : '';
  }

  applyEvent = function(type) {
    const p = unitById(selectedId);
    if (!p || p.team !== 'you') { log('Select one of your players first.'); return; }
    const map = {big:['BIG PLAY',3,20],score:['TD / HUGE PLAY',5,35],bad:['TURNOVER / BAD PLAY',-2,-15]};
    const [label,match,next] = map[type];
    p.matchPct = Math.max(-25,Math.min(25,p.matchPct+match));
    p.queuedPct = Math.max(-60,Math.min(75,p.queuedPct+next));
    log(`📡 ${label}: <b>${p.name}</b> ${match>=0?'+':''}${match}% now, ${next>=0?'+':''}${next}% next battle.${p.queuedPct>=25?' 🔥 He will enter the next fight ON FIRE.':''}`);
    selectPlayer(p.id);
  };

  function auraTickV3() {
    if (!running) return;
    const now = performance.now();
    activeUnits().forEach(p => {
      if (!isHotV3(p) || now-(p.lastAuraV3||0)<900) return;
      p.lastAuraV3 = now;
      aliveTeam('enemy').filter(q => dist(p,q)<78).forEach(q => damage(q,4.5,p));
    });
  }

  function stopSimulatorV3(logIt=true) {
    const was = simRunningV3;
    simRunningV3 = false; clearTimeout(simTimerV3); simTimerV3 = null;
    if ($('simBtnV3')) $('simBtnV3').textContent = 'Start TV plays';
    if ($('simStateV3')) { $('simStateV3').textContent = 'TV mode paused'; $('simStateV3').classList.remove('live'); }
    if (logIt && was) log('📺 TV play simulator paused.');
  }

  function scheduleSimV3() {
    if (!simRunningV3 || running) return;
    simTimerV3 = setTimeout(() => { simulateTVPlayV3(); scheduleSimV3(); }, 3500 + Math.random()*3500);
  }

  function toggleSimulatorV3() {
    if (running) { log('Finish the autobattle first — TV simulation is for the downtime between fights.'); return; }
    if (simRunningV3) { stopSimulatorV3(); return; }
    const p = unitById(selectedId);
    if (!p || p.team !== 'you') { log('Pick one of your players to focus before starting TV plays.'); return; }
    simRunningV3 = true;
    $('simBtnV3').textContent = 'Pause TV plays'; $('simStateV3').textContent = `LIVE · focusing ${p.name}`; $('simStateV3').classList.add('live');
    log(`📺 Simulated NFL action started. Focus: <b>${p.name}</b>.`); scheduleSimV3();
  }

  function simulateTVPlayV3() {
    const p = unitById(selectedId);
    if (!p || p.team !== 'you') { stopSimulatorV3(false); return; }
    const r = Math.random();
    if (r < .45) {
      p.queuedPct = Math.min(75,p.queuedPct+3);
      log(`📺 Routine positive play: <b>${p.name}</b> banks +3% next-battle heat.`); selectPlayer(p.id);
    } else if (r < .78) applyEvent('big');
    else if (r < .90) applyEvent('score');
    else applyEvent('bad');
  }

  startBattle = function() {
    stopSimulatorV3(true);
    base.startBattle();
    updateCooldownV3();
  };

  finishBattle = function() {
    base.finishBattle();
    if ($('resultText')) $('resultText').textContent += ' Go back to TV mode and let more plays happen before fighting again.';
    if ($('rematchBtn')) $('rematchBtn').textContent = 'Back to TV / Setup';
  };

  nextBattle = function() {
    battleNumber++;
    $('overlay').classList.remove('show'); $('setupHint').classList.remove('hide');
    roster.forEach(p => { p.currentHp=p.maxHp; p.alive=true; p.lastAttack=0; p.lastAuraV3=0; p.burstPct=0; p.element=null; });
    enemy = enemyTemplates.map(t => cloneTemplate(t,'enemy'));
    renderAll(); updateCooldownV3();
    $('status').textContent = `TV / setup mode before Battle ${battleNumber}.`;
    log(`📺 Back to TV / setup mode. Reposition if you want, then start Battle ${battleNumber} during downtime.`);
  };

  function resetAllV3() {
    stopSimulatorV3(false);
    base.resetAll();
    roster.forEach((p,i) => { p.setupX = null; p.setupY = null; p.lastAuraV3 = 0; });
    installUIV3(); updateCooldownV3(); renderAll();
  }

  installUIV3();
  roster.forEach((p,i) => { p.setupX ??= null; p.setupY ??= null; p.lastAuraV3 ??= 0; });
  $('quickBtn').onclick = quickLineup;
  $('startBtn').onclick = startBattle;
  $('resetBtn').onclick = resetAllV3;
  $('rematchBtn').onclick = nextBattle;
  document.querySelectorAll('[data-event]').forEach(b => b.onclick = () => applyEvent(b.dataset.event));
  auraTimerV3 = setInterval(auraTickV3,220);
  cooldownTimerV3 = setInterval(updateCooldownV3,250);
  renderAll();
})();

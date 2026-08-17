(() => {
  const baseBuildV4 = buildUnitElement;
  const baseSyncV4 = syncElement;
  const baseSelectV4 = selectPlayer;

  function installCopyV4() {
    const titleSpan = document.querySelector('.title span');
    if (titleSpan) titleSpan.textContent = 'Pick 5 starters + 1 bench, position them, then beat the snot out of the other team.';

    const rules = [...document.querySelectorAll('.panel')].find(p => p.querySelector('h2')?.textContent.includes('POSITIONS'));
    const rulesSummary = rules?.querySelector('p');
    if (rulesSummary) rulesSummary.textContent = 'Win condition: beat the snot out of everyone on the other team. Practical strategy: knock out their QB while keeping yours standing.';

    const selected = $('selectedStats');
    if (selected && !selectedId) selected.textContent = 'ATK = damage per hit · HP = how much punishment they can take.';
  }

  cardHTML = function(p, locked=false) {
    const hpPct = Math.max(0,100*p.currentHp/p.maxHp);
    const selected = selectedId===p.id ? ' selected' : '';
    const atk = Math.round(power(p));
    const hp = Math.ceil(p.currentHp);
    return `<div class="card${locked?' locked':''}${selected}" draggable="${locked?'false':'true'}" data-card="${p.id}">
      ${!p.alive?'<span class="koBadgeV4">KO</span>':''}
      <b>${p.name} #${p.num}</b><span class="pos">${p.role}</span>
      <small>${roleText(p)}</small>
      <div class="statStripV4"><span class="atkStat"><strong>${atk}</strong><em>ATK</em></span><span class="hpStat"><strong>${hp}</strong><em>HP</em></span></div>
      <div class="tinyhp"><span style="width:${hpPct}%"></span></div>
    </div>`;
  };

  buildUnitElement = function(p) {
    const el = baseBuildV4(p);
    if (!el.querySelector('.unitStatsV4')) {
      const stats = document.createElement('div');
      stats.className = 'unitStatsV4';
      stats.innerHTML = '<span class="atkV4"></span><span class="hpV4"></span>';
      el.appendChild(stats);
    }
    return el;
  };

  syncElement = function(p) {
    baseSyncV4(p);
    if (!p.element) return;
    const atk = p.element.querySelector('.atkV4');
    const hp = p.element.querySelector('.hpV4');
    if (atk) atk.innerHTML = `ATK <b>${Math.round(power(p))}</b>`;
    if (hp) hp.innerHTML = `HP <b>${Math.ceil(p.currentHp)}/${p.maxHp}</b>`;
  };

  selectPlayer = function(id) {
    baseSelectV4(id);
    const p = unitById(id);
    if (!p || p.team !== 'you') return;
    $('selectedStats').textContent = `ATK ${Math.round(power(p))} · HP ${Math.ceil(p.currentHp)}/${p.maxHp} · Match ${p.matchPct>=0?'+':''}${p.matchPct.toFixed(0)}% · Next ${p.queuedPct>=0?'+':''}${p.queuedPct.toFixed(0)}%`;
  };

  $('resetBtn')?.addEventListener('click', () => setTimeout(() => {
    installCopyV4();
    renderAll();
  }, 0));

  installCopyV4();
  renderAll();
})();
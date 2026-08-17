const $ = (id) => document.getElementById(id);
const field = $("field");

const templates = [
  {id:"qb1",name:"Cannon Reed",role:"QB",num:12,hp:95,atk:24,speed:72,range:340,cd:690},
  {id:"qb2",name:"Mason Vale",role:"QB",num:7,hp:105,atk:21,speed:68,range:325,cd:720},
  {id:"ol1",name:"Duke Harris",role:"OL",num:71,hp:145,atk:12,speed:88,range:31,cd:780},
  {id:"ol2",name:"Trey Cole",role:"OL",num:73,hp:155,atk:11,speed:82,range:31,cd:800},
  {id:"ol3",name:"Malik Stone",role:"OL",num:75,hp:138,atk:13,speed:94,range:31,cd:760},
  {id:"ol4",name:"Gabe North",role:"OL",num:68,hp:150,atk:11,speed:85,range:31,cd:800},
  {id:"ol5",name:"Isaac Ford",role:"OL",num:79,hp:142,atk:12,speed:90,range:31,cd:790},
  {id:"dl1",name:"Jalen Ward",role:"DL",num:91,hp:165,atk:9,speed:72,range:34,cd:830},
  {id:"dl2",name:"Bo Mercer",role:"DL",num:94,hp:175,atk:8,speed:67,range:34,cd:850},
  {id:"dl3",name:"Nate Knox",role:"DL",num:96,hp:158,atk:10,speed:75,range:34,cd:820},
  {id:"dl4",name:"Cal Brooks",role:"DL",num:90,hp:168,atk:9,speed:70,range:34,cd:835},
  {id:"dl5",name:"Eli Grant",role:"DL",num:98,hp:160,atk:10,speed:74,range:34,cd:825},
];

const enemyTemplates = [
  {id:"eqb",name:"Rival QB",role:"QB",num:9,hp:100,atk:23,speed:70,range:335,cd:700},
  {id:"eol1",name:"Rival Rush",role:"OL",num:72,hp:150,atk:12,speed:88,range:31,cd:790},
  {id:"eol2",name:"Rival Rush",role:"OL",num:76,hp:145,atk:12,speed:91,range:31,cd:785},
  {id:"edl1",name:"Rival Guard",role:"DL",num:92,hp:170,atk:9,speed:70,range:34,cd:835},
  {id:"edl2",name:"Rival Guard",role:"DL",num:97,hp:165,atk:9,speed:72,range:34,cd:830},
];

const playerSlots = [
  {x:.50,y:.82,label:"BACKFIELD"},
  {x:.28,y:.67,label:"LEFT"},
  {x:.42,y:.62,label:"MID-L"},
  {x:.58,y:.62,label:"MID-R"},
  {x:.72,y:.67,label:"RIGHT"},
];
const enemySpawns = [
  {x:.50,y:.18},{x:.28,y:.33},{x:.72,y:.33},{x:.42,y:.38},{x:.58,y:.38},
];

let roster = [];
let active = [null,null,null,null,null];
let benchId = null;
let enemy = [];
let running = false;
let battleNumber = 1;
let selectedId = null;
let raf = null;
let lastFrame = 0;
let swapLockUntil = 0;
let simRunning = false;
let simTimer = null;

function cloneTemplate(template, team) {
  return {
    ...template,
    team,
    maxHp:template.hp,
    currentHp:template.hp,
    alive:true,
    x:0,y:0,homeX:0,homeY:0,
    setupX:null,setupY:null,
    lastAttack:0,lastAura:0,
    matchPct:0,queuedPct:0,burstPct:0,
    element:null,
  };
}

function isHot(player) {
  return !!player && player.alive && ((player.matchPct || 0) + (player.burstPct || 0) >= 25);
}

function ensureSetup(player, index) {
  if (!player) return;
  if (player.setupX == null) player.setupX = playerSlots[index]?.x ?? .5;
  if (player.setupY == null) player.setupY = playerSlots[index]?.y ?? .75;
}

function resetAll() {
  stopSimulator(false);
  cancelAnimationFrame(raf);
  running = false;
  battleNumber = 1;
  selectedId = null;
  benchId = null;
  active = [null,null,null,null,null];
  swapLockUntil = 0;
  roster = templates.map((t) => cloneTemplate(t,"you"));
  enemy = enemyTemplates.map((t) => cloneTemplate(t,"enemy"));
  $("overlay").classList.remove("show");
  $("setupHint").classList.remove("hide");
  $("log").innerHTML = "";
  $("selectedName").textContent = "Click one of your players to focus";
  $("selectedStats").textContent = "ATK = damage per hit · HP = how much punishment they can take.";
  log("Build a lineup: 5 active + 1 bench.");
  renderAll();
  updateCooldown();
}

function pxPos(nx, ny) { return {x:nx*field.clientWidth, y:ny*field.clientHeight}; }
function unitById(id) { return roster.find((p) => p.id===id) || enemy.find((p) => p.id===id); }
function activeUnits() { return active.map((id) => id ? unitById(id) : null).filter(Boolean); }
function teamUnits(team) { return team === "you" ? activeUnits() : enemy; }
function aliveTeam(team) { return teamUnits(team).filter((p) => p.alive); }
function qbOf(team) { return aliveTeam(team).find((p) => p.role === "QB") || null; }
function remainingRoster() { return roster.filter((p) => !active.includes(p.id) && p.id !== benchId); }
function lineupValid() { return active.every(Boolean) && !!benchId && activeUnits().filter((p) => p.role === "QB").length === 1; }
function power(player) { return player.atk * (1 + (player.matchPct + player.burstPct) / 100); }

function protectionFor(qb) {
  if (!qb || !qb.alive) return 0;
  const guards = aliveTeam(qb.team).filter((p) => p.role === "DL");
  let near = 0;
  for (const guard of guards) if (dist(guard,qb) < 95) near++;
  return Math.min(.5, near * .20);
}

function log(text) {
  const row = document.createElement("div");
  row.className = "line";
  const time = new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit",second:"2-digit"});
  row.innerHTML = `<span class="time">${time}</span> ${text}`;
  $("log").prepend(row);
}

function roleText(player) {
  if (player.role === "QB") return "QB · ranged DPS";
  if (player.role === "OL") return "OL · QB rusher";
  return "DL · QB protector";
}

function cardHTML(player, locked=false) {
  const hpPct = Math.max(0,100*player.currentHp/player.maxHp);
  const selected = selectedId === player.id ? " selected" : "";
  const atk = Math.round(power(player));
  const hp = Math.ceil(player.currentHp);
  return `<div class="card${locked?" locked":""}${selected}" draggable="${locked?"false":"true"}" data-card="${player.id}">
    ${!player.alive?'<span class="koBadge">KO</span>':''}
    <b>${player.name} #${player.num}</b><span class="pos">${player.role}</span>
    <small>${roleText(player)}</small>
    <div class="statStrip"><span class="atkStat"><strong>${atk}</strong><em>ATK</em></span><span class="hpStat"><strong>${hp}</strong><em>HP</em></span></div>
    <div class="tinyhp"><span style="width:${hpPct}%"></span></div>
  </div>`;
}

function renderRoster() {
  const remaining = remainingRoster();
  $("roster").innerHTML = remaining.map((p) => cardHTML(p,running)).join("");
  $("rosterNote").textContent = running
    ? `${remaining.length} alternates locked until the battle ends.`
    : `${remaining.length} still available. Choose 5 starters + 1 bench.`;
  document.querySelectorAll("#roster [data-card]").forEach((el) => {
    el.addEventListener("dragstart", (event) => {
      if (running) return event.preventDefault();
      event.dataTransfer.setData("text/plain",el.dataset.card);
      event.dataTransfer.setData("source","roster");
    });
    el.addEventListener("click", () => selectPlayer(el.dataset.card));
  });
}

function renderBench() {
  const player = benchId ? unitById(benchId) : null;
  $("benchSlot").innerHTML = player
    ? cardHTML(player,false)
    : `<span style="font-size:10px;color:#8c7750;font-weight:900">DROP BENCH PLAYER HERE</span>`;
  $("benchSlot").ondragover = (event) => { event.preventDefault(); $("benchSlot").classList.add("dragover"); };
  $("benchSlot").ondragleave = () => $("benchSlot").classList.remove("dragover");
  $("benchSlot").ondrop = (event) => {
    event.preventDefault();
    $("benchSlot").classList.remove("dragover");
    if (running) return;
    const id = event.dataTransfer.getData("text/plain");
    if (id) assignBench(id);
  };
  const card = $("benchSlot").querySelector("[data-card]");
  if (!card || !player) return;
  card.draggable = true;
  card.addEventListener("dragstart", (event) => {
    event.dataTransfer.setData("text/plain",player.id);
    event.dataTransfer.setData("source","bench");
  });
  card.addEventListener("click", () => selectPlayer(player.id));
}

function renderSlots() {
  field.querySelectorAll(".slot").forEach((el) => el.remove());
  if (running) return;
  playerSlots.forEach((slotData,index) => {
    const slot = document.createElement("div");
    slot.className = "slot" + (active[index] ? " filled" : "");
    slot.style.left = (slotData.x*100) + "%";
    slot.style.top = (slotData.y*100) + "%";
    slot.dataset.slot = index;
    slot.innerHTML = active[index] ? "" : `DROP<br>${slotData.label}`;
    slot.ondragover = (event) => { event.preventDefault(); slot.classList.add("dragover"); };
    slot.ondragleave = () => slot.classList.remove("dragover");
    slot.ondrop = (event) => {
      event.preventDefault();
      slot.classList.remove("dragover");
      const id = event.dataTransfer.getData("text/plain");
      if (id) assignActive(id,index);
    };
    field.appendChild(slot);
  });
}

function selectPlayer(id) {
  if (!id) return;
  selectedId = id;
  const player = unitById(id);
  if (!player) return;
  $("selectedName").textContent = `${player.name} #${player.num} — ${player.role}`;
  $("selectedStats").textContent = `ATK ${Math.round(power(player))} · HP ${Math.ceil(player.currentHp)}/${player.maxHp} · Match ${player.matchPct>=0?"+":""}${player.matchPct.toFixed(0)}% · Next ${player.queuedPct>=0?"+":""}${player.queuedPct.toFixed(0)}%`;
  if (simRunning && player.team === "you") $("simState").textContent = `LIVE · focusing ${player.name}`;
  renderRoster();
  renderBench();
}

function assignActive(id, slotIndex) {
  if (running) return;
  if (benchId === id) benchId = null;
  const oldIndex = active.indexOf(id);
  if (oldIndex >= 0) active[oldIndex] = null;
  const displaced = active[slotIndex];
  active[slotIndex] = id;
  if (displaced && displaced !== id) {
    const empty = active.findIndex((x) => !x);
    if (empty >= 0) active[empty] = displaced;
  }
  const player = unitById(id);
  if (player && player.setupX == null) {
    player.setupX = playerSlots[slotIndex].x;
    player.setupY = playerSlots[slotIndex].y;
  }
  renderAll();
}

function assignBench(id) {
  if (running) return;
  const idx = active.indexOf(id);
  if (idx >= 0) active[idx] = null;
  benchId = id;
  renderAll();
}

function quickLineup() {
  if (running) return;
  active = ["qb1","ol1","ol2","dl1","dl2"];
  benchId = "qb2";
  active.forEach((id,index) => {
    const player = unitById(id);
    if (player) {
      player.setupX = playerSlots[index].x;
      player.setupY = playerSlots[index].y;
    }
  });
  renderAll();
}

function clearUnits() { field.querySelectorAll(".unit").forEach((el) => el.remove()); }

function buildUnitElement(player) {
  const el = document.createElement("div");
  el.className = `unit ${player.team}${!running && player.team === "you" ? " setup" : ""}`;
  el.dataset.unit = player.id;
  el.innerHTML = `<div class="hpBar"><span></span></div><div class="sprite"><div class="helmet"></div><div class="shoulders"><div class="jersey">${player.num}</div></div><div class="legs"></div></div><div class="role">${player.role}</div><div class="name">${player.name}</div><div class="unitStats"><span class="atk"></span><span class="hp"></span></div>`;
  el.addEventListener("click", () => { if (player.team === "you") selectPlayer(player.id); });

  if (player.team === "you") {
    el.draggable = !running;
    el.ondragstart = (event) => {
      if (running) return event.preventDefault();
      event.dataTransfer.setData("text/plain",player.id);
      event.dataTransfer.setData("source","field");
    };
    el.ondragover = (event) => { event.preventDefault(); el.style.filter = "brightness(1.35)"; };
    el.ondragleave = () => { el.style.filter = ""; };
    el.ondrop = (event) => {
      event.preventDefault();
      el.style.filter = "";
      const id = event.dataTransfer.getData("text/plain");
      const source = event.dataTransfer.getData("source");
      if (running && source === "bench" && id === benchId) {
        swapBenchWith(player.id);
        return;
      }
      if (!running && id) {
        const slotIndex = active.indexOf(player.id);
        if (slotIndex >= 0) assignActive(id,slotIndex);
      }
    };
  }

  field.appendChild(el);
  player.element = el;
  return el;
}

function syncElement(player) {
  if (!player.element) return;
  player.element.style.left = player.x + "px";
  player.element.style.top = player.y + "px";
  player.element.classList.toggle("ko",!player.alive);
  player.element.classList.toggle("onfire",isHot(player));
  const hpBar = player.element.querySelector(".hpBar span");
  if (hpBar) hpBar.style.width = Math.max(0,100*player.currentHp/player.maxHp) + "%";
  const atk = player.element.querySelector(".unitStats .atk");
  const hp = player.element.querySelector(".unitStats .hp");
  if (atk) atk.innerHTML = `ATK <b>${Math.round(power(player))}</b>`;
  if (hp) hp.innerHTML = `HP <b>${Math.ceil(player.currentHp)}/${player.maxHp}</b>`;

  let shield = player.element.querySelector(".shield");
  const protection = player.role === "QB" ? protectionFor(player) : 0;
  if (protection > 0 && !shield) {
    shield = document.createElement("div");
    shield.className = "shield";
    shield.textContent = "🛡️";
    player.element.appendChild(shield);
  }
  if (protection <= 0 && shield) shield.remove();
}

function renderFieldUnits() {
  clearUnits();
  if (!running) {
    enemy.forEach((player,index) => {
      const pos = pxPos(enemySpawns[index].x,enemySpawns[index].y);
      player.x = pos.x;
      player.y = pos.y;
      buildUnitElement(player);
      syncElement(player);
    });
    active.forEach((id,index) => {
      if (!id) return;
      const player = unitById(id);
      ensureSetup(player,index);
      const pos = pxPos(player.setupX,player.setupY);
      player.x = pos.x;
      player.y = pos.y;
      buildUnitElement(player);
      syncElement(player);
    });
  } else {
    enemy.forEach((player) => { buildUnitElement(player); syncElement(player); });
    activeUnits().forEach((player) => { buildUnitElement(player); syncElement(player); });
  }
}

function renderAll() {
  renderSlots();
  renderFieldUnits();
  renderBench();
  renderRoster();
  $("startBtn").disabled = running || !lineupValid();
  $("quickBtn").disabled = running;
  if (running) $("status").textContent = `Battle ${battleNumber} · bench swaps live`;
  else if (lineupValid()) $("status").textContent = `TV / setup mode before Battle ${battleNumber}.`;
  else $("status").textContent = "Need 5 active, 1 bench, exactly 1 active QB.";
}

field.addEventListener("dragover", (event) => { if (!running) event.preventDefault(); });
field.addEventListener("drop", (event) => {
  if (running || event.dataTransfer.getData("source") !== "field") return;
  event.preventDefault();
  const id = event.dataTransfer.getData("text/plain");
  const player = unitById(id);
  if (!player || player.team !== "you" || !active.includes(id)) return;
  const rect = field.getBoundingClientRect();
  player.setupX = Math.max(.07,Math.min(.93,(event.clientX-rect.left)/rect.width));
  player.setupY = Math.max(.54,Math.min(.89,(event.clientY-rect.top)/rect.height));
  renderFieldUnits();
  log(`📍 ${player.name} repositioned.`);
});

function resetCombatState() {
  roster.forEach((player) => {
    player.currentHp = player.maxHp;
    player.alive = true;
    player.lastAttack = 0;
    player.lastAura = 0;
    player.burstPct = player.queuedPct;
    player.queuedPct = 0;
    player.element = null;
  });
  enemy = enemyTemplates.map((t) => cloneTemplate(t,"enemy"));
  active.forEach((id,index) => {
    const player = unitById(id);
    ensureSetup(player,index);
    const pos = pxPos(player.setupX,player.setupY);
    player.x = pos.x; player.y = pos.y; player.homeX = pos.x; player.homeY = pos.y;
  });
  enemy.forEach((player,index) => {
    const pos = pxPos(enemySpawns[index].x,enemySpawns[index].y);
    player.x = pos.x; player.y = pos.y; player.homeX = pos.x; player.homeY = pos.y;
  });
}

function startBattle() {
  if (!lineupValid() || running) return;
  stopSimulator(true);
  $("overlay").classList.remove("show");
  $("setupHint").classList.add("hide");
  resetCombatState();
  running = true;
  lastFrame = performance.now();
  log(`⚔️ Battle ${battleNumber} starts. Alternates lock; bench swaps rotate on a 6-second cooldown.`);
  renderAll();
  updateCooldown();
  raf = requestAnimationFrame(loop);
}

function dist(a,b) { return Math.hypot(a.x-b.x,a.y-b.y); }
function nearest(player,list) {
  let best = null;
  let bestDistance = Infinity;
  for (const candidate of list) {
    const distance = dist(player,candidate);
    if (distance < bestDistance) { bestDistance = distance; best = candidate; }
  }
  return best;
}

function targetFor(player) {
  const foeTeam = player.team === "you" ? "enemy" : "you";
  const foes = aliveTeam(foeTeam);
  if (!foes.length) return null;
  const foeQB = qbOf(foeTeam);
  if (player.role === "OL") return foeQB || nearest(player,foes);
  if (player.role === "QB") {
    const close = foes.filter((foe) => dist(player,foe) < 150);
    return close.length ? nearest(player,close) : (foeQB || nearest(player,foes));
  }
  const ownQB = qbOf(player.team);
  if (ownQB) {
    const threats = foes.filter((foe) => dist(foe,ownQB) < 175);
    if (threats.length) return nearest(player,threats);
    const close = foes.filter((foe) => dist(player,foe) < 60);
    if (close.length) return nearest(player,close);
    return null;
  }
  return nearest(player,foes);
}

function guardPoint(player) {
  const qb = qbOf(player.team);
  if (!qb) return {x:player.homeX,y:player.homeY};
  const guards = aliveTeam(player.team).filter((candidate) => candidate.role === "DL");
  const index = Math.max(0,guards.indexOf(player));
  const angle = player.team === "you" ? Math.PI*1.5 + (index-.5)*.55 : Math.PI*.5 + (index-.5)*.55;
  return {x:qb.x+Math.cos(angle)*58,y:qb.y+Math.sin(angle)*58};
}

function moveToward(player,target,dt,stopRange) {
  const dx = target.x-player.x;
  const dy = target.y-player.y;
  const distance = Math.hypot(dx,dy) || 1;
  if (distance <= stopRange) {
    player.element?.classList.remove("walking");
    return;
  }
  const step = Math.min(distance-stopRange,player.speed*dt);
  player.x += dx/distance*step;
  player.y += dy/distance*step;
  const pad = 28;
  player.x = Math.max(pad,Math.min(field.clientWidth-pad,player.x));
  player.y = Math.max(pad,Math.min(field.clientHeight-pad,player.y));
  player.element?.classList.add("walking");
}

function damage(target,raw,attacker) {
  if (!target.alive) return;
  let amount = raw;
  if (target.role === "QB") amount *= 1-protectionFor(target);
  amount *= .88 + Math.random()*.24;
  target.currentHp = Math.max(0,target.currentHp-amount);
  flashHit(target);
  floatDamage(target,amount);
  syncElement(target);
  if (target.currentHp <= 0) {
    target.alive = false;
    target.element?.classList.add("ko");
    syncElement(target);
    log(`💥 <b>${attacker.name}</b> knocks out <b>${target.name}</b>${target.role==="QB"?" — QB DOWN!":""}`);
  }
}

function flashHit(player) {
  const el = player.element;
  if (!el) return;
  el.classList.remove("hit");
  void el.offsetWidth;
  el.classList.add("hit");
  setTimeout(() => el.classList.remove("hit"),170);
}

function floatDamage(player,amount) {
  const label = document.createElement("div");
  label.className = "damage";
  label.textContent = "-" + Math.round(amount);
  label.style.left = player.x + "px";
  label.style.top = (player.y-25) + "px";
  field.appendChild(label);
  setTimeout(() => label.remove(),670);
}

function throwBall(attacker,target) {
  const ball = document.createElement("div");
  ball.className = "projectile";
  ball.textContent = "🏈";
  ball.style.left = attacker.x + "px";
  ball.style.top = attacker.y + "px";
  field.appendChild(ball);
  requestAnimationFrame(() => {
    ball.style.left = target.x + "px";
    ball.style.top = target.y + "px";
  });
  setTimeout(() => ball.remove(),250);
}

function attack(player,target,now) {
  if (!target || !target.alive) return;
  if (dist(player,target) > player.range) return;
  if (now-player.lastAttack < player.cd) return;
  player.lastAttack = now;
  if (player.role === "QB") {
    throwBall(player,target);
    setTimeout(() => { if (target.alive) damage(target,power(player),player); },205);
  } else {
    player.element?.classList.remove("melee");
    void player.element?.offsetWidth;
    player.element?.classList.add("melee");
    damage(target,power(player),player);
  }
}

function act(player,dt,now) {
  if (!player.alive) return;
  const target = targetFor(player);
  if (player.role === "DL" && !target) {
    moveToward(player,guardPoint(player),dt,10);
    syncElement(player);
    return;
  }
  if (!target) return;
  const stop = player.role === "QB" ? Math.min(285,player.range-15) : player.range-4;
  moveToward(player,target,dt,stop);
  attack(player,target,now);
  syncElement(player);
}

function auraTick() {
  if (!running) return;
  const now = performance.now();
  activeUnits().forEach((player) => {
    if (!isHot(player) || now-(player.lastAura||0) < 900) return;
    player.lastAura = now;
    aliveTeam("enemy").filter((enemyPlayer) => dist(player,enemyPlayer) < 78).forEach((enemyPlayer) => damage(enemyPlayer,4.5,player));
  });
}

function loop(now) {
  if (!running) return;
  const dt = Math.min(.035,(now-lastFrame)/1000);
  lastFrame = now;
  activeUnits().forEach((player) => act(player,dt,now));
  enemy.forEach((player) => act(player,dt,now));
  [...activeUnits(),...enemy].forEach(syncElement);
  if (!aliveTeam("you").length || !aliveTeam("enemy").length) {
    finishBattle();
    return;
  }
  raf = requestAnimationFrame(loop);
}

function finishBattle() {
  running = false;
  cancelAnimationFrame(raf);
  const you = aliveTeam("you").length;
  const them = aliveTeam("enemy").length;
  const won = you > them;
  roster.forEach((player) => { player.burstPct = 0; });
  $("resultTitle").textContent = won ? "YOU WIN" : "RIVAL WINS";
  $("resultText").textContent = `${you} of your starters standing vs ${them} rivals. Rest-of-match buffs stay. Next-battle bursts were consumed. Go back to TV mode and let more plays happen before fighting again.`;
  $("overlay").classList.add("show");
  $("status").textContent = won ? "Battle won." : "Battle lost.";
  log(`${won?"🏆":"💥"} Battle ${battleNumber} ends.`);
  renderBench();
  renderRoster();
  updateCooldown();
}

function nextBattle() {
  battleNumber++;
  $("overlay").classList.remove("show");
  $("setupHint").classList.remove("hide");
  roster.forEach((player) => {
    player.currentHp = player.maxHp;
    player.alive = true;
    player.lastAttack = 0;
    player.lastAura = 0;
    player.burstPct = 0;
    player.element = null;
  });
  enemy = enemyTemplates.map((t) => cloneTemplate(t,"enemy"));
  renderAll();
  updateCooldown();
  $("status").textContent = `TV / setup mode before Battle ${battleNumber}.`;
  log(`📺 Back to TV / setup mode. Reposition if you want, then start Battle ${battleNumber} during downtime.`);
}

function swapBenchWith(activeId) {
  if (!running || Date.now() < swapLockUntil || !benchId) return;
  const incoming = unitById(benchId);
  const outgoing = unitById(activeId);
  if (!incoming || !outgoing || !incoming.alive) return;
  const index = active.indexOf(activeId);
  if (index < 0) return;
  const oldBench = benchId;
  const pos = {x:outgoing.x,y:outgoing.y,homeX:outgoing.homeX,homeY:outgoing.homeY};
  active[index] = oldBench;
  benchId = activeId;
  incoming.x = pos.x;
  incoming.y = pos.y;
  incoming.homeX = pos.homeX;
  incoming.homeY = pos.homeY;
  incoming.element = null;
  outgoing.element?.remove();
  outgoing.element = null;
  buildUnitElement(incoming);
  syncElement(incoming);
  swapLockUntil = Date.now() + 6000;
  log(`🔁 <b>${incoming.name}</b> comes off the bench for ${outgoing.name}. ${outgoing.alive ? "Pulled player is now the bench." : "KO slot filled; the knocked-out player is now stuck on the bench."}`);
  selectedId = incoming.id;
  renderBench();
  renderRoster();
  selectPlayer(incoming.id);
  updateCooldown();
}

function updateCooldown() {
  const cd = running && Date.now() < swapLockUntil ? Math.ceil((swapLockUntil-Date.now())/1000) : 0;
  $("swapCooldown").textContent = running ? (cd ? `Bench swap ready in ${cd}s` : "Bench swap ready") : "";
}

function applyEvent(type) {
  const player = unitById(selectedId);
  if (!player || player.team !== "you") {
    log("Select one of your players first.");
    return;
  }
  const map = {
    big:["BIG PLAY",3,20],
    score:["TD / HUGE PLAY",5,35],
    bad:["TURNOVER / BAD PLAY",-2,-15],
  };
  const [label,match,next] = map[type];
  player.matchPct = Math.max(-25,Math.min(25,player.matchPct+match));
  player.queuedPct = Math.max(-60,Math.min(75,player.queuedPct+next));
  const fireReady = player.matchPct + player.queuedPct >= 25;
  log(`📡 ${label}: <b>${player.name}</b> ${match>=0?"+":""}${match}% now, ${next>=0?"+":""}${next}% next battle.${fireReady?" 🔥 He is lined up to enter the next fight ON FIRE.":""}`);
  selectPlayer(player.id);
}

function stopSimulator(logIt=true) {
  const wasRunning = simRunning;
  simRunning = false;
  clearTimeout(simTimer);
  simTimer = null;
  $("simBtn").textContent = "Start TV plays";
  $("simState").textContent = "TV mode paused";
  $("simState").classList.remove("live");
  if (logIt && wasRunning) log("📺 TV play simulator paused.");
}

function scheduleSimulator() {
  if (!simRunning || running) return;
  simTimer = setTimeout(() => {
    simulateTVPlay();
    scheduleSimulator();
  },3500 + Math.random()*3500);
}

function toggleSimulator() {
  if (running) {
    log("Finish the autobattle first — TV simulation is for the downtime between fights.");
    return;
  }
  if (simRunning) {
    stopSimulator();
    return;
  }
  const player = unitById(selectedId);
  if (!player || player.team !== "you") {
    log("Pick one of your players to focus before starting TV plays.");
    return;
  }
  simRunning = true;
  $("simBtn").textContent = "Pause TV plays";
  $("simState").textContent = `LIVE · focusing ${player.name}`;
  $("simState").classList.add("live");
  log(`📺 Simulated NFL action started. Focus: <b>${player.name}</b>.`);
  scheduleSimulator();
}

function simulateTVPlay() {
  const player = unitById(selectedId);
  if (!player || player.team !== "you") {
    stopSimulator(false);
    return;
  }
  const roll = Math.random();
  if (roll < .45) {
    player.queuedPct = Math.min(75,player.queuedPct+3);
    log(`📺 Routine positive play: <b>${player.name}</b> banks +3% next-battle heat.`);
    selectPlayer(player.id);
  } else if (roll < .78) applyEvent("big");
  else if (roll < .90) applyEvent("score");
  else applyEvent("bad");
}

document.querySelectorAll("[data-event]").forEach((button) => {
  button.onclick = () => applyEvent(button.dataset.event);
});
$("quickBtn").onclick = quickLineup;
$("startBtn").onclick = startBattle;
$("resetBtn").onclick = resetAll;
$("rematchBtn").onclick = nextBattle;
$("simBtn").onclick = toggleSimulator;
window.addEventListener("resize", () => { if (!running) renderAll(); });
setInterval(auraTick,220);
setInterval(updateCooldown,250);
resetAll();

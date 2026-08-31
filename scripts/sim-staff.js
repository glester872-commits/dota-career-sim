#!/usr/bin/env node
/**
 * Valida que un agente libre no reciba decisiones del staff.
 * Usage: node scripts/sim-staff.js
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const scripts = [];
const re = /<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi;
let m;
while ((m = re.exec(html))) {
  const code = m[1].trim();
  if (!code || code.includes('DCS.assetsInline')) continue;
  scripts.push(code);
}

const mem = {};
const sandbox = {
  console: { log() {}, warn() {}, error: console.error.bind(console) },
  Date, Math, JSON, parseInt, parseFloat, isNaN, Number, String, Object, Array,
  Boolean, Error, RegExp, setTimeout, clearTimeout, encodeURIComponent, decodeURIComponent,
  localStorage: {
    getItem: (k) => (k in mem ? mem[k] : null),
    setItem: (k, v) => { mem[k] = String(v); },
    removeItem: (k) => { delete mem[k]; }
  },
  document: {
    createElement: () => ({ style: {}, setAttribute() {}, appendChild() {}, classList: { add() {}, remove() {} } }),
    getElementById: () => ({ innerHTML: '', appendChild() {}, querySelector() { return null; }, addEventListener() {} }),
    body: { appendChild() {}, style: {} },
    head: { appendChild() {} },
    querySelector: () => null,
    querySelectorAll: () => [],
    addEventListener() {}
  },
  navigator: { language: 'es' },
  location: { href: 'http://localhost/' },
  requestAnimationFrame: (f) => setTimeout(f, 0),
  confirm: () => true,
  alert() {}
};
sandbox.window = sandbox;
sandbox.self = sandbox;
sandbox.globalThis = sandbox;
const ctx = vm.createContext(sandbox);
for (let i = 0; i < scripts.length; i++) {
  try { vm.runInContext(scripts[i], ctx, { timeout: 30000 }); }
  catch (e) { /* UI boot may fail */ }
}
const DCS = sandbox.DCS;
if (!DCS || !DCS.store || !DCS.engine || !DCS.engine.events || !DCS.engine.world.hasActiveTeam) {
  console.error('Failed to boot DCS staff/FA checks');
  process.exit(1);
}
DCS.store.setSilent(true);

const fails = [];
function ok(cond, msg) {
  if (!cond) fails.push(msg);
}

function newCareer(seed) {
  Object.keys(mem).forEach((k) => delete mem[k]);
  return DCS.store.newState({
    name: 'Staff Test',
    nick: 'faStaff',
    region: 'weu',
    nationality: 'Spain',
    role: 'carry',
    archetype: 'mechanical',
    seed: seed || ('staff-' + Date.now().toString(36))
  });
}

function pickTeam(state) {
  const region = state.player.region;
  return (state.world.teams || []).find((t) => t.region === region)
    || (state.world.teams || [])[0];
}

function sign(state) {
  const team = pickTeam(state);
  ok(!!team, 'hay un equipo para firmar');
  DCS.engine.world.joinTeam(state, team, {
    years: 2,
    salary: 48000,
    prizeShare: 0.1,
    signedYear: state.year,
    expectation: team.expectation
  });
  state.offers = [];
  return team;
}

function staffish(text) {
  return /staff|entrenador|coach|manager|analista|organizaci[oó]n|el vestuario|scrims de equipo/i.test(String(text || ''));
}

function defs() {
  return DCS.data.EVENTS || [];
}

function pool(state, phase) {
  const rng = DCS.runtime.get();
  return defs().filter((d) => {
    if (d.phase !== phase && d.phase !== 'any') return false;
    return DCS.engine.events.canAppear(state, d, rng, state.season);
  });
}

function staffInPool(list) {
  return list.filter((d) => d.requiresStaff || d.requiresActiveTeam || DCS.engine.events.eventNeedsTeam(d));
}

/* ---------- FA never gets staff ---------- */
(function faNeverStaff() {
  const state = newCareer('fa-never-staff');
  ok(!DCS.engine.world.hasActiveTeam(state), 'FA nuevo: sin equipo activo');
  ok(state.player.status === 'amateur' || state.player.status === 'free', 'FA nuevo: status amateur/free');
  if (!(state.offers && state.offers.length)) {
    state.offers = [{
      id: 'offer-pending-test',
      teamId: (pickTeam(state) && pickTeam(state).id) || 't-fake',
      teamName: 'Test Club',
      salary: 20000,
      years: 1,
      tier: 3
    }];
  }
  ok(!!(state.offers && state.offers.length), 'oferta pendiente inyectada');
  ok(!DCS.engine.world.hasActiveTeam(state), 'oferta pendiente no cuenta como pertenencia');
  const pre = pool(state, 'pre');
  const mid = pool(state, 'mid');
  const post = pool(state, 'post');
  ok(staffInPool(pre).length === 0, 'FA pre: 0 eventos de staff/equipo, hay ' + staffInPool(pre).map((d) => d.id).join(','));
  ok(staffInPool(mid).length === 0, 'FA mid: 0 eventos de staff/equipo');
  ok(staffInPool(post).length === 0, 'FA post: 0 eventos de staff/equipo');
  const solo = pre.find((d) => d.id === 'solo_rank_grind');
  ok(!!solo, 'FA puede ver clasificatorias personales');
  ok(!!pre.find((d) => d.id === 'hunt_team'), 'FA puede buscar equipo');
  ok(!!pre.find((d) => d.id === 'free_agent_tryout'), 'FA puede ver tryouts');
  const built = solo.build(DCS.engine.events.buildContext(state, DCS.runtime.get(), state.season));
  ok(!staffish(built.text), 'texto de solo_rank_grind no menciona staff: ' + built.text);
  ok(!staffish(built.title), 'título de solo_rank_grind no menciona staff');

  const drawn = [];
  for (let i = 0; i < 80; i++) {
    const ev = DCS.engine.events.draw(state, DCS.runtime.get(), 'pre', state.season, 1);
    if (ev) drawn.push(ev);
  }
  const badDraw = drawn.filter((ev) => {
    const def = DCS.engine.events.defById(ev.key || ev.pendingKey);
    return def && DCS.engine.events.eventNeedsTeam(def);
  });
  ok(badDraw.length === 0, 'draw FA no guarda eventos de staff: ' + badDraw.map((e) => e.key).join(','));
  const usedStaff = Object.keys(state.usedEvents || {}).filter((id) => {
    const def = DCS.engine.events.defById(id);
    return def && DCS.engine.events.eventNeedsTeam(def);
  });
  ok(usedStaff.length === 0, 'usedEvents FA no registra staff: ' + usedStaff.join(','));
  const personal = drawn.filter((ev) => ev.key === 'solo_rank_grind');
  if (personal.length) {
    ok(!staffish(personal[0].text), 'evento guardado de ranking personal sin staff');
  }
})();

/* ---------- leftover teamId is not membership ---------- */
(function leftoverId() {
  const state = newCareer('fa-leftover-id');
  const team = pickTeam(state);
  state.player.teamId = team.id;
  state.player.status = 'free';
  state.player.contract = null;
  ok(!DCS.engine.world.hasActiveTeam(state), 'teamId histórico no cuenta como equipo activo');
  ok(staffInPool(pool(state, 'pre')).length === 0, 'teamId histórico: sin decisiones de staff');
})();

/* ---------- signing enables staff; leaving disables ---------- */
(function signThenLeave() {
  const state = newCareer('sign-then-leave');
  ok(staffInPool(pool(state, 'pre')).length === 0, 'antes de firmar: sin staff');
  sign(state);
  ok(DCS.engine.world.hasActiveTeam(state), 'tras firmar: equipo activo');
  const signedPool = pool(state, 'pre');
  ok(signedPool.some((d) => d.id === 'staff_rank_grind'), 'tras firmar: staff_rank_grind puede aparecer');
  ok(signedPool.some((d) => d.requiresStaff), 'tras firmar: hay decisiones de staff');
  ok(!signedPool.some((d) => d.id === 'solo_rank_grind'), 'con equipo no sale el grind personal de FA');

  const rng = DCS.runtime.get();
  const staffDef = DCS.engine.events.defById('staff_rank_grind');
  const ctx = DCS.engine.events.buildContext(state, rng, state.season);
  const built = staffDef.build(ctx);
  const inst = {
    id: 'e-staff-test',
    key: 'staff_rank_grind',
    pendingKey: 'staff_rank_grind',
    title: built.title,
    text: built.text,
    requiresStaff: true,
    requiresActiveTeam: true,
    resolved: false,
    applied: false,
    options: built.options.map((o) => ({ label: o.label, hint: o.hint }))
  };
  state.season.events.push(inst);
  const mail = DCS.engine.inbox.pushEvent(state, inst);
  ok(!!mail, 'con equipo se guarda el mensaje del staff');
  ok(mail.fromKey === 'inbox.fromCoach' || mail.fromKey === 'inbox.fromOrg', 'remitente de staff, no sistema');
  const again = DCS.engine.inbox.pushEvent(state, inst);
  ok(again && again.id === mail.id, 'no duplica el mensaje del mismo evento');
  const copies = (state.inbox || []).filter((row) => row.dedupeKey === 'event:' + inst.id);
  ok(copies.length === 1, 'una sola copia en bandeja');

  const formBefore = state.player.form;
  DCS.engine.world.leaveTeam(state, 'test-exit');
  ok(!DCS.engine.world.hasActiveTeam(state), 'tras salir: sin equipo activo');
  ok(inst.cancelled, 'evento de staff pendiente queda cancelado');
  ok(inst.resolved && inst.applied, 'evento cancelado no queda abierto');
  ok(inst.outcomeKey === 'events.staffUnavailable', 'outcome de staff no disponible');
  const leftover = (state.inbox || []).find((row) => row.id === mail.id);
  ok(leftover && leftover.resolved, 'mensaje pendiente se marca resuelto');
  ok(!(leftover.actions && leftover.actions.length), 'acciones del mensaje se vacían');
  ok(leftover.resultKey === 'inbox.staffLeft', 'mensaje usa staffLeft, no se aplica');

  const after = DCS.engine.events.resolve(state, rng, inst, 0, state.season);
  ok(state.player.form === formBefore, 'resolver tras salir no aplica el grind del staff');
  ok(/equipo|staff|team/i.test(String(after || inst.outcome || '')), 'el texto explica que ya no hay equipo');
  ok(staffInPool(pool(state, 'pre')).length === 0, 'tras salir: el pool de staff se cierra otra vez');
})();

/* ---------- old resolved mail stays history; cannot apply ---------- */
(function resolvedHistory() {
  const state = newCareer('resolved-history');
  sign(state);
  const rng = DCS.runtime.get();
  const inst = {
    id: 'e-old-staff',
    key: 'coach_change',
    pendingKey: 'coach_change',
    title: 'Cambio en el staff',
    text: 'El nuevo entrenador ordena el caos.',
    requiresStaff: true,
    requiresActiveTeam: true,
    resolved: true,
    applied: true,
    outcome: 'Ya resuelto hace un año.',
    options: []
  };
  state.season.events.push(inst);
  const keptMail = DCS.engine.inbox.push(state, {
    dedupeKey: 'event:e-old-staff',
    category: 'team',
    fromKey: 'inbox.fromCoach',
    subject: 'Cambio en el staff',
    body: 'El nuevo entrenador ordena el caos.',
    resolved: true,
    resultKey: null,
    result: 'Ya resuelto hace un año.',
    meta: { eventId: inst.id, requiresStaff: true },
    actions: []
  });
  DCS.engine.world.leaveTeam(state, 'history');
  const kept = (state.inbox || []).find((row) => row.dedupeKey === 'event:e-old-staff');
  ok(kept && kept.resolved, 'mensaje antiguo resuelto se conserva');
  ok(kept.result === 'Ya resuelto hace un año.', 'el historial no se reescribe como cancelado');
  ok(!(kept.actions && kept.actions.length), 'historial sin acciones ejecutables');
  void keptMail;
})();

/* ---------- pushEvent refuses staff mail while FA ---------- */
(function noStaffMailFa() {
  const state = newCareer('no-staff-mail');
  const inst = {
    id: 'e-illegal',
    key: 'staff_rank_grind',
    pendingKey: 'staff_rank_grind',
    requiresStaff: true,
    requiresActiveTeam: true,
    resolved: false,
    options: [{ label: 'x' }]
  };
  const mail = DCS.engine.inbox.pushEvent(state, inst);
  ok(mail === null, 'FA: pushEvent no guarda correo del staff');
})();

/* ---------- i18n variants ---------- */
(function i18nKeys() {
  ok(!!DCS.t('events.staffUnavailable'), 'i18n ES staffUnavailable');
  ok(!!DCS.t('events.staff_rank_grind.title'), 'i18n staff_rank_grind.title');
  ok(!!DCS.t('events.solo_rank_grind.title'), 'i18n solo_rank_grind.title');
  ok(!!DCS.t('inbox.staffLeft'), 'i18n inbox.staffLeft');
  const prev = DCS.i18n.getLang && DCS.i18n.getLang();
  DCS.i18n.setLang('en', { render: false });
  ok(/team|staff/i.test(DCS.t('events.staffUnavailable')), 'EN staffUnavailable');
  ok(/ranked/i.test(DCS.t('events.solo_rank_grind.text.neutral')), 'EN solo grind text');
  ok(!/staff/i.test(DCS.t('events.solo_rank_grind.text.neutral')), 'EN solo grind no dice staff');
  ok(/staff/i.test(DCS.t('events.staff_rank_grind.text.neutral')), 'EN staff grind sí menciona staff');
  DCS.i18n.setLang(prev || 'es', { render: false });
})();

if (fails.length) {
  console.error('sim-staff FAILED (' + fails.length + ')');
  fails.forEach((f) => console.error(' - ' + f));
  process.exit(1);
}
console.log('sim-staff OK');

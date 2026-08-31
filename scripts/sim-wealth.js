#!/usr/bin/env node
/**
 * Inversiones parciales: cotización, 90%, ledger e idempotencia.
 * Usage: node scripts/sim-wealth.js
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
  alert() {},
  performance: { now: () => Date.now() }
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
if (!DCS || !DCS.store || !DCS.engine || !DCS.engine.finance || !DCS.engine.finance.quote) {
  console.error('Failed to boot DCS wealth');
  process.exit(1);
}
DCS.store.setSilent(true);

const fails = [];
function ok(cond, msg) {
  if (!cond) fails.push(msg);
}

function career() {
  Object.keys(mem).forEach((k) => delete mem[k]);
  const state = DCS.store.newState({
    name: 'Wealth Test', nick: 'cashlab', region: 'weu', nationality: 'Spain',
    role: 'carry', archetype: 'mechanical', seed: 'wealth-' + Date.now().toString(36)
  });
  DCS.engine.finance.init(state);
  DCS.engine.finance.pull(state);
  state.wealth.cash = 200000;
  return state;
}

const F = DCS.engine.finance;

(function parse() {
  ok(!F.parseAmount('').ok, 'vacío');
  ok(!F.parseAmount('abc').ok, 'texto');
  ok(!F.parseAmount('-10').ok, 'negativo texto');
  ok(!F.parseAmount(-5).ok, 'negativo número');
  ok(!F.parseAmount(0).ok, 'cero');
  ok(!F.parseAmount('10.5').ok, 'decimales');
  ok(!F.parseAmount(Infinity).ok, 'infinito');
  ok(F.parseAmount('25000').ok && F.parseAmount('25000').amount === 25000, 'entero válido');
  ok(F.parseAmount(25000.4).amount === 25000, 'redondeo unidad monetaria');
})();

(function percents() {
  const state = career();
  const cash = 200000;
  [10, 25, 50, 75].forEach((p) => {
    const n = F.amountForPct(state, 'funds', p);
    ok(n === Math.round(cash * p / 100), p + '% = ' + n);
    const q = F.quote(state, 'funds', n);
    ok(q.ok, p + '% cotiza');
    ok(q.remaining === cash - n, p + '% restante');
  });
})();

(function manual() {
  const state = career();
  const q = F.quote(state, 'funds', 40000);
  ok(q.ok && q.amount === 40000 && q.remaining === 160000, 'cantidad manual 40k');
  ok(q.gainMin < 0 && q.gainMax > 0, 'rango muestra pérdidas y ganancias');
})();

(function rejects() {
  const state = career();
  ok(!F.quote(state, 'funds', 0).ok, 'rechaza 0');
  ok(!F.quote(state, 'funds', -1).ok, 'rechaza negativo');
  ok(!F.quote(state, 'funds', 'nope').ok, 'rechaza texto');
  ok(!F.quote(state, 'funds', 500000).ok, 'rechaza más que el cash');
  ok(!F.invest(state, 'funds', 500000).ok, 'invest no descuenta si excede');
  ok(state.wealth.cash === 200000, 'cash intacto tras rechazo');
})();

(function reserve() {
  const state = career();
  const over = F.quote(state, 'funds', 190000);
  ok(!over.ok && over.needsAllInConfirm, '91% exige confirmación extra');
  ok(state.wealth.cash === 200000, 'aún no descuenta');
  const all = F.quote(state, 'funds', 200000);
  ok(!all.ok && all.needsAllInConfirm && all.allIn, '100% exige confirmación de saldo cero');
  const withAck = F.invest(state, 'funds', 190000, { allIn: true, opId: 'op-reserve' });
  ok(withAck.ok && withAck.amount === 190000, 'con ack sí invierte 90%+');
  ok(state.wealth.cash === 10000, 'queda la reserva pedida');
})();

(function confirmDeductsOnlyChosen() {
  const state = career();
  const before = state.wealth.cash;
  const quoted = F.quote(state, 'realEstate', 50000);
  ok(quoted.ok, '50k cotiza');
  ok(state.wealth.cash === before, 'cotizar no descuenta');
  const out = F.invest(state, 'realEstate', 50000, { opId: 'op-50k' });
  ok(out.ok && out.amount === 50000, 'confirma 50k');
  ok(state.wealth.cash === before - 50000, 'solo descuenta lo elegido');
  ok(state.wealth.buckets.realEstate === 50000, 'capital va al cubo');
  ok(out.op && out.op.cashBefore === before && out.op.cashAfter === state.wealth.cash, 'ledger guarda saldos');
})();

(function pnlOnInvestedOnly() {
  const state = career();
  F.invest(state, 'funds', 40000, { opId: 'op-pnl' });
  const cashAfter = state.wealth.cash;
  state.wealth.buckets.funds = 28000; /* pérdida de 12k sobre el capital */
  const snap = F.snapshot(state);
  ok(snap.cash === cashAfter, 'el cash no invertido no absorbe la pérdida');
  ok(snap.pnl === 28000 - 40000, 'P&L solo sobre lo invertido');
  ok(snap.cash >= 0, 'sin saldo negativo');
})();

(function yearTickDoesNotTouchCash() {
  const state = career();
  F.invest(state, 'tech', 20000, { opId: 'op-tick' });
  const cash = state.wealth.cash;
  state.wealth.tickedYear = null;
  F.closeYear(state);
  ok(state.wealth.cash === cash, 'el cierre de año no mueve el cash no invertido (salvo rentas de ladrillo)');
  ok(state.wealth.buckets.tech >= 0, 'el cubo no baja de cero');
  const op = state.wealth.ops.find((o) => o.id === 'op-tick');
  ok(op && op.value >= 0, 'la operación no vale negativo');
})();

(function idempotent() {
  const state = career();
  const a = F.invest(state, 'business', 30000, { opId: 'same-op' });
  const cash = state.wealth.cash;
  const b = F.invest(state, 'business', 30000, { opId: 'same-op' });
  ok(a.ok && b.ok && b.duplicate, 'mismo id no vuelve a descontar');
  ok(state.wealth.cash === cash, 'reload/doble clic no duplica');
  ok(state.wealth.ops.filter((o) => o.id === 'same-op').length === 1, 'una sola operación');
})();

(function twoOps() {
  const state = career();
  F.invest(state, 'funds', 20000, { opId: 'a' });
  F.invest(state, 'esports', 30000, { opId: 'b' });
  const active = state.wealth.ops.filter((o) => o.status === 'active');
  ok(active.length === 2, 'varias operaciones activas');
  ok(state.wealth.cash === 150000, 'cash = 200k - 50k');
})();

(function withdrawReturnsToCash() {
  const state = career();
  F.invest(state, 'funds', 40000, { opId: 'w1' });
  const sold = F.withdraw(state, 'funds', 40000);
  ok(sold.ok && sold.proceeds > 0, 'venta devuelve cash (menos comisión)');
  ok(state.wealth.buckets.funds === 0, 'el cubo se vacía');
  const op = state.wealth.ops.find((o) => o.id === 'w1');
  ok(op && op.status === 'closed', 'la operación se cierra al vender');
})();

(function i18n() {
  ok(!!DCS.t('wealth.confirmTitle'), 'ES confirmTitle');
  DCS.i18n.setLang('en', { render: false });
  ok(/confirm/i.test(DCS.t('wealth.confirmTitle')), 'EN confirmTitle');
  DCS.i18n.setLang('es', { render: false });
})();

if (fails.length) {
  console.error('sim-wealth FAILED (' + fails.length + ')');
  fails.forEach((f) => console.error(' - ' + f));
  process.exit(1);
}
console.log('sim-wealth OK');

#!/usr/bin/env node
/**
 * Batch career simulator for balance checks (TI winrate, any title, GOAT).
 * Usage: node scripts/sim-balance.js [nCareers=600]
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const N = parseInt(process.argv[2] || '600', 10);
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
if (!DCS || !DCS.store || !DCS.engine) {
  console.error('Failed to boot DCS');
  process.exit(1);
}
DCS.store.silent = true;

const ROLES = ['carry', 'mid', 'offlane', 'pos4', 'pos5'];
const ARCH = ['mechanical', 'smart', 'aggressive', 'consistent', 'leader'];
const REGS = Object.keys(DCS.data.REGIONS);

function autoResolvePending(state) {
  let guard = 0;
  while (state.pending && guard++ < 20) {
    if (state.pending.type === 'event') {
      const ev = DCS.engine.season.findUnresolvedEvent(state);
      const n = (ev && ev.options && ev.options.length) || 1;
      const pick = Math.min(n - 1, 0); /* always first option */
      try {
        DCS.engine.season.resolvePendingEvent(state, pick);
      } catch (e) {
        if (ev) {
          ev.resolved = true;
          ev.applied = true;
          ev.outcome = 'resolved';
        }
        state.pending = null;
      }
    } else if (state.pending.type === 'retirement') {
      /* keep playing until age forces it elsewhere */
      state.pending = null;
      state.career.lastRetirementPrompt = state.year;
    } else if (state.pending.type === 'wealth') {
      try { DCS.engine.finance.resolveSpecial(state, false); }
      catch (e) { state.pending = null; }
    } else {
      state.pending = null;
    }
  }
}

function handleOffers(state, rng) {
  const offers = state.offers || [];
  if (!offers.length) return;
  offers.sort((a, b) => a.tier - b.tier || b.salary - a.salary);
  const best = offers[0];
  const p = state.player;
  const team = p.teamId ? DCS.engine.world.getTeam(state, p.teamId) : null;
  let accept = false;
  if (best.tier === 1 && (!team || team.tier > 1)) accept = true;
  else if (!team) accept = true;
  else if (best.tier < team.tier) accept = true;
  else if (!p.contract || p.contract.years <= 1) {
    accept = best.tier <= team.tier && best.salary >= (p.contract && p.contract.salary || 0) * 0.95;
  } else if (best.tier === team.tier && best.salary > (p.contract.salary || 0) * 1.15 && rng.chance(0.4)) accept = true;
  if (accept) {
    DCS.engine.market.acceptOffer(state, best);
    state.offers = [];
  } else {
    offers.slice().forEach((o) => DCS.engine.market.rejectOffer(state, o.id));
  }
}

function playSeason(state) {
  const rng = DCS.runtime.get();
  let steps = 0;
  while (!state.finished && steps++ < 400) {
    autoResolvePending(state);
    if (state.finished) break;

    if (state.offers && state.offers.length) handleOffers(state, rng);

    const live = state.season && state.season.liveTour;
    if (live && !live.done) {
      DCS.engine.season.playLive(state, true);
      continue;
    }
    if (live && live.done) {
      DCS.engine.season.continueCompetition(state);
      continue;
    }

    const phase = state.season ? state.season.phase : 'preseason';
    if (phase === 'competition') {
      const out = DCS.engine.season.continueCompetition(state);
      if (out && out.blocked) {
        autoResolvePending(state);
        continue;
      }
      continue;
    }

    /* preseason / review / market / yearEnd / done */
    if (DCS.engine.preseasonSpecial && state.career && state.career.preseasonSpecial &&
        state.career.preseasonSpecial.status === 'pending') {
      /* 60% accept the gamble */
      DCS.engine.preseasonSpecial.resolve(state, rng.chance(0.6) ? 'accept' : 'reject');
    }

    const report = DCS.engine.season.advance(state);
    if (report && report.blocked && report.reason === 'offers') {
      handleOffers(state, rng);
      continue;
    }
    if (report && report.blocked && report.pending) {
      autoResolvePending(state);
      continue;
    }
    if (state.finished) break;
    if (report && report.legacy) break;

    /* Cap very long careers */
    if (state.player.age >= 36 || state.history.length >= 18) {
      DCS.engine.retirement.retire(state, 'age');
      break;
    }
  }
}

function runOne(i) {
  Object.keys(mem).forEach((k) => delete mem[k]);
  const role = ROLES[i % ROLES.length];
  const region = REGS[i % REGS.length];
  const nat = (DCS.data.REGIONS[region].nationalities || ['Unknown'])[0];
  const state = DCS.store.newState({
    name: 'Sim ' + i,
    nick: 's' + i,
    region,
    nationality: nat,
    role,
    archetype: ARCH[i % ARCH.length],
    seed: 'balance-' + i + '-' + Date.now().toString(36)
  });
  /* Arranque como el jugador (sin inflar T1). BOOST=1 reintroduce un 20% de boost. */
  const BOOST_TIER = process.env.BOOST === '1' && (i % 5) === 0;
  if (BOOST_TIER) {
    const p = state.player;
    p.overall = Math.max(p.overall, 78);
    p.potential = Math.max(p.potential, 88);
    p.reputation = Math.max(p.reputation, 55);
    Object.keys(p.attrs).forEach((k) => { p.attrs[k] = Math.max(p.attrs[k], 70); });
    const team = (state.world.teams || []).filter((t) => t.tier === 1 && t.region === region)[0]
      || (state.world.teams || []).filter((t) => t.tier === 1)[0]
      || (state.world.teams || []).filter((t) => t.tier === 2)[0];
    if (team && DCS.engine.world.joinTeam) {
      try {
        DCS.engine.market.acceptOffer
          ? null
          : null;
        DCS.engine.world.joinTeam(state, team, {
          salary: 80000, years: 2, expectation: team.expectation, bonuses: {}, prizeShare: 0.1
        });
        state.offers = [];
      } catch (e) {}
    }
  }
  playSeason(state);
  if (!state.finished) {
    try { DCS.engine.retirement.retire(state, 'sim'); } catch (e) { /* ignore */ }
  }
  const c = state.career || {};
  let leg = state.legacy || null;
  if (!leg && DCS.engine.retirement && DCS.engine.retirement.computeLegacy) {
    try { leg = DCS.engine.retirement.computeLegacy(state, 'sim'); } catch (e) { leg = null; }
  }
  const cat = leg && (leg.category || leg.tier) || null;
  const bt = (leg && leg.bigTitles && typeof leg.bigTitles === 'object')
    ? (leg.bigTitles.count || 0)
    : (leg && leg.bigTitles) || 0;
  const ty = (state.player && state.player.tierYears) || {};
  let pTier = 9;
  if (ty[1]) pTier = 1;
  else if (ty[2]) pTier = 2;
  else if (ty[3]) pTier = 3;
  return {
    tiWon: c.tiWon || 0,
    titles: c.titles || 0,
    tiPlayed: c.tiPlayed || 0,
    bigTitles: bt,
    score: leg && typeof leg.score === 'number' ? leg.score : null,
    goat: !!(cat && String(cat).indexOf('GOAT') >= 0),
    category: cat,
    years: (state.history && state.history.length) || 0,
    peakTier: pTier,
    t1Years: ty[1] || 0
  };
}

const t0 = Date.now();
let tiWins = 0, anyTitle = 0, goat = 0, tiAndGoat = 0, goatNoTi = 0, errors = 0, tiPlayedN = 0;
let reachedT1 = 0, reachedT2 = 0;
const tiWinners = [];
for (let i = 0; i < N; i++) {
  let r;
  try {
    r = runOne(i);
  } catch (e) {
    errors++;
    process.stderr.write('ERR ' + i + ': ' + (e && e.message) + '\n');
    continue;
  }
  if (r.peakTier === 1) reachedT1++;
  if (r.peakTier <= 2) reachedT2++;
  if (r.tiPlayed > 0) tiPlayedN++;
  if (r.tiWon > 0) {
    tiWins++;
    tiWinners.push(r);
  }
  if (r.titles > 0) anyTitle++;
  if (r.goat) {
    goat++;
    if (r.tiWon > 0) tiAndGoat++;
    else goatNoTi++;
  }
  if ((i + 1) % 50 === 0 || i === N - 1) {
    process.stderr.write('… ' + (i + 1) + '/' + N + '\n');
  }
}
const ms = Date.now() - t0;
const pct = (x) => ((100 * x) / N).toFixed(2) + '%';
const goatAmongTi = tiWins ? ((100 * tiAndGoat) / tiWins).toFixed(1) + '%' : 'n/a';
console.log(JSON.stringify({
  n: N,
  ms,
  errors,
  reachedT1: pct(reachedT1),
  reachedT2: pct(reachedT2),
  tiPlayRate: pct(tiPlayedN),
  tiPlayed: tiPlayedN,
  tiWinRate: pct(tiWins),
  tiWins,
  anyTitleRate: pct(anyTitle),
  anyTitle,
  goatRate: pct(goat),
  goat,
  goatWithTi: tiAndGoat,
  goatNoTi,
  goatShareOfTiWinners: goatAmongTi,
  tiWinnerSample: tiWinners.slice(0, 16).map((r) => ({
    tiWon: r.tiWon, tiPlayed: r.tiPlayed, titles: r.titles,
    bigTitles: r.bigTitles, score: r.score, goat: r.goat, years: r.years, cat: r.category
  })),
  targets: { ti: '3.4–4.2%', anyTitle: '82–84%' }
}, null, 2));

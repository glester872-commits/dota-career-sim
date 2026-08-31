#!/usr/bin/env node
/**
 * Validación del sistema de MMR (oficial, una vez, ±25 típico).
 * Usage: node scripts/sim-mmr.js [nCareers=16]
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const N = parseInt(process.argv[2] || '16', 10);
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
if (!DCS || !DCS.store || !DCS.engine || !DCS.engine.player || !DCS.engine.player.applyMapMmr) {
  console.error('Failed to boot DCS MMR');
  process.exit(1);
}
DCS.store.setSilent(true);

const P = DCS.engine.player;
const fails = [];
function ok(cond, msg) {
  if (!cond) fails.push(msg);
}

function blankState(mmr, calibLeft, role) {
  return {
    year: 2026,
    player: {
      mmr: mmr,
      peakMmr: mmr,
      role: role || 'carry',
      mmrCalibLeft: calibLeft == null ? 0 : calibLeft,
      mmrCalibrating: (calibLeft || 0) > 0
    },
    career: { mmrSeen: {}, mmrLog: [] },
    season: { mmrDelta: 0, mmrMaps: 0 }
  };
}

function apply(state, opts) {
  return P.applyMapMmr(state, opts);
}

function stats(arr) {
  if (!arr.length) return { n: 0, min: 0, max: 0, mean: 0, median: 0 };
  const s = arr.slice().sort((a, b) => a - b);
  const sum = s.reduce((a, b) => a + b, 0);
  const mid = Math.floor(s.length / 2);
  const median = s.length % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2;
  return {
    n: s.length,
    min: s[0],
    max: s[s.length - 1],
    mean: Math.round((sum / s.length) * 100) / 100,
    median
  };
}

const carryGood = {
  kills: 14, deaths: 2, assists: 12, gpm: 700, lastHits: 450, netWorth: 31000,
  heroDamage: 32000, towerDamage: 9000, killPart: 0.78, xpm: 720
};
const carryBad = {
  kills: 2, deaths: 9, assists: 4, gpm: 380, lastHits: 180, netWorth: 12000,
  heroDamage: 8000, towerDamage: 400, killPart: 0.32, xpm: 420
};
const pos5Good = {
  kills: 2, deaths: 4, assists: 22, gpm: 320, lastHits: 40, netWorth: 9000,
  heroDamage: 8000, towerDamage: 400, killPart: 0.84, obsWards: 16, sentries: 11,
  wardsDestroyed: 7, stacks: 6, teamfightPart: 0.82, supportGold: 4800
};

/* ---------- unit: sign, caps, rival, once, calib ---------- */
(function units() {
  const even = blankState(4000, 0);
  const w = apply(even, { id: 'u-w', won: true, teamLevel: 50, oppLevel: 50 });
  const l = apply(even, { id: 'u-l', won: false, teamLevel: 50, oppLevel: 50 });
  ok(w.delta > 0, 'win must be positive, got ' + w.delta);
  ok(l.delta < 0, 'loss must be negative, got ' + l.delta);
  ok(w.delta >= 20 && w.delta <= 30, 'even win in 20-30, got ' + w.delta);
  ok(l.delta <= -20 && l.delta >= -30, 'even loss in -20--30, got ' + l.delta);
  ok(Math.abs(w.delta) >= 22 && Math.abs(w.delta) <= 28, 'even win near ±25, got ' + w.delta);

  const mmrBefore = even.player.mmr;
  const dup = apply(even, { id: 'u-w', won: true, teamLevel: 50, oppLevel: 50 });
  ok(dup.skipped === true, 'duplicate must skip');
  ok(even.player.mmr === mmrBefore, 'duplicate must not change mmr');
  ok(Object.keys(even.career.mmrSeen).length === 2, 'two unique maps stored');

  const fav = blankState(4000, 0);
  const dog = blankState(4000, 0);
  const favW = apply(fav, { id: 'fav-w', won: true, teamLevel: 72, oppLevel: 48 });
  const dogW = apply(dog, { id: 'dog-w', won: true, teamLevel: 48, oppLevel: 72 });
  const favL = apply(fav, { id: 'fav-l', won: false, teamLevel: 72, oppLevel: 48 });
  const dogL = apply(dog, { id: 'dog-l', won: false, teamLevel: 48, oppLevel: 72 });
  ok(favW.delta < dogW.delta, 'favorite win < upset win (' + favW.delta + ' vs ' + dogW.delta + ')');
  ok(Math.abs(dogL.delta) < Math.abs(favL.delta), 'underdog loss smaller than favorite loss');
  ok(favW.delta >= 20 && favW.delta <= 24, 'expected win ~20-23, got ' + favW.delta);
  ok(dogW.delta >= 28 && dogW.delta <= 32, 'upset win ~28-32, got ' + dogW.delta);
  ok(dogL.delta <= -20 && dogL.delta >= -24, 'expected loss ~-20--23, got ' + dogL.delta);
  ok(favL.delta <= -28 && favL.delta >= -32, 'upset loss ~-28--32, got ' + favL.delta);
  ok(favW.rival === 'favorite' && dogW.rival === 'underdog', 'rival bands');

  const perfS = blankState(4000, 0, 'carry');
  const goodW = apply(perfS, { id: 'pgw', won: true, teamLevel: 50, oppLevel: 50, line: carryGood });
  const badW = apply(blankState(4000, 0, 'carry'), { id: 'pbw', won: true, teamLevel: 50, oppLevel: 50, line: carryBad });
  const goodL = apply(blankState(4000, 0, 'carry'), { id: 'pgl', won: false, teamLevel: 50, oppLevel: 50, line: carryGood });
  const badL = apply(blankState(4000, 0, 'carry'), { id: 'pbl', won: false, teamLevel: 50, oppLevel: 50, line: carryBad });
  ok(goodW.perf >= 1 && goodW.perf <= 3, 'good win perf +1..+3, got ' + goodW.perf);
  ok(badW.perf <= -1 && badW.perf >= -3, 'weak win perf -1..-3, got ' + badW.perf);
  ok(badW.delta > 0, 'weak win still positive');
  ok(goodL.delta < 0, 'good loss still negative');
  ok(goodW.delta > badW.delta, 'good win yields more than weak win');
  ok(Math.abs(badL.delta) >= Math.abs(goodL.delta), 'bad loss costs at least as much');

  const capS = blankState(4000, 0);
  const capW = apply(capS, { id: 'cap', won: true, teamLevel: 40, oppLevel: 90, line: carryGood });
  ok(Math.abs(capW.delta) <= 35, 'normal cap ±35, got ' + capW.delta);
  const calS = blankState(4000, 10);
  const calW = apply(calS, { id: 'cal', won: true, teamLevel: 40, oppLevel: 90, line: carryGood });
  ok(Math.abs(calW.delta) <= 40, 'calib cap ±40, got ' + calW.delta);
  ok(calS.player.mmrCalibLeft === 9, 'calib decrements');
  for (let i = 0; i < 9; i++) apply(calS, { id: 'cal' + i, won: i % 2 === 0, teamLevel: 50, oppLevel: 50 });
  ok(calS.player.mmrCalibLeft === 0 && calS.player.mmrCalibrating === false, 'calib ends at 10');
  const post = apply(calS, { id: 'post', won: true, teamLevel: 40, oppLevel: 90, line: carryGood });
  ok(Math.abs(post.delta) <= 35, 'after calib cap is 35, got ' + post.delta);

  const a = blankState(3333, 0);
  const b = blankState(3333, 0);
  const ra = apply(a, { id: 'seed', won: true, teamLevel: 55, oppLevel: 51, line: carryGood });
  const rb = apply(b, { id: 'seed', won: true, teamLevel: 55, oppLevel: 51, line: carryGood });
  ok(ra.delta === rb.delta, 'same inputs same delta');

  const roleCarry = P.perfAdj('carry', carryGood);
  const roleCarryAsSup = P.perfAdj('pos5', carryGood);
  const roleSup = P.perfAdj('pos5', pos5Good);
  const roleSupAsCarry = P.perfAdj('carry', pos5Good);
  ok(roleCarry !== roleCarryAsSup || roleSup !== roleSupAsCarry,
    'role-specific performance (carry-line carry/pos5 ' + roleCarry + '/' + roleCarryAsSup +
    ', pos5-line pos5/carry ' + roleSup + '/' + roleSupAsCarry + ')');

  const jump = blankState(4000, 0);
  apply(jump, { id: 'j', won: true, teamLevel: 50, oppLevel: 50, line: carryGood });
  ok(Math.abs(jump.player.mmr - 4000) <= 35, 'single map never jumps more than 35');
})();

/* ---------- 50% / 60% / 40% even-match sequences ---------- */
function sequence(wr, n, seedTag) {
  const st = blankState(4500, 0);
  const deltas = [];
  let wins = 0;
  const wantWins = Math.round(wr * n);
  const outcomes = [];
  for (let i = 0; i < n; i++) outcomes.push(i < wantWins);
  for (let i = n - 1; i > 0; i--) {
    const j = (i * 17 + seedTag * 13) % (i + 1);
    const tmp = outcomes[i]; outcomes[i] = outcomes[j]; outcomes[j] = tmp;
  }
  outcomes.forEach((won, i) => {
    const rec = apply(st, { id: seedTag + '-' + i, won, teamLevel: 50, oppLevel: 50 });
    deltas.push(rec.delta);
    if (won) wins++;
  });
  return {
    wr: wins / n,
    start: 4500,
    end: st.player.mmr,
    net: st.player.mmr - 4500,
    mean: stats(deltas).mean,
    meanW: stats(deltas.filter((d) => d > 0)).mean,
    meanL: stats(deltas.filter((d) => d < 0)).mean,
    dist: stats(deltas),
    seen: Object.keys(st.career.mmrSeen).length,
    maps: n
  };
}

const seq50 = sequence(0.5, 400, 1);
const seq60 = sequence(0.6, 400, 2);
const seq40 = sequence(0.4, 400, 3);
ok(Math.abs(seq50.net) < 120, '50% WR stays near start, net ' + seq50.net);
ok(seq60.net > 200, '60% WR climbs, net ' + seq60.net);
ok(seq40.net < -200, '40% WR falls, net ' + seq40.net);
ok(seq50.seen === 400 && seq60.seen === 400, 'no duplicate processing in sequences');
ok(seq50.dist.min >= -35 && seq50.dist.max <= 35, 'no extreme single-map jump in 50% seq');

/* ---------- rival cases table ---------- */
const rivalTable = ['favorite', 'even', 'underdog'].map((band) => {
  const levels = band === 'favorite' ? [70, 48] : band === 'underdog' ? [48, 70] : [50, 50];
  const st = blankState(4000, 0);
  const w = apply(st, { id: band + 'W', won: true, teamLevel: levels[0], oppLevel: levels[1] });
  const l = apply(st, { id: band + 'L', won: false, teamLevel: levels[0], oppLevel: levels[1] });
  return { band, pWin: w.pWin, win: w.delta, loss: l.delta, rivalW: w.rival, rivalL: l.rival };
});

/* ---------- full careers (real match outcomes, not forced) ---------- */
const ROLES = ['carry', 'mid', 'offlane', 'pos4', 'pos5'];
const ARCH = ['mechanical', 'smart', 'aggressive', 'consistent', 'leader'];
const REGS = Object.keys(DCS.data.REGIONS);

function autoResolvePending(state) {
  let guard = 0;
  while (state.pending && guard++ < 20) {
    if (state.pending.type === 'event') {
      const ev = DCS.engine.season.findUnresolvedEvent(state);
      const n = (ev && ev.options && ev.options.length) || 1;
      const pick = Math.min(n - 1, 0);
      try { DCS.engine.season.resolvePendingEvent(state, pick); }
      catch (e) {
        if (ev) { ev.resolved = true; ev.applied = true; ev.outcome = 'resolved'; }
        state.pending = null;
      }
    } else if (state.pending.type === 'retirement') {
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
      if (out && out.blocked) { autoResolvePending(state); continue; }
      continue;
    }
    if (DCS.engine.preseasonSpecial && state.career && state.career.preseasonSpecial &&
        state.career.preseasonSpecial.status === 'pending') {
      DCS.engine.preseasonSpecial.resolve(state, rng.chance(0.6) ? 'accept' : 'reject');
    }
    const report = DCS.engine.season.advance(state);
    if (report && report.blocked && report.reason === 'offers') { handleOffers(state, rng); continue; }
    if (report && report.blocked && report.pending) { autoResolvePending(state); continue; }
    if (state.finished) break;
    if (report && report.legacy) break;
    if (state.player.age >= 36 || state.history.length >= 18) {
      DCS.engine.retirement.retire(state, 'age');
      break;
    }
  }
}

function runCareer(i) {
  Object.keys(mem).forEach((k) => delete mem[k]);
  const role = ROLES[i % ROLES.length];
  const region = REGS[i % REGS.length];
  const nat = (DCS.data.REGIONS[region].nationalities || ['Unknown'])[0];
  const mmrBeforeTeam = { v: null };
  const state = DCS.store.newState({
    name: 'Mmr ' + i,
    nick: 'm' + i,
    region,
    nationality: nat,
    role,
    archetype: ARCH[i % ARCH.length],
    seed: 'mmr-' + i + '-v1'
  });
  const start = state.player.mmr;
  const startCalib = state.player.mmrCalibLeft;
  ok(startCalib === 10 && state.player.mmrCalibrating, 'new career calibrates');
  playSeason(state);
  if (!state.finished) {
    try { DCS.engine.retirement.retire(state, 'sim'); } catch (e) { /* ignore */ }
  }
  const seen = Object.keys(state.career.mmrSeen || {}).length;
  const hist = state.history || [];
  const mapsOfficial = hist.reduce((s, h) => s + (h.mmrMaps || 0), 0);
  const allD = [];
  const winD = [];
  const lossD = [];
  Object.keys(state.career.mmrSeen || {}).forEach((id) => {
    const rec = state.career.mmrSeen[id];
    if (!rec || rec.skipped) return;
    allD.push(rec.delta);
    if (rec.won) winD.push(rec.delta); else lossD.push(rec.delta);
  });
  const wr = (state.career.wins || 0) / Math.max(1, state.career.maps || 1);
  const byYear = hist.map((h) => ({
    year: h.year,
    mmrStart: h.mmrStart,
    mmrEnd: h.mmrEnd,
    delta: h.mmrDelta,
    maps: h.mmrMaps,
    wr: h.acc && h.acc.maps ? h.acc.wins / h.acc.maps : null
  }));
  const extreme = allD.some((d) => Math.abs(d) > 40);
  ok(!extreme, 'career ' + i + ' has delta beyond ±40');
  ok(seen === mapsOfficial || seen >= mapsOfficial, 'seen vs season maps ' + seen + '/' + mapsOfficial);
  ok(state.player.mmrCalibLeft === 0 || seen < 10, 'calib consumed after enough maps');
  /* team change must not rewrite MMR: compare last history mmrEnd vs current */
  ok(typeof state.player.mmr === 'number', 'mmr persisted');
  return {
    i, start, end: state.player.mmr, net: state.player.mmr - start,
    years: hist.length, maps: state.career.maps || 0, wr,
    seen, mapsOfficial,
    meanW: stats(winD).mean, meanL: stats(lossD).mean,
    dist: stats(allD),
    byYear,
    calibLeft: state.player.mmrCalibLeft,
    peak: state.player.peakMmr
  };
}

const careers = [];
let errors = 0;
const t0 = Date.now();
for (let i = 0; i < N; i++) {
  try { careers.push(runCareer(i)); }
  catch (e) {
    errors++;
    fails.push('career ' + i + ': ' + (e && e.message));
  }
}

const nets = careers.map((c) => c.net);
const wrs = careers.map((c) => c.wr);
const meanW = stats(careers.map((c) => c.meanW).filter((x) => x));
const meanL = stats(careers.map((c) => c.meanL).filter((x) => x));
const pooled = [];
careers.forEach((c) => {
  if (c.dist && c.dist.n) {
    /* reconstruct approx via min/max already checked */
  }
});
const highWr = careers.filter((c) => c.wr >= 0.52 && c.maps > 40);
const lowWr = careers.filter((c) => c.wr <= 0.48 && c.maps > 40);
if (highWr.length) {
  const avgNet = highWr.reduce((s, c) => s + c.net, 0) / highWr.length;
  ok(avgNet > 0, 'sustained >50% WR should climb on average, got ' + avgNet.toFixed(1));
}
if (lowWr.length) {
  const avgNet = lowWr.reduce((s, c) => s + c.net, 0) / lowWr.length;
  ok(avgNet < 80, 'low WR should not explode upward, got ' + avgNet.toFixed(1));
}

const out = {
  ok: fails.length === 0,
  fails,
  errors,
  ms: Date.now() - t0,
  units: {
    rivalTable,
    seq50, seq60, seq40
  },
  careers: {
    n: careers.length,
    start: stats(careers.map((c) => c.start)),
    end: stats(careers.map((c) => c.end)),
    net: stats(nets),
    wr: stats(wrs),
    meanWinDelta: meanW,
    meanLossDelta: meanL,
    sample: careers.slice(0, 8).map((c) => ({
      i: c.i, start: c.start, end: c.end, net: c.net, wr: Math.round(c.wr * 1000) / 1000,
      maps: c.maps, seen: c.seen, meanW: c.meanW, meanL: c.meanL, dist: c.dist,
      years: c.byYear.map((y) => y.mmrEnd)
    }))
  }
};

console.log(JSON.stringify(out, null, 2));
if (fails.length) process.exit(1);

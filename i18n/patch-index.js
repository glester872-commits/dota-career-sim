#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const INDEX = path.join(ROOT, 'index.html');

let html = fs.readFileSync(INDEX, 'utf8');

const core = fs.readFileSync(path.join(__dirname, 'core.js'), 'utf8');
const es = fs.readFileSync(path.join(__dirname, 'es.js'), 'utf8');
const en = fs.readFileSync(path.join(__dirname, 'en.js'), 'utf8');

const I18N_MARK = '<!-- DCS_I18N_BEGIN -->';
const I18N_END = '<!-- DCS_I18N_END -->';

const i18nBlock =
  I18N_MARK + '\n<script>\n' + core + '\n</script>\n<script>\n' + es +
  '\n</script>\n<script>\n' + en + '\n</script>\n' + I18N_END;

if (html.includes(I18N_MARK)) {
  html = html.replace(new RegExp(I18N_MARK + '[\\s\\S]*?' + I18N_END), i18nBlock);
} else {
  const anchor = '<html lang="es">';
  if (!html.includes(anchor)) throw new Error('html lang anchor missing');
  html = html.replace(anchor, '<html lang="es">\n' + i18nBlock);
}

const LANG_CSS_MARK = '/* DCS_LANG_SWITCH_CSS */';
const langCss = `
${LANG_CSS_MARK}
.lang-switch {
  display: inline-flex; align-items: center; gap: 4px;
  font-family: inherit; font-size: 11px; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--text-3);
}
.lang-switch .lang-btn {
  background: transparent; border: 0; color: inherit; cursor: pointer;
  padding: 4px 6px; min-height: 28px; opacity: 0.55; font: inherit;
  letter-spacing: inherit; text-transform: inherit;
}
.lang-switch .lang-btn:hover,
.lang-switch .lang-btn:focus-visible { opacity: 1; color: var(--text); outline: none; }
.lang-switch .lang-btn.active {
  opacity: 1; color: var(--gold, #d4a84b); font-weight: 700;
}
.lang-switch .lang-sep { opacity: 0.35; user-select: none; }
.hero-foot { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.hero-foot .lang-switch { margin-left: auto; }
.topbar-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.topbar .lang-switch { flex-shrink: 0; }
.about-top-actions { display: flex; align-items: center; gap: 10px; }
@media (max-width: 720px) {
  .lang-switch { font-size: 10px; }
  .lang-switch .lang-btn { padding: 6px 8px; min-height: 36px; }
  .hero-foot { justify-content: center; }
  .hero-foot .lang-switch { margin-left: 0; width: 100%; justify-content: center; }
}

/* DCS_MATE_NAT_CSS */
.mate-line {
  display: inline-flex; align-items: center; gap: 7px; min-width: 0; max-width: 100%;
}
.mate-line .mate-nick { min-width: 0; overflow: hidden; text-overflow: ellipsis; }
.mate-line .mate-country {
  color: var(--text-3, #8b93a7); font-size: 0.86em; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis; max-width: 11em;
}
.mate-nat { display: inline-flex; align-items: center; flex-shrink: 0; line-height: 1; }
.mate-nat .flag-sm, .mate-nat .flag-neutral {
  width: 22px; height: 15px; object-fit: contain; border-radius: 2px;
  box-shadow: 0 0 0 1px rgba(255,255,255,.12); background: #0b0e14;
}
.flag-neutral {
  display: inline-block; box-sizing: border-box;
  background: repeating-linear-gradient(-45deg, #2a3140, #2a3140 3px, #1a1f2a 3px, #1a1f2a 6px);
  border: 1px solid rgba(255,255,255,.14);
}
.flag-sm, .flag-lg { object-fit: contain; }
.mate-roster { display: flex; flex-direction: column; gap: 8px; }
.mate-roster-row {
  display: flex; align-items: center; justify-content: space-between; gap: 10px; min-width: 0;
}
.mate-roster-role { flex-shrink: 0; }
@media (max-width: 720px) {
  .mate-line .mate-country { display: none; }
}

/* DCS_HEROES_INBOX_CSS */
.hero-top-list { display: flex; flex-direction: column; gap: 10px; }
.hero-top-row {
  display: flex; align-items: center; gap: 12px; min-width: 0;
}
.hero-portrait {
  width: 72px; height: 40px; object-fit: cover; border-radius: 3px;
  flex-shrink: 0; background: #0b0e14;
  box-shadow: 0 0 0 1px rgba(255,255,255,.1);
}
.hero-top-name { font-weight: 650; }
.hero-top-meta { font-size: 12px; color: var(--text-3, #8b93a7); }
.mail-list { display: flex; flex-direction: column; gap: 6px; }
.mail-row {
  display: flex; align-items: flex-start; gap: 10px; width: 100%;
  text-align: left; background: rgba(255,255,255,.03);
  border: 1px solid rgba(255,255,255,.06); border-radius: 8px;
  padding: 12px 14px; cursor: pointer; color: inherit; font: inherit;
}
.mail-row:hover { background: rgba(255,255,255,.06); }
.mail-row.unread { border-color: rgba(212,168,75,.35); background: rgba(212,168,75,.06); }
.mail-dot {
  width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex-shrink: 0;
  background: transparent;
}
.mail-row.unread .mail-dot { background: var(--gold, #d4a84b); }
.mail-main { display: flex; flex-direction: column; gap: 2px; min-width: 0; flex: 1; }
.mail-from { font-size: 11px; color: var(--text-3); text-transform: uppercase; letter-spacing: .06em; }
.mail-subject { font-weight: 650; }
.mail-summary { font-size: 13px; color: var(--text-3); }
.mail-side { flex-shrink: 0; }
.mail-cat { font-size: 11px; color: var(--text-3); }
.mail-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.mail-result { margin-top: 10px; }
.nav-inbox-ico { font-size: 14px; opacity: .9; }
.pref-hero-list {
  display: flex; flex-wrap: wrap; gap: 14px; align-items: flex-start;
}
.pref-hero { display: flex; flex-direction: column; gap: 6px; width: 88px; }
.pref-hero .hero-portrait { width: 72px; height: 40px; object-fit: cover; }
.pref-hero-name { font-size: 12px; font-weight: 650; line-height: 1.25; }
@media (max-width: 720px) {
  .pref-hero { width: 72px; }
}
@media (max-width: 720px) {
  .hero-portrait { width: 56px; height: 32px; }
  .mail-row { padding: 10px 12px; }
}
`;

if (html.includes(LANG_CSS_MARK)) {
  html = html.replace(/\/\* DCS_LANG_SWITCH_CSS \*\/[\s\S]*?(?=\n<\/style>)/, langCss.trim() + '\n');
} else {
  html = html.replace('</style>', langCss + '\n</style>');
}

function once(label, find, repl) {
  if (!html.includes(find)) {
    console.warn('SKIP (not found):', label);
    return false;
  }
  html = html.replace(find, repl);
  console.log('OK', label);
  return true;
}

function replaceAllSafe(label, find, repl) {
  if (!html.includes(find)) {
    console.warn('SKIP all (not found):', label);
    return 0;
  }
  const before = html.split(find).length - 1;
  html = html.split(find).join(repl);
  console.log('OK', label, 'x' + before);
  return before;
}

once(
  'bind-archetypes',
  '  DCS.data.ARCHETYPES = ARCHETYPES;\n  DCS.data.ARCHETYPE_LIST = ARCHETYPE_LIST;\n})(window.DCS = window.DCS || {});',
  '  DCS.data.ARCHETYPES = ARCHETYPES;\n  DCS.data.ARCHETYPE_LIST = ARCHETYPE_LIST;\n' +
    '  if (DCS.i18n) { try { DCS.i18n.bindFields(ARCHETYPES, \'arch\', [\'name\', \'desc\', \'pros\', \'cons\']); } catch (e) {} }\n' +
    '})(window.DCS = window.DCS || {});'
);
once(
  'bind-roles',
  '  DCS.data.ROLES = ROLES;\n})(window.DCS = window.DCS || {});',
  '  DCS.data.ROLES = ROLES;\n  if (DCS.i18n) { try { DCS.i18n.bindFields(ROLES, \'role\', [\'label\', \'desc\']); } catch (e) {} }\n})(window.DCS = window.DCS || {});'
);
once(
  'bind-regions',
  '  DCS.data.REGIONS = REGIONS;\n  DCS.data.REGION_LIST = REGION_LIST;\n  DCS.data.NATIONALITIES = NATIONALITIES;',
  '  DCS.data.REGIONS = REGIONS;\n  DCS.data.REGION_LIST = REGION_LIST;\n  DCS.data.NATIONALITIES = NATIONALITIES;\n  if (DCS.i18n) { try { DCS.i18n.bindFields(REGIONS, \'region\', [\'name\']); } catch (e) {} }'
);

once(
  'roundName',
  `  function roundName(r, rounds) {
    var left = rounds - r;
    if (left === 0) return 'Final';
    if (left === 1) return 'Semifinal';
    if (left === 2) return 'Cuartos de final';
    if (left === 3) return 'Octavos de final';
    return 'Ronda ' + r;
  }`,
  `  function roundName(r, rounds) {
    var left = rounds - r;
    if (left === 0) return 'FINAL';
    if (left === 1) return 'SEMIFINALS';
    if (left === 2) return 'QUARTERFINALS';
    if (left === 3) return 'ROUND_OF_16';
    return 'ROUND:' + r;
  }
  function displayStage(stage) {
    if (!stage) return '';
    if (String(stage).indexOf('ROUND:') === 0) {
      return (DCS.i18n && DCS.i18n.t('stage.ROUND_N', { n: String(stage).slice(6) }, 'Ronda ' + String(stage).slice(6))) || ('Ronda ' + String(stage).slice(6));
    }
    return (DCS.i18n && DCS.i18n.stage(stage)) || stage;
  }`
);

once(
  'groupStageName',
  `  function groupStageName(template) {
    return template.kind === 'league' ? 'Liga regular' : 'Fase de grupos';
  }`,
  `  function groupStageName(template) {
    return template.kind === 'league' ? 'LEAGUE' : 'GROUP_STAGE';
  }`
);

once(
  'isGroupStageLabel',
  `  function isGroupStageLabel(stage) {
    return stage === 'Fase de grupos' || stage === 'Liga regular';
  }`,
  `  function isGroupStageLabel(stage) {
    var k = DCS.i18n ? DCS.i18n.stageKey(stage) : stage;
    return k === 'GROUP_STAGE' || k === 'LEAGUE' ||
      stage === 'Fase de grupos' || stage === 'Liga regular' ||
      stage === 'Group Stage' || stage === 'Regular Season';
  }`
);

once(
  'export-displayStage',
  '    formatLabel: formatLabel,',
  '    formatLabel: formatLabel,\n    displayStage: displayStage,\n    groupStageName: groupStageName,'
);

once(
  'getMatchResultType-labels',
  `    var type = 'NORMAL';
    var label = won === true ? 'VICTORIA' : (won === false ? 'DERROTA' : 'EMPATE');

    if (won === true) {
      if (upset) {
        type = 'UPSET';
        label = 'GRAN VICTORIA · UPSET';
      } else if (isComeback()) {
        type = 'COMEBACK';
        label = 'VICTORIA EN REMONTADA';
      } else if (total >= 2 && l === 0 && w >= 2) {
        type = 'DOMINANT';
        label = 'VICTORIA DOMINANTE';
      } else if (total >= 2 && l > 0 && w === l + 1) {
        type = 'CLOSE';
        label = 'VICTORIA AJUSTADA';
      } else {
        type = 'NORMAL';
        label = 'VICTORIA';
      }
    } else if (won === false) {
      if (disappointing) {
        type = 'DISAPPOINTING';
        label = 'DERROTA DECEPCIONANTE';
      } else if (total >= 2 && w === 0 && l >= 2) {
        type = 'DOMINANT';
        label = 'DERROTA CLARA';
      } else if (total >= 2 && w > 0 && l === w + 1) {
        type = 'CLOSE';
        label = 'DERROTA AJUSTADA';
      } else {
        type = 'NORMAL';
        label = 'DERROTA';
      }
    }

    return {
      result: result,
      type: type,
      label: label,
      verdict: won === true ? 'VICTORIA' : (won === false ? 'DERROTA' : 'EMPATE'),
      upset: upset,
      disappointing: disappointing,
      comeback: type === 'COMEBACK'
    };
  }`,
  `    var type = 'NORMAL';

    if (won === true) {
      if (upset) type = 'UPSET';
      else if (isComeback()) type = 'COMEBACK';
      else if (total >= 2 && l === 0 && w >= 2) type = 'DOMINANT';
      else if (total >= 2 && l > 0 && w === l + 1) type = 'CLOSE';
      else type = 'NORMAL';
    } else if (won === false) {
      if (disappointing) type = 'DISAPPOINTING';
      else if (total >= 2 && w === 0 && l >= 2) type = 'DOMINANT';
      else if (total >= 2 && w > 0 && l === w + 1) type = 'CLOSE';
      else type = 'NORMAL';
    }

    var rt = {
      result: result,
      type: type,
      upset: upset,
      disappointing: disappointing,
      comeback: type === 'COMEBACK'
    };
    rt.label = (DCS.i18n && DCS.i18n.matchType(rt)) || (won === true ? 'VICTORIA' : (won === false ? 'DERROTA' : 'EMPATE'));
    rt.verdict = (DCS.i18n && DCS.i18n.matchVerdict(rt)) || rt.label;
    return rt;
  }`
);

(function patchResultLabel() {
  const start = html.indexOf('function resultLabel(placement, field, template)');
  if (start < 0) return console.warn('SKIP resultLabel body');
  const end = html.indexOf('\n  function ', start + 10);
  const chunk = html.slice(start, end > 0 ? end : start + 800);
  let next = chunk
    .replace("return 'Campeón'", "return 'CHAMPION'")
    .replace("return closed ? 'Clasificado al evento' : 'Clasificado'", "return closed ? 'QUALIFIED_EVENT' : 'QUALIFIED'")
    .replace("return 'Subcampeón'", "return 'RUNNER_UP'")
    .replace("return passes ? 'Clasificado' : 'Eliminado en la final'", "return passes ? 'QUALIFIED' : 'ELIMINATED_FINAL'")
    .replace("if (placement === 3) return '3er puesto';", "if (placement === 3) return 'PLACE_3';")
    .replace("if (placement === 4) return '4º puesto';", "if (placement === 4) return 'PLACE_4';")
    .replace("if (placement <= 6) return '5º-6º puesto';", "if (placement <= 6) return 'PLACE_5_6';")
    .replace("if (placement <= 8) return '7º-8º puesto';", "if (placement <= 8) return 'PLACE_7_8';")
    .replace("if (placement <= 12) return '9º-12º puesto';", "if (placement <= 12) return 'PLACE_9_12';")
    .replace("return placement + 'º puesto';", "return 'PLACE:' + placement;");
  html = html.slice(0, start) + next + html.slice(start + chunk.length);
  console.log('OK resultLabel');
})();

replaceAllSafe(
  'elim-groups-result',
  "live.elimReason === 'groups'\n        ? 'Eliminado en fase de grupos'\n        : D.resultLabel(placement, template.field, template)",
  "live.elimReason === 'groups'\n        ? 'ELIMINATED_GROUPS'\n        : D.resultLabel(placement, template.field, template)"
);

replaceAllSafe(
  'early-exit-compare',
  "t.result === 'Eliminado en fase de grupos'",
  "(t.result === 'ELIMINATED_GROUPS' || t.result === 'Eliminado en fase de grupos' || t.result === 'Eliminated in Group Stage')"
);

const DISPLAY_HELPER_MARK = '/* DCS_I18N_DISPLAY_HELPERS */';
if (!html.includes(DISPLAY_HELPER_MARK)) {
  const insertAt = html.indexOf('  S.home = function ()');
  if (insertAt < 0) throw new Error('S.home not found');
  const helpers = `
  ${DISPLAY_HELPER_MARK}
  function t(key, vars, fallback) {
    return (DCS.i18n && DCS.i18n.t(key, vars, fallback)) || fallback || '';
  }
  function tResult(label) {
    if (!label) return '';
    if (String(label).indexOf('PLACE:') === 0) {
      return t('result.PLACE_N', { n: String(label).slice(6) }, String(label).slice(6) + 'º puesto');
    }
    return (DCS.i18n && DCS.i18n.result(label)) || label;
  }
  function tStage(stage) {
    if (!stage) return '';
    if (DCS.engine && DCS.engine.tournaments && DCS.engine.tournaments.displayStage) {
      return DCS.engine.tournaments.displayStage(stage);
    }
    return (DCS.i18n && DCS.i18n.stage(stage)) || stage;
  }
  function tMatch(rt) {
    if (!rt) return '';
    return (DCS.i18n && DCS.i18n.matchType(rt)) || rt.label || '';
  }

`;
  html = html.slice(0, insertAt) + helpers + html.slice(insertAt);
  console.log('OK display helpers');
}

once(
  'home-lead-actions',
  `      '<p class="hero-lead">Construye tu carrera. Cada temporada puede cambiarlo todo.</p>' +
      '<div class="hero-actions">' +
      c.btn('Nueva carrera', 'new-career', { variant: 'primary', size: 'lg' }) +
      (save ? c.btn('Continuar carrera', 'continue', { size: 'lg' }) : '') +
      '</div>';`,
  `      '<p class="hero-lead">' + t('home.lead') + '</p>' +
      '<div class="hero-actions">' +
      c.btn(t('home.newCareer'), 'new-career', { variant: 'primary', size: 'lg' }) +
      (save ? c.btn(t('home.continueCareer'), 'continue', { size: 'lg' }) : '') +
      '</div>';`
);

once(
  'home-wipe',
  `        c.btn('Borrar y empezar de cero', 'wipe', { variant: 'danger' }) +`,
  `        c.btn(t('home.wipe'), 'wipe', { variant: 'danger' }) +`
);

once(
  'home-storage',
  `      html += '<p class="hero-note">Tu navegador ha bloqueado el almacenamiento local; la partida solo vivirá en esta pestaña.</p>';`,
  `      html += '<p class="hero-note">' + t('home.storageBlocked') + '</p>';`
);

once(
  'home-about-foot',
  `    html += '<div class="hero-foot">' +
      '<button type="button" class="about-link" data-action="open-about">Acerca de</button>' +
      '</div>';`,
  `    html += '<div class="hero-foot">' +
      '<button type="button" class="about-link" data-action="open-about">' + t('home.about') + '</button>' +
      (DCS.i18n ? DCS.i18n.langSwitch() : '') +
      '</div>';`
);

(function patchAbout() {
  const start = html.indexOf('  S.about = function ()');
  const end = html.indexOf('  /* ---------------------------------------------------------\n     CREACIÓN DE JUGADOR');
  if (start < 0 || end < 0) return console.warn('SKIP about');
  const next = `  S.about = function () {
    var medalSrc = (DCS.assetsInline && DCS.assetsInline['ancestral-i']) ||
      'assets/ranks/ancestral-i.png';
    var medal = '<div class="creator-medal">' +
      '<img src="' + medalSrc + '" alt="' + t('about.medalAlt') + '" width="110" height="92" loading="lazy">' +
      '<span class="medal-label">' + t('about.medal') + '</span>' +
      '</div>';

    return '<div class="about-page">' +
      '<div class="about-top">' +
      '<div class="about-brand"><i></i><span>DOTA 2</span><b>CAREER</b></div>' +
      '<div class="about-top-actions">' + (DCS.i18n ? DCS.i18n.langSwitch() : '') +
      c.btn(t('about.back'), 'go-home', { variant: 'ghost' }) + '</div>' +
      '</div>' +

      '<header class="about-hero">' +
      '<div class="about-kicker">' + t('about.kicker') + '</div>' +
      '<h1 class="about-tagline"><span>' + t('about.tag1') + '</span><span>' + t('about.tag2') + '</span><span>' + t('about.tag3') + '</span></h1>' +
      '<p class="about-lead">' + t('about.lead') + '</p>' +
      '</header>' +

      '<section class="about-section">' +
      '<h3>' + t('about.s1Title') + '</h3>' +
      '<p>' + t('about.s1p1') + '</p>' +
      '<p>' + t('about.s1p2') + '</p>' +
      '</section>' +

      '<section class="about-section">' +
      '<h3>' + t('about.s2Title') + '</h3>' +
      '<p>' + t('about.s2p1') + '</p>' +
      '<p>' + t('about.s2p2') + '</p>' +
      '</section>' +

      '<section class="about-section">' +
      '<h3>' + t('about.s3Title') + '</h3>' +
      '<p>' + t('about.s3p1') + '</p>' +
      '<div class="about-path" aria-hidden="true">' +
      '<span>' + t('about.path1') + '</span><i>↓</i>' +
      '<span>' + t('about.path2') + '</span><i>↓</i>' +
      '<span>' + t('about.path3') + '</span><i>↓</i>' +
      '<span>' + t('about.path4') + '</span><i>↓</i>' +
      '<span>' + t('about.path5') + '</span><i>↓</i>' +
      '<span>' + t('about.path6') + '</span>' +
      '</div>' +
      '<p class="about-close-q">' + t('about.closeQ') + '</p>' +
      '</section>' +

      '<aside class="creator-card" aria-label="' + t('about.creditsAria') + '">' +
      '<div class="creator-kicker">' + t('about.createdBy') + '</div>' +
      '<p class="creator-name">Lester Daviel Gutiérrez Vidal</p>' +
      '<div class="creator-nick">¨desiigner¨</div>' +
      medal +
      '</aside>' +
      '</div>';
  };

`;
  html = html.slice(0, start) + next + html.slice(end);
  console.log('OK about');
})();

once(
  'NAV-static',
  `  var NAV = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'profile', label: 'Perfil' },
    { id: 'team', label: 'Equipo' },
    { id: 'season', label: 'Temporada' },
    { id: 'tournaments', label: 'Torneos' },
    { id: 'finances', label: 'Patrimonio' },
    { id: 'offers', label: 'Ofertas' },
    { id: 'career', label: 'Carrera' },
    { id: 'legacy', label: 'Legado' }
  ];

  var PHASES = [
    { id: 'preseason', label: 'Pretemporada' },
    { id: 'competition', label: 'Competición' },
    { id: 'review', label: 'Cierre' },
    { id: 'market', label: 'Mercado' },
    { id: 'yearEnd', label: 'Fin de año' }
  ];`,
  `  var NAV_IDS = ['dashboard', 'profile', 'team', 'season', 'tournaments', 'finances', 'offers', 'career', 'legacy'];
  var PHASE_IDS = ['preseason', 'competition', 'review', 'market', 'yearEnd'];
  function navItems() {
    return NAV_IDS.map(function (id) {
      return { id: id, label: t('nav.' + id) };
    });
  }
  function phaseItems() {
    return PHASE_IDS.map(function (id) {
      return { id: id, label: t('phase.' + id) };
    });
  }`
);

replaceAllSafe('NAV.map', 'NAV.map(function (n)', 'navItems().map(function (n)');

(function patchPhaseTrackProperly() {
  const re = /phaseTrack:\s*function\s*\(state\)\s*\{[\s\S]*?\n\s*\},/;
  const m = html.match(re);
  if (!m) return console.warn('SKIP phaseTrack');
  let body = m[0].replace(/\bPHASES\b/g, 'phaseItems()');
  html = html.replace(m[0], body);
  console.log('OK phaseTrack');
})();

once(
  'shell-hud',
  `      var hud = '<div class="hud">' +
        '<div class="hud-item"><span class="hud-k">Edad</span><span class="hud-v">' + p.age + '</span></div>' +
        '<div class="hud-item"><span class="hud-k">Val</span><span class="hud-v" style="color:var(--gold)">' + p.overall + '</span></div>' +
        '<div class="hud-item"><span class="hud-k">MMR</span><span class="hud-v">' + fmt.mmr(p.mmr) + '</span></div>' +
        '<div class="hud-item"><span class="hud-k">Rating</span><span class="hud-v">' + (last === null ? '—' : last) + '</span></div>' +
        '<div class="hud-item"><span class="hud-k">Rep</span><span class="hud-v">' + Math.round(p.reputation) + '</span></div>' +
        '<div class="hud-item"><span class="hud-k">€</span><span class="hud-v">' + fmt.money(DCS.engine.finance.snapshot(state).cash) + '</span></div>' +
        '</div>';`,
  `      var hud = '<div class="hud">' +
        '<div class="hud-item"><span class="hud-k">' + t('hud.age') + '</span><span class="hud-v">' + p.age + '</span></div>' +
        '<div class="hud-item"><span class="hud-k">' + t('hud.overall') + '</span><span class="hud-v" style="color:var(--gold)">' + p.overall + '</span></div>' +
        '<div class="hud-item"><span class="hud-k">' + t('hud.mmr') + '</span><span class="hud-v">' + fmt.mmr(p.mmr) + '</span></div>' +
        '<div class="hud-item"><span class="hud-k">' + t('hud.rating') + '</span><span class="hud-v">' + (last === null ? t('common.none') : last) + '</span></div>' +
        '<div class="hud-item"><span class="hud-k">' + t('hud.rep') + '</span><span class="hud-v">' + Math.round(p.reputation) + '</span></div>' +
        '<div class="hud-item"><span class="hud-k">€</span><span class="hud-v">' + fmt.money(DCS.engine.finance.snapshot(state).cash) + '</span></div>' +
        '</div>';`
);

once(
  'shell-fa-meta',
  `'<span class="meta">' + (team ? c.teamMark(team, 'sm') : 'Agente libre') + '</span></div>' +
        '<div class="topbar-right">' + hud +
        c.badge(state.year, 'info') + '</div></header>' +`,
  `'<span class="meta">' + (team ? c.teamMark(team, 'sm') : t('common.freeAgent')) + '</span></div>' +
        '<div class="topbar-right">' + hud +
        (DCS.i18n ? DCS.i18n.langSwitch({ className: 'lang-switch topbar-lang' }) : '') +
        c.badge(state.year, 'info') + '</div></header>' +`
);

once(
  'shell-home-btn',
  `'<button data-action="go-home">Inicio</button>' +`,
  `'<button data-action="go-home">' + t('common.home') + '</button>' +`
);

once(
  'nav-badges-live',
  `? ' <span class="badge badge-gold">cierre</span>' +
            : ' <span class="badge badge-gold">en juego</span>';`,
  `? ' <span class="badge badge-gold">' + t('nav.closing') + '</span>' +
            : ' <span class="badge badge-gold">' + t('nav.live') + '</span>';`
);

once(
  'advance-series',
  `        return '<div class="advance"><span class="hint">Serie en curso</span><span class="spacer"></span>' +
          c.btn('Simular serie', 'tour-series', { variant: 'primary' }) +
          c.btn('Simular torneo', 'tour-rest', { variant: 'ghost' }) + '</div>';`,
  `        return '<div class="advance"><span class="hint">' + t('tour.seriesInProgress') + '</span><span class="spacer"></span>' +
          c.btn(t('tour.simulateSeries'), 'tour-series', { variant: 'primary' }) +
          c.btn(t('tour.simulateTournament'), 'tour-rest', { variant: 'ghost' }) + '</div>';`
);

once(
  'advance-pending',
  `        return '<div class="advance"><span class="hint">Tienes una decisión pendiente</span>' +
          '<span class="spacer"></span>' + c.btn('Resolver', 'show-pending', { variant: 'primary' }) + '</div>';`,
  `        return '<div class="advance"><span class="hint">' + t('tour.decisionPending') + '</span>' +
          '<span class="spacer"></span>' + c.btn(t('common.resolve'), 'show-pending', { variant: 'primary' }) + '</div>';`
);

once(
  'advance-offers',
  `          ? '<span class="hint gold">' + state.offers.length + ' oferta(s) sin responder</span>' +
          c.btn('Ver ofertas', 'nav', { value: 'offers', variant: 'gold' })
          : c.btn('Saltar al mercado', 'advance-fast', { variant: 'ghost' })) +`,
  `          ? '<span class="hint gold">' + t('tour.offersPending', { count: state.offers.length }) + '</span>' +
          c.btn(t('tour.viewOffers'), 'nav', { value: 'offers', variant: 'gold' })
          : c.btn(t('tour.skipToMarket'), 'advance-fast', { variant: 'ghost' })) +`
);

once(
  'modal-event',
  `        html = '<div class="modal-bg"><div class="modal">' +
          '<div class="modal-head"><div class="modal-kicker">Decisión</div><h3>' + c.esc(ev.title) + '</h3></div>' +
          '<div class="modal-body"><p>' + c.esc(ev.text) + '</p><div class="choices">' +
          ev.options.map(function (o, i) {
            return '<button class="choice" data-action="choose" data-value="' + i + '">' +
              '<b>' + c.esc(o.label) + '</b><span>' + c.esc(o.hint || '') + '</span></button>';
          }).join('') +
          '</div><p class="small muted mt">Nadie te va a decir qué pasa después.</p></div></div></div>';`,
  `        var evView = (DCS.i18n && DCS.i18n.eventView(ev)) || { title: ev.title, text: ev.text, options: ev.options || [] };
        html = '<div class="modal-bg"><div class="modal">' +
          '<div class="modal-head"><div class="modal-kicker">' + t('modal.decision') + '</div><h3>' + c.esc(evView.title) + '</h3></div>' +
          '<div class="modal-body"><p>' + c.esc(evView.text) + '</p><div class="choices">' +
          evView.options.map(function (o, i) {
            return '<button class="choice" data-action="choose" data-value="' + i + '">' +
              '<b>' + c.esc(o.label) + '</b><span>' + c.esc(o.hint || '') + '</span></button>';
          }).join('') +
          '</div><p class="small muted mt">' + t('modal.noSpoilers') + '</p></div></div></div>';`
);

once(
  'modal-retire',
  `        html = '<div class="modal-bg"><div class="modal">' +
          '<div class="modal-head"><div class="modal-kicker">Fin de ciclo</div><h3>¿Ha llegado el momento?</h3></div>' +
          '<div class="modal-body"><p>' + c.esc(d.text) + '</p>' +
          '<ul class="lines">' + d.reasons.map(function (r) { return '<li>' + c.esc(r) + '</li>'; }).join('') + '</ul>' +
          '<div class="choices">' +
          '<button class="choice" data-action="retire-no"><b>Continuar mi carrera</b>' +
          '<span>Seguir intentándolo: bajar de tier, cambiar de región o de rol, reconstruirte.</span></button>' +
          '<button class="choice" data-action="retire-yes"><b>Retirarme</b>' +
          '<span>Cerrar la carrera aquí y descubrir tu legado.</span></button>' +
          '</div></div></div></div>';`,
  `        html = '<div class="modal-bg"><div class="modal">' +
          '<div class="modal-head"><div class="modal-kicker">' + t('modal.endCycle') + '</div><h3>' + t('modal.retireQ') + '</h3></div>' +
          '<div class="modal-body"><p>' + c.esc(d.text) + '</p>' +
          '<ul class="lines">' + d.reasons.map(function (r) { return '<li>' + c.esc(r) + '</li>'; }).join('') + '</ul>' +
          '<div class="choices">' +
          '<button class="choice" data-action="retire-no"><b>' + t('modal.keepPlaying') + '</b>' +
          '<span>' + t('modal.keepPlayingHint') + '</span></button>' +
          '<button class="choice" data-action="retire-yes"><b>' + t('modal.retire') + '</b>' +
          '<span>' + t('modal.retireHint') + '</span></button>' +
          '</div></div></div></div>';`
);

once(
  'modal-wealth',
  `        html = '<div class="modal-bg"><div class="modal">' +
          '<div class="modal-head"><div class="modal-kicker">Dinero</div><h3>' + c.esc(pend.title) + '</h3></div>' +
          '<div class="modal-body"><p>' + c.esc(pend.text) + '</p>' +
          '<p class="small muted">Te piden ' + fmt.money(pend.amount) + ' en ' + c.esc(pend.catName) + '. Nadie te dice qué sale.</p>' +
          '<div class="choices">' +
          '<button class="choice" data-action="wealth-yes"><b>Invertir</b>' +
          '<span>Riesgo alto. Pones el dinero y esperas.</span></button>' +
          '<button class="choice" data-action="wealth-no"><b>Rechazar</b>' +
          '<span>Conservas la liquidez.</span></button>' +
          '</div></div></div></div>';`,
  `        html = '<div class="modal-bg"><div class="modal">' +
          '<div class="modal-head"><div class="modal-kicker">' + t('modal.money') + '</div><h3>' + c.esc(pend.title) + '</h3></div>' +
          '<div class="modal-body"><p>' + c.esc(pend.text) + '</p>' +
          '<p class="small muted">' + t('modal.wealthAsk', { amount: fmt.money(pend.amount), cat: pend.catName }) + '</p>' +
          '<div class="choices">' +
          '<button class="choice" data-action="wealth-yes"><b>' + t('common.invest') + '</b>' +
          '<span>' + t('modal.investHint') + '</span></button>' +
          '<button class="choice" data-action="wealth-no"><b>' + t('common.reject') + '</b>' +
          '<span>' + t('modal.rejectHint') + '</span></button>' +
          '</div></div></div></div>';`
);

if (!html.includes("case 'set-lang':")) {
  const actIdx = html.indexOf("case 'open-about':");
  if (actIdx >= 0) {
    html = html.slice(0, actIdx) +
      "case 'set-lang':\n          if (DCS.i18n) DCS.i18n.setLang(value || 'es');\n          return;\n        " +
      html.slice(actIdx);
    console.log('OK set-lang');
  } else {
    console.warn('SKIP set-lang handler');
  }
}

/* Init i18n when UI boots */
once(
  'i18n-init-boot',
  '  DCS.ui = DCS.ui || {};\n  DCS.ui.screens = S;',
  '  if (DCS.i18n) DCS.i18n.init();\n  DCS.ui = DCS.ui || {};\n  DCS.ui.screens = S;'
);

fs.writeFileSync(INDEX, html);
console.log('Wrote', INDEX, 'size', html.length);

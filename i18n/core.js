/* DCS i18n — lightweight typed-key catalogs (es default, en, ready for more). */
(function (DCS) {
  'use strict';

  var STORAGE_KEY = 'dcs.lang';
  var DEFAULT_LANG = 'es';
  var SUPPORTED = ['es', 'en'];

  var catalogs = Object.create(null);
  var missing = Object.create(null);
  var lang = DEFAULT_LANG;

  function deepGet(obj, path) {
    if (!obj || !path) return undefined;
    var parts = path.split('.');
    var cur = obj;
    for (var i = 0; i < parts.length; i++) {
      if (cur == null || typeof cur !== 'object') return undefined;
      cur = cur[parts[i]];
    }
    return cur;
  }

  function interpolate(str, vars) {
    if (str == null || typeof str !== 'string') return str;
    if (!vars) return str;
    return str.replace(/\{\{(\w+)\}\}/g, function (_, k) {
      return vars[k] != null ? String(vars[k]) : '';
    });
  }

  function pickPlural(forms, count) {
    if (forms == null) return undefined;
    if (typeof forms === 'string') return forms;
    var n = Math.abs(Number(count)) || 0;
    if (typeof forms === 'object') {
      if (n === 1 && forms.one != null) return forms.one;
      if (forms.other != null) return forms.other;
      if (forms.one != null) return forms.one;
    }
    return undefined;
  }

  function asString(val, vars) {
    if (val == null) return undefined;
    if (typeof val === 'object') {
      if (val.one != null || val.other != null) {
        val = pickPlural(val, vars && vars.count);
      } else {
        return undefined; /* nested dict — not a leaf string */
      }
    }
    if (val == null || val === '') return undefined;
    return interpolate(String(val), vars);
  }

  function resolve(key, vars, fallback) {
    var primary = asString(deepGet(catalogs[lang], key), vars);
    if (primary != null) return primary;

    if (lang !== DEFAULT_LANG) {
      var fb = asString(deepGet(catalogs[DEFAULT_LANG], key), vars);
      if (fb != null) {
        if (typeof console !== 'undefined' && console.warn && !missing[lang + ':' + key]) {
          missing[lang + ':' + key] = 1;
          console.warn('[i18n] missing ' + lang + ' key:', key);
        }
        return fb;
      }
    }

    if (fallback != null && fallback !== '') return interpolate(String(fallback), vars);

    if (typeof console !== 'undefined' && console.warn && !missing['?:' + key]) {
      missing['?:' + key] = 1;
      console.warn('[i18n] missing key:', key);
    }
    return '';
  }

  function readStored() {
    try {
      var v = localStorage.getItem(STORAGE_KEY);
      if (v && SUPPORTED.indexOf(v) >= 0) return v;
    } catch (e) { /* ignore */ }
    return DEFAULT_LANG;
  }

  function writeStored(v) {
    try { localStorage.setItem(STORAGE_KEY, v); } catch (e) { /* ignore */ }
  }

  function setDocumentLang(v) {
    try {
      if (document && document.documentElement) document.documentElement.lang = v;
    } catch (e) { /* ignore */ }
  }

  /* Known Spanish (and code) stage labels → stable keys */
  var STAGE_ALIASES = {
    'Fase de grupos': 'GROUP_STAGE',
    'Group Stage': 'GROUP_STAGE',
    'GROUP_STAGE': 'GROUP_STAGE',
    'Liga regular': 'LEAGUE',
    'Regular Season': 'LEAGUE',
    'LEAGUE': 'LEAGUE',
    'Final': 'FINAL',
    'Grand Final': 'FINAL',
    'FINAL': 'FINAL',
    'Semifinal': 'SEMIFINALS',
    'Semifinals': 'SEMIFINALS',
    'SEMIFINALS': 'SEMIFINALS',
    'Cuartos de final': 'QUARTERFINALS',
    'Quarterfinals': 'QUARTERFINALS',
    'QUARTERFINALS': 'QUARTERFINALS',
    'Octavos de final': 'ROUND_OF_16',
    'Round of 16': 'ROUND_OF_16',
    'ROUND_OF_16': 'ROUND_OF_16',
    'Open Qualifier': 'OPEN_QUALIFIER',
    'OPEN_QUALIFIER': 'OPEN_QUALIFIER',
    'Closed Qualifier': 'CLOSED_QUALIFIER',
    'CLOSED_QUALIFIER': 'CLOSED_QUALIFIER'
  };

  var RESULT_ALIASES = {
    'Eliminado en fase de grupos': 'ELIMINATED_GROUPS',
    'Eliminated in Group Stage': 'ELIMINATED_GROUPS',
    'ELIMINATED_GROUPS': 'ELIMINATED_GROUPS',
    'Clasificado': 'QUALIFIED',
    'Qualified': 'QUALIFIED',
    'QUALIFIED': 'QUALIFIED',
    'Clasificado al evento': 'QUALIFIED_EVENT',
    'Qualified for the event': 'QUALIFIED_EVENT',
    'QUALIFIED_EVENT': 'QUALIFIED_EVENT',
    'Eliminado en la final': 'ELIMINATED_FINAL',
    'Eliminated in the Final': 'ELIMINATED_FINAL',
    'ELIMINATED_FINAL': 'ELIMINATED_FINAL',
    'Eliminado': 'ELIMINATED',
    'Eliminated': 'ELIMINATED',
    'ELIMINATED': 'ELIMINATED',
    'Campeón': 'CHAMPION',
    'Champion': 'CHAMPION',
    'CHAMPION': 'CHAMPION',
    'Subcampeón': 'RUNNER_UP',
    'Runner-up': 'RUNNER_UP',
    'RUNNER_UP': 'RUNNER_UP',
    '3er puesto': 'PLACE_3',
    '3rd place': 'PLACE_3',
    'PLACE_3': 'PLACE_3',
    '4º puesto': 'PLACE_4',
    '4th place': 'PLACE_4',
    'PLACE_4': 'PLACE_4',
    '5º-6º puesto': 'PLACE_5_6',
    '5th–6th place': 'PLACE_5_6',
    'PLACE_5_6': 'PLACE_5_6',
    '7º-8º puesto': 'PLACE_7_8',
    '7th–8th place': 'PLACE_7_8',
    'PLACE_7_8': 'PLACE_7_8',
    '9º-12º puesto': 'PLACE_9_12',
    '9th–12th place': 'PLACE_9_12',
    'PLACE_9_12': 'PLACE_9_12',
    'Eliminado en cuartos': 'ELIMINATED_QF',
    'Eliminated in Quarterfinals': 'ELIMINATED_QF',
    'ELIMINATED_QF': 'ELIMINATED_QF',
    'Eliminado en semifinales': 'ELIMINATED_SF',
    'Eliminated in Semifinals': 'ELIMINATED_SF',
    'ELIMINATED_SF': 'ELIMINATED_SF',
    'Eliminado en la clasificatoria': 'ELIMINATED_QUALIFIER',
    'Eliminated in Qualifiers': 'ELIMINATED_QUALIFIER',
    'ELIMINATED_QUALIFIER': 'ELIMINATED_QUALIFIER'
  };

  var MATCH_LABEL_KEYS = {
    WIN_NORMAL: 'match.victory',
    WIN_DOMINANT: 'match.dominantWin',
    WIN_CLOSE: 'match.closeWin',
    WIN_COMEBACK: 'match.comebackWin',
    WIN_UPSET: 'match.upsetWin',
    LOSS_NORMAL: 'match.defeat',
    LOSS_DOMINANT: 'match.clearLoss',
    LOSS_CLOSE: 'match.closeLoss',
    LOSS_DISAPPOINTING: 'match.disappointingLoss',
    DRAW: 'match.draw',
    VERDICT_WIN: 'match.victory',
    VERDICT_LOSS: 'match.defeat',
    VERDICT_DRAW: 'match.draw'
  };

  function stageKey(stage) {
    if (!stage) return '';
    if (STAGE_ALIASES[stage]) return STAGE_ALIASES[stage];
    if (/^Ronda\s+(\d+)$/i.test(stage) || /^Round\s+(\d+)$/i.test(stage)) {
      return 'ROUND_N';
    }
    return String(stage);
  }

  function resultKey(label) {
    if (!label) return '';
    if (RESULT_ALIASES[label]) return RESULT_ALIASES[label];
    var m = String(label).match(/^(\d+)[º°]?(\s*puesto|\s*place)?$/i);
    if (m) return 'PLACE_N';
    return String(label);
  }

  var i18n = {
    DEFAULT_LANG: DEFAULT_LANG,
    SUPPORTED: SUPPORTED.slice(),
    catalogs: catalogs,
    missing: missing,

    register: function (code, dict) {
      if (!code || !dict) return;
      catalogs[code] = dict;
      if (SUPPORTED.indexOf(code) < 0) SUPPORTED.push(code);
    },

    getLang: function () { return lang; },

    setLang: function (code, opts) {
      if (SUPPORTED.indexOf(code) < 0 && !catalogs[code]) return lang;
      lang = code;
      writeStored(code);
      setDocumentLang(code);
      if (!opts || opts.render !== false) {
        try {
          if (DCS.ui && DCS.ui.app && typeof DCS.ui.app.render === 'function') {
            DCS.ui.app.render();
          }
        } catch (e) { /* ignore */ }
      }
      return lang;
    },

    t: function (key, vars, fallback) {
      return resolve(key, vars || null, fallback);
    },

    tn: function (key, count, vars, fallback) {
      var v = vars ? Object.assign({}, vars) : {};
      v.count = count;
      return resolve(key, v, fallback);
    },

    /* Format helpers — presentation only */
    number: function (n, opts) {
      try {
        return new Intl.NumberFormat(lang === 'en' ? 'en-US' : 'es-ES', opts || {}).format(n);
      } catch (e) {
        return String(n);
      }
    },

    money: function (n) {
      try {
        return new Intl.NumberFormat(lang === 'en' ? 'en-US' : 'es-ES', {
          style: 'currency', currency: 'EUR', maximumFractionDigits: 0
        }).format(n);
      } catch (e) {
        return '€' + String(n);
      }
    },

    stageKey: stageKey,
    resultKey: resultKey,

    stage: function (stage, vars) {
      var k = stageKey(stage);
      if (k === 'ROUND_N') {
        var n = (String(stage).match(/(\d+)/) || [])[1] || '';
        return resolve('stage.ROUND_N', Object.assign({ n: n }, vars || {}), stage);
      }
      return resolve('stage.' + k, vars, stage);
    },

    result: function (label, vars) {
      var k = resultKey(label);
      if (k === 'PLACE_N') {
        var n = (String(label).match(/(\d+)/) || [])[1] || '';
        return resolve('result.PLACE_N', Object.assign({ n: n }, vars || {}), label);
      }
      if (RESULT_ALIASES[label] || RESULT_ALIASES[k]) {
        return resolve('result.' + k, vars, label);
      }
      /* Unknown legacy string — show as-is */
      return label;
    },

    matchType: function (rt) {
      if (!rt) return '';
      var result = rt.result || (rt.won === true ? 'WIN' : (rt.won === false ? 'LOSS' : 'DRAW'));
      var type = rt.type || 'NORMAL';
      var key;
      if (result === 'DRAW') key = MATCH_LABEL_KEYS.DRAW;
      else if (result === 'WIN') {
        key = MATCH_LABEL_KEYS['WIN_' + type] || MATCH_LABEL_KEYS.WIN_NORMAL;
      } else {
        key = MATCH_LABEL_KEYS['LOSS_' + type] || MATCH_LABEL_KEYS.LOSS_NORMAL;
      }
      return resolve(key, null, rt.label || '');
    },

    matchVerdict: function (rt) {
      if (!rt) return '';
      var result = rt.result || 'DRAW';
      var key = result === 'WIN' ? MATCH_LABEL_KEYS.VERDICT_WIN
        : (result === 'LOSS' ? MATCH_LABEL_KEYS.VERDICT_LOSS : MATCH_LABEL_KEYS.VERDICT_DRAW);
      return resolve(key, null, rt.verdict || '');
    },

    /** Re-resolve event copy at display time (language-switch safe). */
    eventView: function (ev) {
      if (!ev) return { title: '', text: '', options: [] };
      var key = ev.key || ev.pendingKey || '';
      var vars = ev.vars || {};
      var title = key
        ? resolve('events.' + key + '.title', vars, ev.title || '')
        : (ev.title || '');
      var text = '';
      if (ev.textKey) {
        text = resolve(ev.textKey, vars, ev.text || '');
      } else if (key) {
        var tone = ev.tone || 'neutral';
        text = resolve('events.' + key + '.text.' + tone, vars,
          resolve('events.' + key + '.text', vars, ev.text || ''));
      } else {
        text = ev.text || '';
      }
      var options = (ev.options || []).map(function (o, i) {
        var lk = o.labelKey || (key ? 'events.' + key + '.opt' + i + '.label' : null);
        var hk = o.hintKey || (key ? 'events.' + key + '.opt' + i + '.hint' : null);
        return {
          label: lk ? resolve(lk, vars, o.label || '') : (o.label || ''),
          hint: hk ? resolve(hk, vars, o.hint || '') : (o.hint || '')
        };
      });
      return { title: title, text: text, options: options };
    },

    /** Compact language switcher markup */
    langSwitch: function (opts) {
      opts = opts || {};
      var cls = opts.className || 'lang-switch';
      var html = '<div class="' + cls + '" role="group" aria-label="' +
        resolve('common.language', null, 'Idioma') + '">';
      for (var i = 0; i < SUPPORTED.length; i++) {
        var code = SUPPORTED[i];
        var active = code === lang ? ' active' : '';
        html += '<button type="button" class="lang-btn' + active +
          '" data-action="set-lang" data-value="' + code + '" aria-pressed="' +
          (code === lang ? 'true' : 'false') + '">' +
          code.toUpperCase() + '</button>';
        if (i < SUPPORTED.length - 1) html += '<span class="lang-sep" aria-hidden="true">|</span>';
      }
      html += '</div>';
      return html;
    },

    /**
     * Bind object field getters to translation keys.
     * Preserves original Spanish as fallback via closure.
     */
    bindFields: function (bag, prefix, fields) {
      if (!bag) return;
      Object.keys(bag).forEach(function (id) {
        var item = bag[id];
        if (!item) return;
        (fields || []).forEach(function (field) {
          if (!Object.prototype.hasOwnProperty.call(item, field)) return;
          var raw = item[field];
          if (typeof raw !== 'string') return;
          try {
            Object.defineProperty(item, field, {
              configurable: true,
              enumerable: true,
              get: function () {
                return resolve(prefix + '.' + id + '.' + field, null, raw);
              }
            });
          } catch (e) { /* ignore non-configurable */ }
        });
      });
    },

    init: function () {
      lang = readStored();
      setDocumentLang(lang);
      return lang;
    }
  };

  DCS.i18n = i18n;
  /** Global translation helper (safe outside UI screens IIFE). */
  DCS.t = function (key, vars, fallback) {
    return i18n.t(key, vars, fallback);
  };
})(window.DCS = window.DCS || {});

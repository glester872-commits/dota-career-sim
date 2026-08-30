#!/usr/bin/env python3
"""Inject heroes catalog + top-3 UI + inbox system into index.html."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
I18N = ROOT / "i18n"
HEROES_JS = (ROOT / "data" / "heroes-catalog.js").read_text(encoding="utf-8")

I18N_ES = {
    "nav": {"inbox": "Bandeja"},
    "heroes": {
        "topThree": "Mejores tres héroes",
        "topThreeSub": "Según tus partidas oficiales: victorias primero, luego porcentaje.",
        "empty": "Todavía no hay suficientes partidas para destacar héroes.",
        "maps": "Partidas",
        "wins": "Victorias",
        "losses": "Derrotas",
        "winrate": "Winrate",
        "noMapsYet": "Sin partidas todavía",
        "portraitAlt": "Retrato de {{name}}",
    },
    "inbox": {
        "title": "Bandeja de entrada",
        "empty": "No tienes mensajes",
        "emptyFilter": "No hay mensajes en este filtro",
        "unread": "No leídos",
        "all": "Todos",
        "offers": "Ofertas",
        "tournaments": "Torneos",
        "team": "Equipo",
        "system": "Sistema",
        "markRead": "Marcar leído",
        "markUnread": "Marcar no leído",
        "delete": "Eliminar",
        "open": "Abrir",
        "back": "Volver",
        "resolved": "Resuelto",
        "expired": "Expirado",
        "expires": "Caduca",
        "from": "De",
        "confirmAction": "¿Confirmas esta acción?",
        "actionDone": "Acción completada",
        "alreadyResolved": "Esta decisión ya está resuelta",
        "negotiate": "Negociar",
        "viewTournament": "Ver torneo",
        "viewResults": "Ver resultados",
        "viewOffers": "Ver ofertas",
        "hintAcceptOffer": "Firmar y unirte a este equipo.",
        "hintRejectOffer": "Descartar esta oferta.",
        "hintViewOffers": "Ver el mercado completo.",
        "cat": {
            "offers": "Ofertas",
            "tournaments": "Torneos",
            "team": "Equipo",
            "system": "Sistema",
            "career": "Carrera",
        },
        "fromSystem": "Sistema",
        "fromOrg": "Organización",
        "fromCoach": "Entrenador",
        "fromMarket": "Mercado",
        "fromCircuit": "Circuito",
        "offerSubject": "Oferta de {{team}}",
        "offerSummary": "{{tier}} · {{salary}} · {{years}}",
        "offerBody": "{{team}} te ofrece un contrato. Revisa las condiciones antes de decidir.",
        "offerAccepted": "Has firmado con {{team}}.",
        "offerRejected": "Has rechazado a {{team}}.",
        "eventSubject": "{{title}}",
        "eventSummary": "Decisión pendiente",
        "tourSubject": "{{name}} — {{result}}",
        "tourSummary": "{{place}} · {{prize}}",
        "tourBody": "Resumen de {{name}}. Resultado: {{result}}.",
        "contractEndSubject": "Fin de contrato",
        "contractEndBody": "Tu contrato ha llegado a su fin. El mercado se abre de nuevo.",
        "freeAgentSubject": "Agente libre",
        "freeAgentBody": "Quedas libre. Busca ofertas en el mercado.",
        "yearSubject": "Cierre de {{year}}",
        "yearBody": "El año competitivo termina. Revisa tu patrimonio y prepárate para el siguiente ciclo.",
    },
}

I18N_EN = {
    "nav": {"inbox": "Inbox"},
    "heroes": {
        "topThree": "Top three heroes",
        "topThreeSub": "Based on your official matches: wins first, then win rate.",
        "empty": "Not enough matches yet to highlight heroes.",
        "maps": "Matches",
        "wins": "Wins",
        "losses": "Losses",
        "winrate": "Win rate",
        "noMapsYet": "No matches yet",
        "portraitAlt": "Portrait of {{name}}",
    },
    "inbox": {
        "title": "Inbox",
        "empty": "You have no messages",
        "emptyFilter": "No messages in this filter",
        "unread": "Unread",
        "all": "All",
        "offers": "Offers",
        "tournaments": "Tournaments",
        "team": "Team",
        "system": "System",
        "markRead": "Mark read",
        "markUnread": "Mark unread",
        "delete": "Delete",
        "open": "Open",
        "back": "Back",
        "resolved": "Resolved",
        "expired": "Expired",
        "expires": "Expires",
        "from": "From",
        "confirmAction": "Confirm this action?",
        "actionDone": "Action completed",
        "alreadyResolved": "This decision is already resolved",
        "negotiate": "Negotiate",
        "viewTournament": "View tournament",
        "viewResults": "View results",
        "viewOffers": "View offers",
        "hintAcceptOffer": "Sign and join this team.",
        "hintRejectOffer": "Turn this offer down.",
        "hintViewOffers": "Open the full transfer market.",
        "cat": {
            "offers": "Offers",
            "tournaments": "Tournaments",
            "team": "Team",
            "system": "System",
            "career": "Career",
        },
        "fromSystem": "System",
        "fromOrg": "Organization",
        "fromCoach": "Coach",
        "fromMarket": "Market",
        "fromCircuit": "Circuit",
        "offerSubject": "Offer from {{team}}",
        "offerSummary": "{{tier}} · {{salary}} · {{years}}",
        "offerBody": "{{team}} is offering you a contract. Review the terms before you decide.",
        "offerAccepted": "You signed with {{team}}.",
        "offerRejected": "You rejected {{team}}.",
        "eventSubject": "{{title}}",
        "eventSummary": "Decision pending",
        "tourSubject": "{{name}} — {{result}}",
        "tourSummary": "{{place}} · {{prize}}",
        "tourBody": "Summary of {{name}}. Result: {{result}}.",
        "contractEndSubject": "Contract ended",
        "contractEndBody": "Your contract has ended. The market opens again.",
        "freeAgentSubject": "Free agent",
        "freeAgentBody": "You are free. Look for offers on the market.",
        "yearSubject": "End of {{year}}",
        "yearBody": "The competitive year is over. Review your wealth and prepare for the next cycle.",
    },
}


def deep_merge(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst


def load_cat(path: Path) -> dict:
    s = path.read_text(encoding="utf-8")
    i, j = s.index("{"), s.rindex("}")
    return json.loads(
        subprocess.check_output(
            ["node", "-e", f"process.stdout.write(JSON.stringify({s[i:j+1]}))"],
            text=True,
        )
    )


def write_cat(path: Path, code: str, data: dict) -> None:
    path.write_text(
        f'DCS.i18n.register("{code}", {json.dumps(data, ensure_ascii=False, separators=(",", ":"))});\n',
        encoding="utf-8",
    )


def once(html: str, label: str, old: str, new: str) -> str:
    if old not in html:
        print("SKIP", label)
        return html
    print("OK", label)
    return html.replace(old, new, 1)


INBOX_MODULE = r"""
<script>
/* ============================================================
   ENGINE / INBOX — bandeja de mensajes persistente
   ============================================================ */
(function (DCS) {
  'use strict';

  function t(key, vars, fb) {
    return DCS.t ? DCS.t(key, vars || null, fb || '') : (fb || key);
  }

  function ensure(state) {
    if (!state.inbox) state.inbox = [];
    if (!state.counters) state.counters = {};
    if (typeof state.counters.inbox !== 'number') state.counters.inbox = 1;
    return state.inbox;
  }

  function unreadCount(state) {
    return ensure(state).filter(function (m) { return m && !m.read && !m.deleted; }).length;
  }

  function findByDedupe(state, key) {
    if (!key) return null;
    var list = ensure(state);
    for (var i = 0; i < list.length; i++) {
      if (list[i] && list[i].dedupeKey === key && !list[i].deleted) return list[i];
    }
    return null;
  }

  function push(state, msg) {
    if (!state || !msg) return null;
    ensure(state);
    if (msg.dedupeKey && findByDedupe(state, msg.dedupeKey)) return findByDedupe(state, msg.dedupeKey);
    var id = msg.id || ('m' + (state.counters.inbox++));
    var row = {
      id: id,
      dedupeKey: msg.dedupeKey || null,
      category: msg.category || 'system',
      fromKey: msg.fromKey || 'inbox.fromSystem',
      fromName: msg.fromName || null,
      subjectKey: msg.subjectKey || null,
      subject: msg.subject || '',
      subjectVars: msg.subjectVars || {},
      summaryKey: msg.summaryKey || null,
      summary: msg.summary || '',
      summaryVars: msg.summaryVars || {},
      bodyKey: msg.bodyKey || null,
      body: msg.body || '',
      bodyVars: msg.bodyVars || {},
      createdAt: msg.createdAt || Date.now(),
      year: msg.year != null ? msg.year : state.year,
      read: !!msg.read,
      deleted: false,
      resolved: !!msg.resolved,
      resultKey: msg.resultKey || null,
      result: msg.result || null,
      resultVars: msg.resultVars || {},
      actions: msg.actions || [],
      expiresAt: msg.expiresAt || null,
      meta: msg.meta || {}
    };
    state.inbox.unshift(row);
    if (state.inbox.length > 120) state.inbox = state.inbox.slice(0, 120);
    return row;
  }

  function get(state, id) {
    var list = ensure(state);
    for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i];
    return null;
  }

  function subjectOf(m) {
    if (!m) return '';
    if (m.subjectKey) return t(m.subjectKey, m.subjectVars, m.subject);
    return m.subject || '';
  }
  function summaryOf(m) {
    if (!m) return '';
    if (m.summaryKey) return t(m.summaryKey, m.summaryVars, m.summary);
    return m.summary || '';
  }
  function bodyOf(m) {
    if (!m) return '';
    if (m.bodyKey) return t(m.bodyKey, m.bodyVars, m.body);
    return m.body || '';
  }
  function fromOf(m) {
    if (!m) return '';
    if (m.fromName) return m.fromName;
    return t(m.fromKey || 'inbox.fromSystem', null, 'Sistema');
  }
  function resultOf(m) {
    if (!m) return '';
    if (m.resultKey) return t(m.resultKey, m.resultVars, m.result || '');
    return m.result || '';
  }

  function isExpired(m, now) {
    if (!m || !m.expiresAt) return false;
    return (now || Date.now()) > m.expiresAt;
  }

  function markRead(state, id, read) {
    var m = get(state, id);
    if (!m) return false;
    m.read = read !== false;
    return true;
  }

  function remove(state, id) {
    var m = get(state, id);
    if (!m) return false;
    m.deleted = true;
    return true;
  }

  function resolve(state, id, resultKey, result, resultVars) {
    var m = get(state, id);
    if (!m) return false;
    m.resolved = true;
    m.read = true;
    m.resultKey = resultKey || m.resultKey;
    m.result = result || m.result;
    m.resultVars = resultVars || m.resultVars || {};
    m.actions = [];
    return true;
  }

  function list(state, filter) {
    var now = Date.now();
    return ensure(state).filter(function (m) {
      if (!m || m.deleted) return false;
      if (filter === 'unread') return !m.read;
      if (filter && filter !== 'all') return m.category === filter;
      return true;
    }).map(function (m) {
      if (isExpired(m, now) && m.actions && m.actions.length && !m.resolved) {
        m.resolved = true;
        m.resultKey = m.resultKey || 'inbox.expired';
        m.actions = [];
      }
      return m;
    });
  }

  /* ---- producers ---- */
  function pushOffer(state, offer) {
    if (!offer) return null;
    var salary = (DCS.ui && DCS.ui.fmt) ? DCS.ui.fmt.moneyFull(offer.salary) : String(offer.salary);
    return push(state, {
      dedupeKey: 'offer:' + offer.id,
      category: 'offers',
      fromKey: 'inbox.fromMarket',
      fromName: offer.teamName,
      subjectKey: 'inbox.offerSubject',
      subjectVars: { team: offer.teamName },
      summaryKey: 'inbox.offerSummary',
      summaryVars: {
        tier: 'Tier ' + offer.tier,
        salary: salary,
        years: offer.years + (offer.years === 1 ? 'y' : 'y')
      },
      bodyKey: 'inbox.offerBody',
      bodyVars: { team: offer.teamName },
      expiresAt: offer.expiresAt || null,
      meta: { offerId: offer.id, teamId: offer.teamId },
      actions: [
        { id: 'accept-offer', labelKey: 'common.accept', hintKey: 'inbox.hintAcceptOffer', confirm: true },
        { id: 'reject-offer', labelKey: 'common.reject', hintKey: 'inbox.hintRejectOffer', confirm: true },
        { id: 'view-offers', labelKey: 'inbox.viewOffers', hintKey: 'inbox.hintViewOffers', confirm: false }
      ]
    });
  }

  function pushEvent(state, ev) {
    if (!ev || ev.resolved) return null;
    var view = (DCS.i18n && DCS.i18n.eventView(ev)) || { title: ev.title, text: ev.text };
    var actions = (ev.options || []).map(function (o, i) {
      return { id: 'choose-event', value: i, label: o.label, labelKey: o.labelKey || null, confirm: true };
    });
    return push(state, {
      dedupeKey: 'event:' + ev.id,
      category: 'team',
      fromKey: 'inbox.fromOrg',
      subjectKey: ev.key ? ('events.' + ev.key + '.title') : null,
      subject: view.title,
      summaryKey: 'inbox.eventSummary',
      body: view.text,
      meta: { eventId: ev.id },
      actions: actions
    });
  }

  function pushTournament(state, rec) {
    if (!rec) return null;
    var result = (DCS.i18n && DCS.i18n.result(rec.result)) || rec.result || '';
    var prize = (DCS.ui && DCS.ui.fmt) ? DCS.ui.fmt.money(rec.prize || 0) : String(rec.prize || 0);
    return push(state, {
      dedupeKey: 'tour:' + (rec.id || (rec.name + ':' + state.year)),
      category: 'tournaments',
      fromKey: 'inbox.fromCircuit',
      fromName: rec.name,
      subjectKey: 'inbox.tourSubject',
      subjectVars: { name: rec.name, result: result },
      summaryKey: 'inbox.tourSummary',
      summaryVars: { place: result, prize: prize },
      bodyKey: 'inbox.tourBody',
      bodyVars: { name: rec.name, result: result },
      meta: { tournamentId: rec.id, name: rec.name },
      actions: [
        { id: 'view-tournaments', labelKey: 'inbox.viewResults', confirm: false }
      ],
      resolved: true,
      read: false
    });
  }

  DCS.engine = DCS.engine || {};
  DCS.engine.inbox = {
    ensure: ensure,
    push: push,
    get: get,
    list: list,
    unreadCount: unreadCount,
    markRead: markRead,
    remove: remove,
    resolve: resolve,
    subjectOf: subjectOf,
    summaryOf: summaryOf,
    bodyOf: bodyOf,
    fromOf: fromOf,
    resultOf: resultOf,
    isExpired: isExpired,
    pushOffer: pushOffer,
    pushEvent: pushEvent,
    pushTournament: pushTournament
  };
})(window.DCS = window.DCS || {});
</script>
"""


def main() -> None:
    es, en = load_cat(I18N / "es.js"), load_cat(I18N / "en.js")
    deep_merge(es, I18N_ES)
    deep_merge(en, I18N_EN)
    write_cat(I18N / "es.js", "es", es)
    write_cat(I18N / "en.js", "en", en)
    print("i18n merged")

    html = INDEX.read_text(encoding="utf-8")

    # Inject heroes catalog before ENGINE / MATCH
    if "DCS.engine.heroes" not in html:
        anchor = "/* ============================================================\n   ENGINE / MATCH — simulación de mapas y series"
        if anchor not in html:
            raise SystemExit("match anchor missing")
        html = html.replace(
            "<script>\n" + anchor,
            "<script>\n" + HEROES_JS + "\n</script>\n<script>\n" + anchor,
            1,
        )
        print("OK heroes catalog inject")
    else:
        print("SKIP heroes catalog")

    # Inject inbox module before UI / SCREENS or after center msg
    if "DCS.engine.inbox" not in html:
        anchor = "/* ============================================================\n   UI / SCREENS · INICIO, CREACIÓN, DASHBOARD E INFORMES"
        if anchor not in html:
            # try after center msg script end
            mark = "DCS.ui.centerMsg = centerMsg;\n  DCS.centerMsg = centerMsg;"
            idx = html.find(mark)
            if idx < 0:
                raise SystemExit("inbox inject anchor missing")
            end = html.find("</script>", idx)
            html = html[: end + len("</script>")] + "\n" + INBOX_MODULE + html[end + len("</script>") :]
        else:
            html = html.replace(
                "<script>\n" + anchor,
                INBOX_MODULE + "\n<script>\n" + anchor,
                1,
            )
        print("OK inbox module inject")
    else:
        print("SKIP inbox module")

    # VERSION bump
    html = once(
        html,
        "version-5",
        "var VERSION = 4;",
        "var VERSION = 5;",
    )

    # newState: heroStats + inbox
    html = once(
        html,
        "newState-fields",
        "      offers: [],\n"
        "      history: [],\n"
        "      usedEvents: {},\n"
        "      eventLog: [],\n"
        "      counters: { event: 1, offer: 1 },\n"
        "      career: {\n"
        "        maps: 0, wins: 0, losses: 0,\n",
        "      offers: [],\n"
        "      inbox: [],\n"
        "      history: [],\n"
        "      usedEvents: {},\n"
        "      eventLog: [],\n"
        "      counters: { event: 1, offer: 1, inbox: 1 },\n"
        "      career: {\n"
        "        maps: 0, wins: 0, losses: 0,\n"
        "        heroStats: {},\n",
    )

    # migrate
    html = once(
        html,
        "migrate-v5",
        "    if (!state.eventLog) state.eventLog = [];\n"
        "    if (!state.usedEvents) state.usedEvents = {};\n",
        "    if (!state.eventLog) state.eventLog = [];\n"
        "    if (!state.usedEvents) state.usedEvents = {};\n"
        "    if (!state.inbox) state.inbox = [];\n"
        "    if (!state.counters) state.counters = { event: 1, offer: 1, inbox: 1 };\n"
        "    if (typeof state.counters.inbox !== 'number') state.counters.inbox = 1;\n"
        "    if (state.career && !state.career.heroStats) state.career.heroStats = {};\n"
        "    if (DCS.engine.heroes && DCS.engine.heroes.ensureStats) DCS.engine.heroes.ensureStats(state);\n"
        "    if (DCS.engine.inbox && DCS.engine.inbox.ensure) DCS.engine.inbox.ensure(state);\n",
    )

    # playSeries: pick hero + record
    html = once(
        html,
        "playSeries-heroes",
        "    r.maps.forEach(function (m) { DCS.engine.stats.add(live.acc, m.line, m.win); });",
        "    r.maps.forEach(function (m, mi) {\n"
        "      if (DCS.engine.heroes && DCS.engine.heroes.pickForMap) {\n"
        "        m.heroId = DCS.engine.heroes.pickForMap(state, rng, state.player && state.player.role);\n"
        "        DCS.engine.heroes.record(state, m.heroId, m.win);\n"
        "      }\n"
        "      DCS.engine.stats.add(live.acc, m.line, m.win);\n"
        "    });",
    )
    html = once(
        html,
        "playSeries-maps-hero",
        "      maps: r.maps.map(function (m) {\n"
        "        return { win: m.win, line: m.line };\n"
        "      })",
        "      maps: r.maps.map(function (m) {\n"
        "        return { win: m.win, line: m.line, heroId: m.heroId || null };\n"
        "      })",
    )

    # Profile stats: top 3 heroes
    html = once(
        html,
        "profile-top3",
        """    if (tab === 'stats') {
      if (!state.career.acc || !state.career.acc.maps) {
        return head + c.card({ title: t('ui.noData', null, 'Sin datos'), body: c.empty(t('profile.noOfficialMaps')) });
      }
      return head +
        c.card({
          title: t('ui.careerAverages', { role: role.name }, 'Promedios · ' + role.name), meta: state.career.maps + ' ' + t('ui.maps', null, 'mapas'),
          body: c.statGrid(p.role, careerAvg)
        }) +
        c.card({
          title: t('profile.vsBenchmark'),
          subtitle: 'Dónde caen tus números entre un jugador flojo y uno de élite en ' + role.name + '.',
          body: c.statBars(p.role, careerAvg), delay: 60
        });
    }""",
        """    if (tab === 'stats') {
      if (!state.career.acc || !state.career.acc.maps) {
        return head + c.card({ title: t('ui.noData', null, 'Sin datos'), body: c.empty(t('profile.noOfficialMaps')) }) +
          S.topHeroesCard(state);
      }
      return head +
        c.card({
          title: t('ui.careerAverages', { role: role.name }, 'Promedios · ' + role.name), meta: state.career.maps + ' ' + t('ui.maps', null, 'mapas'),
          body: c.statGrid(p.role, careerAvg)
        }) +
        c.card({
          title: t('profile.vsBenchmark'),
          subtitle: 'Dónde caen tus números entre un jugador flojo y uno de élite en ' + role.name + '.',
          body: c.statBars(p.role, careerAvg), delay: 60
        }) +
        S.topHeroesCard(state);
    }""",
    )

    # Insert topHeroesCard + inbox screen before S.team or after S.profile
    top_heroes_fn = r"""
  S.topHeroesCard = function (state) {
    var top = (DCS.engine.heroes && DCS.engine.heroes.topThree)
      ? DCS.engine.heroes.topThree(state) : [];
    if (!top.length) {
      return c.card({
        title: t('heroes.topThree'),
        subtitle: t('heroes.topThreeSub'),
        body: c.empty(t('heroes.empty')),
        delay: 90
      });
    }
    var rows = top.map(function (h) {
      var hero = DCS.engine.heroes.get(h.id);
      var name = hero ? hero.localized_name : ('#' + h.id);
      var src = hero ? DCS.engine.heroes.portraitUrl(hero) : '';
      var wr = Math.round(h.winrate * 1000) / 10;
      return '<div class="hero-top-row">' +
        '<img class="hero-portrait" src="' + c.esc(src) + '" alt="' +
        c.esc(t('heroes.portraitAlt', { name: name }, name)) +
        '" width="64" height="36" loading="lazy" decoding="async">' +
        '<div class="hero-top-main"><div class="hero-top-name">' + c.esc(name) + '</div>' +
        '<div class="hero-top-meta">' + t('heroes.maps') + ' ' + h.maps +
        ' · ' + t('heroes.wins') + ' ' + h.wins +
        ' · ' + t('heroes.losses') + ' ' + h.losses +
        ' · ' + t('heroes.winrate') + ' ' + wr + '%</div></div></div>';
    }).join('');
    return c.card({
      title: t('heroes.topThree'),
      subtitle: t('heroes.topThreeSub'),
      body: '<div class="hero-top-list">' + rows + '</div>',
      delay: 90
    });
  };

"""

    if "S.topHeroesCard" not in html:
        html = once(
            html,
            "insert-topHeroesCard",
            "  /* ---------------------------------------------------------\n     EQUIPO\n     --------------------------------------------------------- */\n  S.team = function (state) {",
            top_heroes_fn
            + "  /* ---------------------------------------------------------\n     EQUIPO\n     --------------------------------------------------------- */\n  S.team = function (state) {",
        )

    # NAV inbox
    html = once(
        html,
        "nav-inbox",
        "var NAV_IDS = ['dashboard', 'profile', 'team', 'season', 'tournaments', 'finances', 'offers', 'career', 'legacy'];",
        "var NAV_IDS = ['dashboard', 'profile', 'team', 'season', 'tournaments', 'finances', 'offers', 'inbox', 'career', 'legacy'];",
    )

    # shell case inbox + badge
    html = once(
        html,
        "shell-case-inbox",
        "      case 'offers': return S.offers(state);\n"
        "      case 'career': return S.career(state, app.tab.career);",
        "      case 'offers': return S.offers(state);\n"
        "      case 'inbox': return S.inbox(state, app.tab.inbox || 'all', app.openMail);\n"
        "      case 'career': return S.career(state, app.tab.career);",
    )

    # nav badge for unread - find offers badge pattern
    html = once(
        html,
        "nav-badge-inbox",
        "          if (n.id === 'offers' && state.offers && state.offers.length) {\n"
        "            badge = ' <span class=\"badge badge-gold\">' + state.offers.length + '</span>';\n"
        "          }",
        "          if (n.id === 'offers' && state.offers && state.offers.length) {\n"
        "            badge = ' <span class=\"badge badge-gold\">' + state.offers.length + '</span>';\n"
        "          }\n"
        "          if (n.id === 'inbox' && DCS.engine.inbox) {\n"
        "            var ur = DCS.engine.inbox.unreadCount(state);\n"
        "            if (ur) badge = ' <span class=\"badge badge-gold\">' + ur + '</span>';\n"
        "          }",
    )

    # app.tab.inbox + openMail
    html = once(
        html,
        "app-tab-inbox",
        "    tab: { profile: 'attrs', season: 'summary', career: 'timeline' },",
        "    tab: { profile: 'attrs', season: 'summary', career: 'timeline', inbox: 'all' },\n"
        "    openMail: null,",
    )

    # S.inbox screen - insert before S.offers or after S.finances
    inbox_screen = r"""
  /* ---------------------------------------------------------
     BANDEJA DE ENTRADA
     --------------------------------------------------------- */
  S.inbox = function (state, filter, openId) {
    filter = filter || 'all';
    var IB = DCS.engine.inbox;
    if (!IB) return c.empty('Inbox unavailable');
    var list = IB.list(state, filter);
    var filters = [
      { id: 'all', label: t('inbox.all') },
      { id: 'unread', label: t('inbox.unread') },
      { id: 'offers', label: t('inbox.offers') },
      { id: 'tournaments', label: t('inbox.tournaments') },
      { id: 'team', label: t('inbox.team') },
      { id: 'system', label: t('inbox.system') }
    ];
    var head = '<div class="page-head"><div><h2>' + t('inbox.title') + '</h2>' +
      '<div class="sub">' + IB.unreadCount(state) + ' ' + t('inbox.unread').toLowerCase() + '</div></div></div>' +
      c.tabs(filters, filter, 'tab-inbox');

    if (openId) {
      var mail = IB.get(state, openId);
      if (!mail || mail.deleted) {
        return head + c.empty(t('inbox.empty'));
      }
      if (!mail.read) IB.markRead(state, openId, true);
      var when = new Date(mail.createdAt);
      var whenStr = isNaN(when.getTime()) ? '' :
        when.toLocaleString(DCS.i18n && DCS.i18n.getLang() === 'en' ? 'en-US' : 'es-ES');
      var actions = '';
      if (!mail.resolved && mail.actions && mail.actions.length && !IB.isExpired(mail)) {
        actions = '<div class="mail-decision">' +
          '<div class="modal-kicker">' + t('modal.decision', null, 'Decisión') + '</div>' +
          '<div class="choices">' + mail.actions.map(function (a, ai) {
          var label = a.labelKey ? t(a.labelKey, null, a.label || '') : (a.label || '');
          var hint = '';
          if (a.hintKey) hint = t(a.hintKey, a.hintVars || null, a.hint || '');
          else if (a.hint) hint = a.hint;
          return '<button type="button" class="choice" data-action="inbox-action" data-value="' +
            c.esc(mail.id + '|' + ai) + '"><b>' + c.esc(label) + '</b>' +
            (hint ? '<span>' + c.esc(hint) + '</span>' : '') + '</button>';
        }).join('') + '</div></div>';
      }
      var result = mail.resolved
        ? '<p class="mail-result"><b>' + t('inbox.resolved') + ':</b> ' + c.esc(IB.resultOf(mail) || '—') + '</p>'
        : (IB.isExpired(mail) ? '<p class="mail-result muted">' + t('inbox.expired') + '</p>' : '');
      return head +
        c.card({
          title: IB.subjectOf(mail),
          meta: c.badge(t('inbox.cat.' + (mail.category || 'system'), null, mail.category), mail.read ? 'info' : 'gold'),
          body:
            '<div class="kv"><span>' + t('inbox.from') + '</span><span>' + c.esc(IB.fromOf(mail)) + '</span></div>' +
            '<div class="kv"><span>Date</span><span>' + c.esc(whenStr) + '</span></div>' +
            (mail.expiresAt ? '<div class="kv"><span>' + t('inbox.expires') + '</span><span>' +
              c.esc(new Date(mail.expiresAt).toLocaleString()) + '</span></div>' : '') +
            '<p class="mt">' + c.esc(IB.bodyOf(mail)) + '</p>' +
            result + actions +
            '<div class="row mt">' +
            c.btn(t('inbox.back'), 'inbox-close', { variant: 'ghost' }) +
            c.btn(mail.read ? t('inbox.markUnread') : t('inbox.markRead'), 'inbox-toggle-read', { value: mail.id, variant: 'ghost' }) +
            c.btn(t('inbox.delete'), 'inbox-delete', { value: mail.id, variant: 'danger' }) +
            '</div>'
        });
    }

    if (!list.length) {
      return head + c.empty(filter === 'all' ? t('inbox.empty') : t('inbox.emptyFilter'));
    }

    var rows = list.map(function (m) {
      return '<button type="button" class="mail-row' + (m.read ? '' : ' unread') +
        '" data-action="inbox-open" data-value="' + c.esc(m.id) + '">' +
        '<span class="mail-dot" aria-hidden="true"></span>' +
        '<span class="mail-main"><span class="mail-from">' + c.esc(IB.fromOf(m)) + '</span>' +
        '<span class="mail-subject">' + c.esc(IB.subjectOf(m)) + '</span>' +
        '<span class="mail-summary">' + c.esc(IB.summaryOf(m)) + '</span></span>' +
        '<span class="mail-side"><span class="mail-cat">' +
        c.esc(t('inbox.cat.' + (m.category || 'system'), null, m.category)) +
        '</span></span></button>';
    }).join('');

    return head + '<div class="mail-list">' + rows + '</div>';
  };

"""

    if "S.inbox = function" not in html:
        # Place before career or after offers
        html = once(
            html,
            "insert-S.inbox",
            "  /* ---------------------------------------------------------\n     CARRERA\n     --------------------------------------------------------- */",
            inbox_screen
            + "  /* ---------------------------------------------------------\n     CARRERA\n     --------------------------------------------------------- */",
        )

    # Handlers for inbox actions - before default in handle
    handlers = r"""
        case 'tab-inbox':
          app.tab.inbox = value || 'all';
          app.openMail = null;
          app.render();
          return;

        case 'inbox-open':
          app.openMail = value;
          if (DCS.engine.inbox) DCS.engine.inbox.markRead(DCS.game.state, value, true);
          DCS.game.persist();
          app.render();
          return;

        case 'inbox-close':
          app.openMail = null;
          app.render();
          return;

        case 'inbox-toggle-read': {
          var mm = DCS.engine.inbox && DCS.engine.inbox.get(DCS.game.state, value);
          if (mm) {
            DCS.engine.inbox.markRead(DCS.game.state, value, !mm.read);
            DCS.game.persist();
          }
          app.render();
          return;
        }

        case 'inbox-delete':
          if (DCS.engine.inbox) DCS.engine.inbox.remove(DCS.game.state, value);
          if (app.openMail === value) app.openMail = null;
          DCS.game.persist();
          app.render();
          return;

        case 'inbox-action': {
          var parts = String(value || '').split('|');
          var mid = parts[0];
          var ai = parseInt(parts[1], 10) || 0;
          var mail = DCS.engine.inbox && DCS.engine.inbox.get(DCS.game.state, mid);
          if (!mail || mail.resolved) {
            app.toast(DCS.t('inbox.alreadyResolved', null, 'Ya resuelto'));
            app.render();
            return;
          }
          if (DCS.engine.inbox.isExpired(mail)) {
            DCS.engine.inbox.resolve(DCS.game.state, mid, 'inbox.expired', null);
            DCS.game.persist();
            app.toast(DCS.t('inbox.expired'));
            app.render();
            return;
          }
          var act = (mail.actions || [])[ai];
          if (!act) return;
          if (act.confirm && !confirm(DCS.t('inbox.confirmAction', null, '¿Confirmas?'))) return;
          var st = DCS.game.state;
          var outMsg = DCS.t('inbox.actionDone');
          if (act.id === 'accept-offer' && mail.meta && mail.meta.offerId) {
            var acc = DCS.game.acceptOffer(mail.meta.offerId);
            if (acc && acc.ok) {
              DCS.engine.inbox.resolve(st, mid, 'inbox.offerAccepted', null, { team: mail.fromName || '' });
              /* resolve sibling offer mails */
              (st.inbox || []).forEach(function (om) {
                if (om && om.category === 'offers' && !om.resolved && om.id !== mid) {
                  DCS.engine.inbox.resolve(st, om.id, 'inbox.offerRejected', null, { team: om.fromName || '' });
                }
              });
              outMsg = DCS.t('inbox.offerAccepted', { team: mail.fromName || '' });
            } else {
              outMsg = (acc && acc.reason) || DCS.t('game.offerGone');
            }
          } else if (act.id === 'reject-offer' && mail.meta && mail.meta.offerId) {
            var rej = DCS.game.rejectOffer(mail.meta.offerId);
            DCS.engine.inbox.resolve(st, mid, 'inbox.offerRejected', null, { team: mail.fromName || '' });
            outMsg = DCS.t('inbox.offerRejected', { team: mail.fromName || '' });
          } else if (act.id === 'choose-event') {
            var evOut = DCS.game.resolveEvent(act.value);
            var outcome = evOut && evOut.outcome;
            if (evOut && evOut.outcomeKey && DCS.t) {
              outcome = DCS.t(evOut.outcomeKey, evOut.vars || {}, outcome || '');
            }
            DCS.engine.inbox.resolve(st, mid, null, outcome || '');
            outMsg = String(outcome || DCS.t('inbox.actionDone')).slice(0, 110);
          } else if (act.id === 'view-offers') {
            app.openMail = null;
            app.go('offers');
            return;
          } else if (act.id === 'view-tournaments') {
            app.openMail = null;
            app.go('tournaments');
            return;
          }
          DCS.game.persist();
          app.toast(outMsg);
          app.render();
          return;
        }

"""

    if "case 'inbox-open':" not in html:
        html = once(
            html,
            "inbox-handlers",
            "        case 'tab-profile':\n"
            "          app.tab.profile = value || 'attrs';\n"
            "          app.render();\n"
            "          return;",
            handlers
            + "        case 'tab-profile':\n"
            "          app.tab.profile = value || 'attrs';\n"
            "          app.render();\n"
            "          return;",
        )

    # Hook: after generateInitialOffers / when offers set - push to inbox
    # Patch game.acceptOffer toast path is fine; add push when offers assigned in market report / ensureFaMarket

    # Absorb tournament → inbox
    # Find absorbLive or where tournament record is finalized
    html = once(
        html,
        "absorb-inbox-tour",
        "    state.season.tournaments.push(record);\n"
        "    if (record.placement === 1 && record.kind !== 'qualifier') state.season.titles++;",
        "    state.season.tournaments.push(record);\n"
        "    if (record.placement === 1 && record.kind !== 'qualifier') state.season.titles++;\n"
        "    if (DCS.engine.inbox && DCS.engine.inbox.pushTournament) DCS.engine.inbox.pushTournament(state, record);",
    )

    # When pending event is set, push inbox
    html = once(
        html,
        "pending-event-inbox",
        "      state.pending = { type: 'event', eventId: pendingEvent.id };\n"
        "      return { type: 'event', blocked: true };",
        "      state.pending = { type: 'event', eventId: pendingEvent.id };\n"
        "      if (DCS.engine.inbox && DCS.engine.inbox.pushEvent) DCS.engine.inbox.pushEvent(state, pendingEvent);\n"
        "      return { type: 'event', blocked: true };",
    )
    # There may be two occurrences
    html = html.replace(
        "      state.pending = { type: 'event', eventId: pendingEvent.id };\n"
        "      return { type: 'event', blocked: true };",
        "      state.pending = { type: 'event', eventId: pendingEvent.id };\n"
        "      if (DCS.engine.inbox && DCS.engine.inbox.pushEvent) DCS.engine.inbox.pushEvent(state, pendingEvent);\n"
        "      return { type: 'event', blocked: true };",
    )
    print("OK pending-event-inbox all")

    # Push offers when generated - find generateInitialOffers return or where offers assigned
    # Safer: wrap in game layer after generateInitialOffers in newState
    html = once(
        html,
        "newState-offer-inbox",
        "    if (DCS.engine.market.generateInitialOffers) {\n"
        "      DCS.engine.market.generateInitialOffers(state, rng);\n"
        "    }",
        "    if (DCS.engine.market.generateInitialOffers) {\n"
        "      DCS.engine.market.generateInitialOffers(state, rng);\n"
        "    }\n"
        "    if (DCS.engine.inbox && state.offers) {\n"
        "      state.offers.forEach(function (o) { DCS.engine.inbox.pushOffer(state, o); });\n"
        "    }",
    )

    # Also when market phase generates offers - search state.offers = offers
    html = once(
        html,
        "market-offers-inbox",
        "    state.offers = offers;\n"
        "    state.season.phase = 'yearEnd';",
        "    state.offers = offers;\n"
        "    if (DCS.engine.inbox && offers) {\n"
        "      offers.forEach(function (o) { DCS.engine.inbox.pushOffer(state, o); });\n"
        "    }\n"
        "    state.season.phase = 'yearEnd';",
    )

    # CSS for heroes + inbox in patch-index later; inject mark for now
    css = """
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
.mail-decision { margin-top: 16px; }
.mail-decision .modal-kicker { margin-bottom: 2px; }
.mail-decision .choices { margin-top: 10px; }
.mail-decision .choice { width: 100%; display: block; }
.mail-result { margin-top: 10px; }
@media (max-width: 720px) {
  .hero-portrait { width: 56px; height: 32px; }
  .mail-row { padding: 10px 12px; }
}
"""
    if "DCS_HEROES_INBOX_CSS" not in html:
        # Append into LANG CSS area via marker before </style> won't survive - add to patch-index
        pass

    # Append CSS to patch-index.js langCss
    patch = (I18N / "patch-index.js").read_text(encoding="utf-8")
    if "DCS_HEROES_INBOX_CSS" not in patch:
        patch = patch.replace(
            "@media (max-width: 720px) {\n  .mate-line .mate-country { display: none; }\n}\n`;",
            "@media (max-width: 720px) {\n  .mate-line .mate-country { display: none; }\n}\n"
            + css
            + "`;",
            1,
        )
        (I18N / "patch-index.js").write_text(patch, encoding="utf-8")
        print("OK patch-index CSS")
    else:
        print("SKIP patch-index CSS")

    INDEX.write_text(html, encoding="utf-8")
    subprocess.check_call(["node", str(I18N / "patch-index.js")], stdout=subprocess.DEVNULL)
    print("done", INDEX.stat().st_size)


if __name__ == "__main__":
    main()

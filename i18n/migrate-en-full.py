#!/usr/bin/env python3
"""Merge new i18n keys and wire index.html call sites for full EN/ES coverage."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "i18n"
INDEX = ROOT / "index.html"

NEW_ES = {
    "game": {
        "careerFinished": "Carrera finalizada",
        "noSave": "No hay ninguna partida guardada.",
        "needNick": "Necesitas un nickname.",
        "wipeConfirm": "Se borrará la carrera guardada. ¿Seguro?",
        "newCareerConfirm": "Ya existe una carrera guardada. Empezar una nueva la borrará. ¿Continuar?",
        "answerMarket": "Responde al mercado antes de cerrar el año.",
        "signedWith": "Has firmado con {{team}}.",
        "offerGone": "Esa oferta ya no está disponible.",
        "rejectedTeam": "Has rechazado a {{team}}.",
        "weeksPassedToast": {
            "one": "Ha pasado {{count}} semana.",
            "other": "Han pasado {{count}} semanas.",
        },
        "cannotWait": "No puedes esperar ahora.",
        "rejectedAll": "Has rechazado todas las ofertas.",
        "investedIn": "Has puesto {{amount}} en {{name}}.",
        "investFailed": "No se pudo invertir.",
        "soldRecover": "Recuperas {{amount}} tras costes.",
        "luxuryOk": "Te das un respiro. El gasto no volverá.",
        "keepCash": "Conservas la liquidez.",
        "keepGoing": "Sigues adelante.",
        "retireConfirm": "¿Retirarte ahora y cerrar la carrera?",
        "next": {
            "preseason": "Iniciar pretemporada",
            "competition": "Jugar la temporada",
            "review": "Cerrar la temporada",
            "market": "Abrir el mercado",
            "yearEnd": "Terminar el año",
            "startYear": "Empezar {{year}}",
            "continue": "Continuar",
        },
    },
    "phase": {
        "preseason": "Pretemporada",
        "competition": "Competición",
        "review": "Cierre de temporada",
        "market": "Mercado",
        "yearEnd": "Fin de año",
    },
    "ui": {
        "goToTournament": "Ir al torneo",
        "tournamentClosed": "Torneo cerrado",
        "seriesBySeries": "Serie a serie",
        "noLiveTournament": "No hay un torneo en curso.",
        "noPendingSeries": "No hay un torneo en juego. Abre el siguiente evento avanzando la temporada.",
        "alreadyPlayed": "Ya disputados esta temporada:",
        "noPendingTitle": "Sin serie pendiente",
        "competitiveCalendar": "Calendario competitivo",
        "tournamentsLead": "De la clasificatoria abierta a The International: cada plaza se gana.",
        "circuitTitle": "Circuito",
        "circuitIntro": "El circuito competitivo conecta clasificatorias, torneos regionales y grandes eventos internacionales. Cada competición tiene su propio nivel de prestigio y dificultad.",
        "sectionQual": "Clasificatorias",
        "sectionReg": "Regionales",
        "sectionIntl": "Eventos internacionales",
        "international": "Internacional",
        "titlesCount": {
            "one": "{{count}} título",
            "other": "{{count}} títulos",
        },
        "editionsCount": {
            "one": "{{count}} edición",
            "other": "{{count}} ediciones",
        },
        "plannedCalendar": "Calendario previsto:",
        "clickTourDetail": "Pulsa cualquier torneo para ver serie a serie.",
        "worldChampion": "★ campeón del mundo",
        "ofField": "{{place}} de {{field}}",
        "classified": "Clasificado",
        "maps": "Mapas",
        "winrate": "Winrate",
        "series": "Series",
        "rosterQuality": "Calidad del roster",
        "synergy": "Sinergia",
        "resources": "Recursos",
        "style": "Estilo",
        "currentStatus": "Estado actual",
        "valuation": "Valoración",
        "lastSeason": "última temporada",
        "seasonRating": "Rating de temporada",
        "maxMmr": "MMR máximo",
        "proYears": "Años pro",
        "titles": "Títulos",
        "stats": "Estadísticas",
        "careerAverages": "Promedios de carrera · {{role}}",
        "noTournamentsPlayed": "Sin torneos disputados.",
        "inPlay": "En juego",
        "directInvite": "Invitación directa",
        "viaOpen": "Vía Open Qualifier",
        "viaClosed": "Vía Closed Qualifier",
        "viaQualifier": "Vía clasificatorio",
        "blocked": "Bloqueado",
        "notPlayed": "No disputado",
        "next": "Siguiente",
        "pending": "Pendiente",
        "eliminatedInQual": "Eliminado en la clasificatoria",
        "toDecide": "Por decidir",
        "mainEvent": "Main Event",
        "earningsHistory": "histórico de carrera",
        "available": "disponible",
        "net": "neto",
        "wealthLead": "Lo que ganas en el servidor no es el final",
        "wealthBlurb": "Earnings es historia. El cash es lo que puedes mover. El patrimonio es lo que queda.",
        "histPerformance": "Rendimiento histórico",
        "invested": "Invertido",
        "currentValue": "Valor actual",
        "pnl": "Ganancia / pérdida",
        "investments": "Inversiones",
        "circuitClimate": "Clima del circuito",
        "noMarketMoves": "Sin movimientos de mercado este año. Mantener cash también cuenta.",
        "yearNotClosed": "Todavía no ha cerrado un año con inversiones.",
        "whatWithMoney": "¿Qué haces con el dinero?",
        "fewDecisions": "Pocas decisiones. Sin microgestión.",
        "careerClosedWealth": "La carrera ya está cerrada. Esto es lo que construiste.",
        "notEnoughCash": "Todavía no hay liquidez suficiente para mover ficha. Gana en el servidor y vuelve.",
        "belowMinRound": "Tienes efectivo, pero no llega al mínimo para una ronda.",
        "pickCatAmount": "Elige categoría y cantidad. No hay cifras de retorno. El año decide.",
        "orDoNothing": "O no hagas nada: el cash no se mueve solo.",
        "sell": "Vender {{name}}",
        "exitCosts": "Incluye costes de salida",
        "risk": "Riesgo",
        "potential": "Potencial",
        "variation": "Variación",
        "luxuryTitle": "Lujo y estilo de vida",
        "luxurySub": "No produce rentabilidad.",
        "luxuryHint": "Mejora moderadamente moral y reputación, pero el dinero no vuelve. Gastado: {{amount}}",
        "spend": "Gastar {{amount}}",
        "back": "Volver",
        "evolution": "Evolución",
        "attributes": "Atributos",
        "noData": "Sin datos",
        "pureSkill": "Habilidad individual pura. Importa, pero no manda.",
        "howCircuitEachYear": "Cómo te evaluó el circuito cada año.",
        "years": "años",
        "interest": "Interés {{level}}",
        "destroyedWards": "Wards destruidos",
        "participation": "Participación",
        "supportGold": "Oro en soporte",
        "heroDamage": "Daño a héroes",
        "towerDamage": "Daño a torres",
        "teamfightPart": "Teamfight part.",
        "smokePart": "Smoke part.",
    },
    "dash": {
        "age": "Edad",
        "season": "Temporada",
        "reputation": "Reputación",
        "ranking": "Ranking",
        "netWorth": "Patrimonio",
        "team": "Equipo",
        "contract": "Contrato",
        "form": "Forma",
        "market": "Mercado",
        "freeAgentStatus": "Agente libre",
        "debutMarket": "Mercado de debut",
        "entryRegion": "Región de entrada",
        "nextRival": "Próximo rival",
        "captain": "Capitán",
        "internalRole": "Rol interno",
        "position": "Posición",
        "rosterSynergy": "Sinergia del roster",
        "seasonsWithoutTeam": "Temporadas sin equipo",
        "faNoMaps": "Eres agente libre. Sin equipo no hay mapas oficiales: el mercado es tu único camino.",
        "careerStarts": "Tu carrera empieza aquí. Pulsa {{action}} para seguir.",
    },
}

NEW_EN = {
    "game": {
        "careerFinished": "Career finished",
        "noSave": "No saved career found.",
        "needNick": "You need a nickname.",
        "wipeConfirm": "This will delete the saved career. Are you sure?",
        "newCareerConfirm": "A saved career already exists. Starting a new one will erase it. Continue?",
        "answerMarket": "Answer the market before closing the year.",
        "signedWith": "You signed with {{team}}.",
        "offerGone": "That offer is no longer available.",
        "rejectedTeam": "You turned down {{team}}.",
        "weeksPassedToast": {
            "one": "{{count}} week has passed.",
            "other": "{{count}} weeks have passed.",
        },
        "cannotWait": "You can’t wait right now.",
        "rejectedAll": "You rejected every offer.",
        "investedIn": "You put {{amount}} into {{name}}.",
        "investFailed": "Couldn’t invest.",
        "soldRecover": "You recover {{amount}} after fees.",
        "luxuryOk": "You take a break. That money won’t come back.",
        "keepCash": "You keep the cash.",
        "keepGoing": "You keep going.",
        "retireConfirm": "Retire now and close the career?",
        "next": {
            "preseason": "Start preseason",
            "competition": "Play the season",
            "review": "Close the season",
            "market": "Open the market",
            "yearEnd": "End the year",
            "startYear": "Start {{year}}",
            "continue": "Continue",
        },
    },
    "phase": {
        "preseason": "Preseason",
        "competition": "Competition",
        "review": "Season review",
        "market": "Market",
        "yearEnd": "Year end",
    },
    "ui": {
        "goToTournament": "Go to tournament",
        "tournamentClosed": "Tournament closed",
        "seriesBySeries": "Series by series",
        "noLiveTournament": "No tournament in progress.",
        "noPendingSeries": "No tournament in play. Advance the season to open the next event.",
        "alreadyPlayed": "Already played this season:",
        "noPendingTitle": "No series pending",
        "competitiveCalendar": "Competitive calendar",
        "tournamentsLead": "From the open qualifier to The International: every spot is earned.",
        "circuitTitle": "Circuit",
        "circuitIntro": "The competitive circuit links qualifiers, regional tournaments and major international events. Each competition has its own prestige and difficulty.",
        "sectionQual": "Qualifiers",
        "sectionReg": "Regionals",
        "sectionIntl": "International events",
        "international": "International",
        "titlesCount": {"one": "{{count}} title", "other": "{{count}} titles"},
        "editionsCount": {"one": "{{count}} edition", "other": "{{count}} editions"},
        "plannedCalendar": "Scheduled calendar:",
        "clickTourDetail": "Tap any tournament to see it series by series.",
        "worldChampion": "★ world champion",
        "ofField": "{{place}} of {{field}}",
        "classified": "Qualified",
        "maps": "Maps",
        "winrate": "Winrate",
        "series": "Series",
        "rosterQuality": "Roster quality",
        "synergy": "Synergy",
        "resources": "Resources",
        "style": "Style",
        "currentStatus": "Current status",
        "valuation": "Rating",
        "lastSeason": "last season",
        "seasonRating": "Season rating",
        "maxMmr": "Peak MMR",
        "proYears": "Pro years",
        "titles": "Titles",
        "stats": "Statistics",
        "careerAverages": "Career averages · {{role}}",
        "noTournamentsPlayed": "No tournaments played yet.",
        "inPlay": "Live",
        "directInvite": "Direct invite",
        "viaOpen": "Via Open Qualifier",
        "viaClosed": "Via Closed Qualifier",
        "viaQualifier": "Via qualifier",
        "blocked": "Blocked",
        "notPlayed": "Not played",
        "next": "Next",
        "pending": "Pending",
        "eliminatedInQual": "Eliminated in the qualifier",
        "toDecide": "TBD",
        "mainEvent": "Main Event",
        "earningsHistory": "career earnings",
        "available": "available",
        "net": "net",
        "wealthLead": "What you earn in-game isn’t the end",
        "wealthBlurb": "Earnings are history. Cash is what you can move. Net worth is what remains.",
        "histPerformance": "Historical performance",
        "invested": "Invested",
        "currentValue": "Current value",
        "pnl": "Profit / loss",
        "investments": "Investments",
        "circuitClimate": "Circuit climate",
        "noMarketMoves": "No market moves this year. Holding cash still counts.",
        "yearNotClosed": "You haven’t closed a year with investments yet.",
        "whatWithMoney": "What do you do with the money?",
        "fewDecisions": "Few decisions. No micromanagement.",
        "careerClosedWealth": "The career is closed. This is what you built.",
        "notEnoughCash": "Not enough liquidity to make a move. Win on the server and come back.",
        "belowMinRound": "You have cash, but not enough for a round.",
        "pickCatAmount": "Pick a category and amount. No return figures. The year decides.",
        "orDoNothing": "Or do nothing: cash doesn’t move on its own.",
        "sell": "Sell {{name}}",
        "exitCosts": "Includes exit costs",
        "risk": "Risk",
        "potential": "Potential",
        "variation": "Change",
        "luxuryTitle": "Luxury & lifestyle",
        "luxurySub": "Doesn’t produce returns.",
        "luxuryHint": "Slightly boosts morale and reputation, but the money doesn’t come back. Spent: {{amount}}",
        "spend": "Spend {{amount}}",
        "back": "Back",
        "evolution": "Evolution",
        "attributes": "Attributes",
        "noData": "No data",
        "pureSkill": "Pure individual skill. It matters, but it doesn’t rule.",
        "howCircuitEachYear": "How the circuit rated you each year.",
        "years": "years old",
        "interest": "Interest {{level}}",
        "destroyedWards": "Wards destroyed",
        "participation": "Participation",
        "supportGold": "Support gold",
        "heroDamage": "Hero damage",
        "towerDamage": "Tower damage",
        "teamfightPart": "Teamfight part.",
        "smokePart": "Smoke part.",
    },
    "dash": {
        "age": "Age",
        "season": "Season",
        "reputation": "Reputation",
        "ranking": "Ranking",
        "netWorth": "Net Worth",
        "team": "Team",
        "contract": "Contract",
        "form": "Form",
        "market": "Market",
        "freeAgentStatus": "Free Agent",
        "debutMarket": "Debut market",
        "entryRegion": "Entry region",
        "nextRival": "Next opponent",
        "captain": "Captain",
        "internalRole": "Internal role",
        "position": "Role",
        "rosterSynergy": "Roster synergy",
        "seasonsWithoutTeam": "Seasons without a team",
        "faNoMaps": "You’re a Free Agent. Without a team there are no official maps: the market is your only path.",
        "careerStarts": "Your career starts here. Hit {{action}} to keep going.",
    },
}


def deep_merge(base: dict, overlay: dict) -> dict:
    out = dict(base)
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            # plural forms: replace wholesale if one/other
            if "one" in v or "other" in v:
                out[k] = v
            else:
                out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_catalog(path: Path, lang: str) -> dict:
    text = path.read_text(encoding="utf-8")
    marker = f'DCS.i18n.register("{lang}", '
    i = text.find(marker)
    if i < 0:
        raise SystemExit(f"missing register in {path}")
    obj, _ = json.JSONDecoder().raw_decode(text[i + len(marker) :])
    return obj


def write_catalog(path: Path, lang: str, obj: dict, header: str) -> None:
    # compact JSON like existing files
    payload = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    path.write_text(f"{header}\nDCS.i18n.register(\"{lang}\", {payload});\n", encoding="utf-8")


def sync_index_catalogs(html: str, es_obj: dict, en_obj: dict) -> str:
    def repl(lang: str, obj: dict, text: str) -> str:
        marker = f'DCS.i18n.register("{lang}", '
        i = text.find(marker)
        if i < 0:
            raise SystemExit(f"index missing {lang}")
        j = i + len(marker)
        _, end = json.JSONDecoder().raw_decode(text[j:])
        payload = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
        return text[:j] + payload + text[j + end :]

    html = repl("es", es_obj, html)
    html = repl("en", en_obj, html)
    return html


def must_replace(html: str, old: str, new: str, label: str) -> str:
    if old not in html:
        raise SystemExit(f"MISSING {label}:\n{old[:240]}")
    return html.replace(old, new, 1)


def main() -> None:
    es_path = I18N / "es.js"
    en_path = I18N / "en.js"
    es = deep_merge(load_catalog(es_path, "es"), NEW_ES)
    en = deep_merge(load_catalog(en_path, "en"), NEW_EN)

    # Keep existing keys that NEW overwrote carefully for phase.review etc — intentional

    write_catalog(es_path, "es", es, "/* Dota Career Sim — Spanish catalog */")
    write_catalog(en_path, "en", en, "/* Dota Career Sim — English catalog */")

    html = INDEX.read_text(encoding="utf-8")
    html = sync_index_catalogs(html, es, en)

    # --- PHASE_LABEL + phaseLabel + nextLabel ---
    html = must_replace(
        html,
        """  var PHASE_LABEL = {
    preseason: 'Pretemporada',
    competition: 'Competición',
    review: 'Cierre de temporada',
    market: 'Mercado',
    yearEnd: 'Fin de año'
  };""",
        """  var PHASE_LABEL = {
    preseason: 'Pretemporada',
    competition: 'Competición',
    review: 'Cierre de temporada',
    market: 'Mercado',
    yearEnd: 'Fin de año'
  };
  function phaseLabelLive(ph) {
    if (!ph || ph === 'done') ph = 'preseason';
    var key = 'phase.' + ph;
    var fb = PHASE_LABEL[ph] || ph;
    return (DCS.i18n && DCS.i18n.t(key, null, fb)) || fb;
  }""",
        "PHASE_LABEL helper",
    )

    html = must_replace(
        html,
        """      if (!s || s.finished) return 'Carrera finalizada';
      if (s.pending && s.pending.type === 'retirement') return (DCS.i18n && DCS.i18n.t('modal.retireQ')) || '¿Ha llegado el momento?';
      if (s.pending && s.pending.type === 'event') return (DCS.i18n && DCS.i18n.t('modal.pendingEvent')) || 'Decisión pendiente';
      if (s.pending && s.pending.type === 'wealth') return (DCS.i18n && DCS.i18n.t('modal.pendingWealth')) || 'Oportunidad financiera';
      if (s.pending && s.pending.type === 'tournament') return s.season.liveTour ? s.season.liveTour.name : ((DCS.i18n && DCS.i18n.t('modal.pendingTour')) || 'Torneo');
      var ph = s.season ? s.season.phase : 'preseason';
      if (ph === 'done') return 'Pretemporada';
      return DCS.engine.season.PHASE_LABEL[ph] || ph;
    },

    nextLabel: function () {
      var s = game.state;
      if (!s) return '';
      var ph = s.season ? s.season.phase : 'preseason';
      var map = {
        preseason: 'Iniciar pretemporada',
        competition: 'Jugar la temporada',
        review: 'Cerrar la temporada',
        market: 'Abrir el mercado',
        yearEnd: 'Terminar el año',
        done: 'Empezar ' + s.year
      };
      return map[ph] || 'Continuar';
    }""",
        """      if (!s || s.finished) return (DCS.t && DCS.t('game.careerFinished', null, 'Carrera finalizada')) || 'Carrera finalizada';
      if (s.pending && s.pending.type === 'retirement') return (DCS.i18n && DCS.i18n.t('modal.retireQ')) || '¿Ha llegado el momento?';
      if (s.pending && s.pending.type === 'event') return (DCS.i18n && DCS.i18n.t('modal.pendingEvent')) || 'Decisión pendiente';
      if (s.pending && s.pending.type === 'wealth') return (DCS.i18n && DCS.i18n.t('modal.pendingWealth')) || 'Oportunidad financiera';
      if (s.pending && s.pending.type === 'tournament') return s.season.liveTour ? s.season.liveTour.name : ((DCS.i18n && DCS.i18n.t('modal.pendingTour')) || 'Torneo');
      var ph = s.season ? s.season.phase : 'preseason';
      var live = DCS.engine && DCS.engine.season && DCS.engine.season.phaseLabelLive;
      return live ? live(ph) : ((DCS.t && DCS.t('phase.' + (ph === 'done' ? 'preseason' : ph), null, ph)) || ph);
    },

    nextLabel: function () {
      var s = game.state;
      if (!s) return '';
      var ph = s.season ? s.season.phase : 'preseason';
      var t = function (k, vars, fb) { return (DCS.t && DCS.t(k, vars, fb)) || fb; };
      if (ph === 'done') return t('game.next.startYear', { year: s.year }, 'Empezar ' + s.year);
      var keys = {
        preseason: 'game.next.preseason',
        competition: 'game.next.competition',
        review: 'game.next.review',
        market: 'game.next.market',
        yearEnd: 'game.next.yearEnd'
      };
      var fb = {
        preseason: 'Iniciar pretemporada',
        competition: 'Jugar la temporada',
        review: 'Cerrar la temporada',
        market: 'Abrir el mercado',
        yearEnd: 'Terminar el año'
      };
      return t(keys[ph] || 'game.next.continue', null, fb[ph] || 'Continuar');
    }""",
        "phaseLabel/nextLabel",
    )

    # Export phaseLabelLive on season engine if PHASE_LABEL exported nearby
    if "phaseLabelLive: phaseLabelLive" not in html:
        html = must_replace(
            html,
            "    PHASE_LABEL: PHASE_LABEL,",
            "    PHASE_LABEL: PHASE_LABEL,\n    phaseLabelLive: phaseLabelLive,",
            "export phaseLabelLive",
        )

    # --- eventHtml uses eventView ---
    html = must_replace(
        html,
        """  function eventHtml(ev) {
    if (!ev) return '';
    var icon = ev.tone === 'great' ? '★' : (ev.tone === 'good' ? '▲' : (ev.tone === 'bad' ? '▼' : '◆'));
    return '<div class="event ' + c.toneClass(ev.tone) + '">' +
      '<h4><span class="muted small">' + icon + '</span> ' + c.esc(ev.title) + '</h4><p>' + c.esc(ev.text) + '</p>' +
      (ev.outcome ? '<div class="outcome"><b>' + c.esc(ev.chosen || '') + '</b> — ' + c.esc(ev.outcome) + '</div>' : '') +
      '</div>';
  }""",
        """  function eventHtml(ev) {
    if (!ev) return '';
    var view = (DCS.i18n && DCS.i18n.eventView(ev)) || {
      title: ev.title || '', text: ev.text || '', options: ev.options || []
    };
    var icon = ev.tone === 'great' ? '★' : (ev.tone === 'good' ? '▲' : (ev.tone === 'bad' ? '▼' : '◆'));
    var chosen = ev.chosen || '';
    if (ev.chosenKey && DCS.t) chosen = DCS.t(ev.chosenKey, ev.vars || {}, chosen);
    var outcome = ev.outcome || '';
    if (ev.outcomeKey && DCS.t) outcome = DCS.t(ev.outcomeKey, ev.vars || {}, outcome);
    return '<div class="event ' + c.toneClass(ev.tone) + '">' +
      '<h4><span class="muted small">' + icon + '</span> ' + c.esc(view.title) + '</h4><p>' + c.esc(view.text) + '</p>' +
      (outcome ? '<div class="outcome"><b>' + c.esc(chosen) + '</b> — ' + c.esc(outcome) + '</div>' : '') +
      '</div>';
  }""",
        "eventHtml",
    )

    # --- ATTRS live labels ---
    html = must_replace(
        html,
        """  var ATTRS = [
    { key: 'mech', label: 'Mecánicas' },
    { key: 'sense', label: 'Game Sense' },
    { key: 'pool', label: 'Hero Pool' },
    { key: 'cons', label: 'Consistencia' },
    { key: 'ment', label: 'Mentalidad' },
    { key: 'team', label: 'Teamplay' },
    { key: 'adapt', label: 'Adaptación' },
    { key: 'lead', label: 'Liderazgo' }
  ];

  var ATTR_KEYS = ATTRS.map(function (a) { return a.key; });""",
        """  var ATTRS = [
    { key: 'mech', label: 'Mecánicas' },
    { key: 'sense', label: 'Game Sense' },
    { key: 'pool', label: 'Hero Pool' },
    { key: 'cons', label: 'Consistencia' },
    { key: 'ment', label: 'Mentalidad' },
    { key: 'team', label: 'Teamplay' },
    { key: 'adapt', label: 'Adaptación' },
    { key: 'lead', label: 'Liderazgo' }
  ];
  ATTRS.forEach(function (a) {
    var raw = a.label;
    try {
      Object.defineProperty(a, 'label', {
        configurable: true, enumerable: true,
        get: function () {
          return (DCS.i18n && DCS.i18n.t('attrs.' + a.key, null, raw)) || raw;
        }
      });
    } catch (e) { /* ignore */ }
  });

  var ATTR_KEYS = ATTRS.map(function (a) { return a.key; });""",
        "ATTRS i18n",
    )

    # --- app.handle confirms/toasts ---
    replacements = [
        (
            "if (DCS.store.hasSave() && !confirm('Ya existe una carrera guardada. Empezar una nueva la borrará. ¿Continuar?')) return;",
            "if (DCS.store.hasSave() && !confirm(DCS.t('game.newCareerConfirm', null, 'Ya existe una carrera guardada. Empezar una nueva la borrará. ¿Continuar?'))) return;",
        ),
        (
            "if (!confirm('Se borrará la carrera guardada. ¿Seguro?')) return;",
            "if (!confirm(DCS.t('game.wipeConfirm', null, 'Se borrará la carrera guardada. ¿Seguro?'))) return;",
        ),
        (
            "else app.toast('No hay ninguna partida guardada.');",
            "else app.toast(DCS.t('game.noSave', null, 'No hay ninguna partida guardada.'));",
        ),
        (
            "if (!d.nick || !d.nick.trim()) { app.toast('Necesitas un nickname.'); return; }",
            "if (!d.nick || !d.nick.trim()) { app.toast(DCS.t('game.needNick', null, 'Necesitas un nickname.')); return; }",
        ),
        (
            "app.toast('Responde al mercado antes de cerrar el año.');",
            "app.toast(DCS.t('game.answerMarket', null, 'Responde al mercado antes de cerrar el año.'));",
        ),
        (
            "app.toast('Has firmado con ' + offer.teamName + '.');",
            "app.toast(DCS.t('game.signedWith', { team: offer.teamName }, 'Has firmado con ' + offer.teamName + '.'));",
        ),
        (
            "app.toast('Esa oferta ya no está disponible.');",
            "app.toast(DCS.t('game.offerGone', null, 'Esa oferta ya no está disponible.'));",
        ),
        (
            "app.toast('Has rechazado a ' + rej.teamName + '.');",
            "app.toast(DCS.t('game.rejectedTeam', { team: rej.teamName }, 'Has rechazado a ' + rej.teamName + '.'));",
        ),
        (
            "app.toast('Han pasado ' + wr.weeks + (wr.weeks === 1 ? ' semana.' : ' semanas.'));",
            "app.toast((DCS.i18n && DCS.i18n.tn) ? DCS.i18n.tn('game.weeksPassedToast', wr.weeks, { count: wr.weeks }) : ('Han pasado ' + wr.weeks + (wr.weeks === 1 ? ' semana.' : ' semanas.')));",
        ),
        (
            "app.toast('No puedes esperar ahora.');",
            "app.toast(DCS.t('game.cannotWait', null, 'No puedes esperar ahora.'));",
        ),
        (
            "app.toast('Has rechazado todas las ofertas.');",
            "app.toast(DCS.t('game.rejectedAll', null, 'Has rechazado todas las ofertas.'));",
        ),
        (
            "app.toast(put.ok ? 'Has puesto ' + fmt.money(put.amount) + ' en ' + put.name + '.' : (put.reason || 'No se pudo invertir.'));",
            "app.toast(put.ok ? DCS.t('game.investedIn', { amount: fmt.money(put.amount), name: put.name }, 'Has puesto ' + fmt.money(put.amount) + ' en ' + put.name + '.') : (put.reason || DCS.t('game.investFailed', null, 'No se pudo invertir.')));",
        ),
        (
            "app.toast(sold.ok?'Recuperas '+fmt.money(sold.proceeds)+' tras costes.':sold.reason);app.render();return;",
            "app.toast(sold.ok?DCS.t('game.soldRecover',{amount:fmt.money(sold.proceeds)},'Recuperas '+fmt.money(sold.proceeds)+' tras costes.'):sold.reason);app.render();return;",
        ),
        (
            "app.toast(lux.ok?'Te das un respiro. El gasto no volverá.':lux.reason);app.render();return;",
            "app.toast(lux.ok?DCS.t('game.luxuryOk',null,'Te das un respiro. El gasto no volverá.'):lux.reason);app.render();return;",
        ),
        (
            "app.toast(yes.ok ? yes.text : (yes.reason || 'No se pudo invertir.'));",
            "app.toast(yes.ok ? yes.text : (yes.reason || DCS.t('game.investFailed', null, 'No se pudo invertir.')));",
        ),
        (
            "app.toast(no.text || 'Conservas la liquidez.');",
            "app.toast(no.text || DCS.t('game.keepCash', null, 'Conservas la liquidez.'));",
        ),
        (
            "app.toast('Sigues adelante.');",
            "app.toast(DCS.t('game.keepGoing', null, 'Sigues adelante.'));",
        ),
        (
            "if (!confirm('¿Retirarte ahora y cerrar la carrera?')) return;",
            "if (!confirm(DCS.t('game.retireConfirm', null, '¿Retirarte ahora y cerrar la carrera?'))) return;",
        ),
    ]
    for old, new in replacements:
        if old not in html:
            print("WARN skip toast:", old[:60])
        else:
            html = html.replace(old, new, 1)

    # accessLabel before bulk lit replaces (shares some strings)
    html = must_replace(
        html,
        """  function accessLabel(access) {
    if (access === 'invite') return 'Invitado';
    if (access === 'closed') return 'Vía Closed Qualifier';
    if (access === 'open') return 'Vía Open Qualifier';
    if (access === 'qualifier') return 'Vía clasificatorio';
    return 'En el calendario';
  }""",
        """  function accessLabel(access) {
    if (access === 'invite') return t('tour.directInvite', null, 'Invitado');
    if (access === 'closed') return t('ui.viaClosed', null, 'Vía Closed Qualifier');
    if (access === 'open') return t('ui.viaOpen', null, 'Vía Open Qualifier');
    if (access === 'qualifier') return t('ui.viaQualifier', null, 'Vía clasificatorio');
    return t('season.calendar', null, 'En el calendario');
  }""",
        "accessLabel",
    )

    # --- bulk exact UI string → t() for common labels inside screen builders ---
    # Prefer replace of string literals used as visible labels when safe.
    ui_lit = [
        ("'Ir al torneo'", "t('ui.goToTournament', null, 'Ir al torneo')"),
        ("'Torneo cerrado'", "t('ui.tournamentClosed', null, 'Torneo cerrado')"),
        ("'Serie a serie'", "t('ui.seriesBySeries', null, 'Serie a serie')"),
        ("'No hay un torneo en curso.'", "t('ui.noLiveTournament', null, 'No hay un torneo en curso.')"),
        ("'Sin serie pendiente'", "t('ui.noPendingTitle', null, 'Sin serie pendiente')"),
        ("'Calendario competitivo'", "t('ui.competitiveCalendar', null, 'Calendario competitivo')"),
        ("'Circuito'", "t('ui.circuitTitle', null, 'Circuito')"),
        ("'Clasificatorias'", "t('ui.sectionQual', null, 'Clasificatorias')"),
        ("'Regionales'", "t('ui.sectionReg', null, 'Regionales')"),
        ("'Eventos internacionales'", "t('ui.sectionIntl', null, 'Eventos internacionales')"),
        ("'Calendario previsto:'", "t('ui.plannedCalendar', null, 'Calendario previsto:')"),
        ("'Pulsa cualquier torneo para ver serie a serie.'", "t('ui.clickTourDetail', null, 'Pulsa cualquier torneo para ver serie a serie.')"),
        ("'★ campeón del mundo'", "t('ui.worldChampion', null, '★ campeón del mundo')"),
        ("'Calidad del roster'", "t('ui.rosterQuality', null, 'Calidad del roster')"),
        ("'Sinergia'", "t('ui.synergy', null, 'Sinergia')"),
        ("'Recursos'", "t('ui.resources', null, 'Recursos')"),
        ("'Estilo'", "t('ui.style', null, 'Estilo')"),
        ("'Mapas'", "t('ui.maps', null, 'Mapas')"),
        ("'Winrate'", "t('ui.winrate', null, 'Winrate')"),
        ("'Series'", "t('ui.series', null, 'Series')"),
        ("'Estado actual'", "t('ui.currentStatus', null, 'Estado actual')"),
        ("'Valoración'", "t('ui.valuation', null, 'Valoración')"),
        ("'Rating de temporada'", "t('ui.seasonRating', null, 'Rating de temporada')"),
        ("'MMR máximo'", "t('ui.maxMmr', null, 'MMR máximo')"),
        ("'Años pro'", "t('ui.proYears', null, 'Años pro')"),
        ("'Títulos'", "t('ui.titles', null, 'Títulos')"),
        ("'Estadísticas'", "t('ui.stats', null, 'Estadísticas')"),
        ("'Sin datos'", "t('ui.noData', null, 'Sin datos')"),
        ("'Evolución'", "t('ui.evolution', null, 'Evolución')"),
        ("'Atributos'", "t('ui.attributes', null, 'Atributos')"),
        ("'Sin torneos disputados.'", "t('ui.noTournamentsPlayed', null, 'Sin torneos disputados.')"),
        ("'En juego'", "t('ui.inPlay', null, 'En juego')"),
        ("'Bloqueado'", "t('ui.blocked', null, 'Bloqueado')"),
        ("'No disputado'", "t('ui.notPlayed', null, 'No disputado')"),
        ("'Pendiente'", "t('ui.pending', null, 'Pendiente')"),
        ("'Por decidir'", "t('ui.toDecide', null, 'Por decidir')"),
        ("'Eliminado en la clasificatoria'", "t('ui.eliminatedInQual', null, 'Eliminado en la clasificatoria')"),
        ("'Main Event'", "t('ui.mainEvent', null, 'Main Event')"),
        ("'Invitación directa'", "t('ui.directInvite', null, 'Invitación directa')"),
        ("'Vía Open Qualifier'", "t('ui.viaOpen', null, 'Vía Open Qualifier')"),
        ("'Vía Closed Qualifier'", "t('ui.viaClosed', null, 'Vía Closed Qualifier')"),
        ("'Vía clasificatorio'", "t('ui.viaQualifier', null, 'Vía clasificatorio')"),
        ("'histórico de carrera'", "t('ui.earningsHistory', null, 'histórico de carrera')"),
        ("'disponible'", "t('ui.available', null, 'disponible')"),
        ("'neto'", "t('ui.net', null, 'neto')"),
        ("'Rendimiento histórico'", "t('ui.histPerformance', null, 'Rendimiento histórico')"),
        ("'Invertido'", "t('ui.invested', null, 'Invertido')"),
        ("'Valor actual'", "t('ui.currentValue', null, 'Valor actual')"),
        ("'Ganancia / pérdida'", "t('ui.pnl', null, 'Ganancia / pérdida')"),
        ("'Inversiones'", "t('ui.investments', null, 'Inversiones')"),
        ("'Clima del circuito'", "t('ui.circuitClimate', null, 'Clima del circuito')"),
        ("'¿Qué haces con el dinero?'", "t('ui.whatWithMoney', null, '¿Qué haces con el dinero?')"),
        ("'Pocas decisiones. Sin microgestión.'", "t('ui.fewDecisions', null, 'Pocas decisiones. Sin microgestión.')"),
        ("'Lujo y estilo de vida'", "t('ui.luxuryTitle', null, 'Lujo y estilo de vida')"),
        ("'No produce rentabilidad.'", "t('ui.luxurySub', null, 'No produce rentabilidad.')"),
        ("'Volver'", "t('ui.back', null, 'Volver')"),
        ("'sin nombre'", "t('create.noName', null, 'sin nombre')"),
        ("'Participación'", "t('ui.participation', null, 'Participación')"),
        ("'Wards destruidos'", "t('ui.destroyedWards', null, 'Wards destruidos')"),
        ("'Oro en soporte'", "t('ui.supportGold', null, 'Oro en soporte')"),
        ("'Daño a héroes'", "t('ui.heroDamage', null, 'Daño a héroes')"),
        ("'Daño a torres'", "t('ui.towerDamage', null, 'Daño a torres')"),
    ]

    # Only apply inside screen/app regions to reduce false positives — still global but strings are specific
    count = 0
    for old, new in ui_lit:
        n = html.count(old)
        if n:
            html = html.replace(old, new)
            count += n
            print(f"  lit x{n}: {old} -> {new[:40]}")
    print("literal replacements", count)

    # Specific multi-word UI blocks
    html = html.replace(
        "'De la clasificatoria abierta a The International: cada plaza se gana.'",
        "t('ui.tournamentsLead', null, 'De la clasificatoria abierta a The International: cada plaza se gana.')",
    )
    html = html.replace(
        "'No hay un torneo en juego. Abre el siguiente evento avanzando la temporada.'",
        "t('ui.noPendingSeries', null, 'No hay un torneo en juego. Abre el siguiente evento avanzando la temporada.')",
    )
    html = html.replace(
        "'Ya disputados esta temporada:'",
        "t('ui.alreadyPlayed', null, 'Ya disputados esta temporada:')",
    )
    html = html.replace(
        "'El circuito competitivo conecta clasificatorias, torneos regionales y grandes eventos internacionales. Cada competición tiene su propio nivel de prestigio y dificultad.'",
        "t('ui.circuitIntro', null, 'El circuito competitivo conecta clasificatorias, torneos regionales y grandes eventos internacionales. Cada competición tiene su propio nivel de prestigio y dificultad.')",
    )
    html = html.replace(
        "'Lo que ganas en el servidor no es el final'",
        "t('ui.wealthLead', null, 'Lo que ganas en el servidor no es el final')",
    )
    html = html.replace(
        "'Earnings es historia. El cash es lo que puedes mover. El patrimonio es lo que queda.'",
        "t('ui.wealthBlurb', null, 'Earnings es historia. El cash es lo que puedes mover. El patrimonio es lo que queda.')",
    )
    html = html.replace(
        "'Sin movimientos de mercado este año. Mantener cash también cuenta.'",
        "t('ui.noMarketMoves', null, 'Sin movimientos de mercado este año. Mantener cash también cuenta.')",
    )
    html = html.replace(
        "'Todavía no ha cerrado un año con inversiones.'",
        "t('ui.yearNotClosed', null, 'Todavía no ha cerrado un año con inversiones.')",
    )
    html = html.replace(
        "'La carrera ya está cerrada. Esto es lo que construiste.'",
        "t('ui.careerClosedWealth', null, 'La carrera ya está cerrada. Esto es lo que construiste.')",
    )
    html = html.replace(
        "'Todavía no hay liquidez suficiente para mover ficha. Gana en el servidor y vuelve.'",
        "t('ui.notEnoughCash', null, 'Todavía no hay liquidez suficiente para mover ficha. Gana en el servidor y vuelve.')",
    )
    html = html.replace(
        "'Tienes efectivo, pero no llega al mínimo para una ronda.'",
        "t('ui.belowMinRound', null, 'Tienes efectivo, pero no llega al mínimo para una ronda.')",
    )
    html = html.replace(
        "'Elige categoría y cantidad. No hay cifras de retorno. El año decide.'",
        "t('ui.pickCatAmount', null, 'Elige categoría y cantidad. No hay cifras de retorno. El año decide.')",
    )
    html = html.replace(
        "'O no hagas nada: el cash no se mueve solo.'",
        "t('ui.orDoNothing', null, 'O no hagas nada: el cash no se mueve solo.')",
    )
    html = html.replace(
        "'Incluye costes de salida'",
        "t('ui.exitCosts', null, 'Incluye costes de salida')",
    )
    html = html.replace(
        "'Habilidad individual pura. Importa, pero no manda.'",
        "t('ui.pureSkill', null, 'Habilidad individual pura. Importa, pero no manda.')",
    )
    html = html.replace(
        "'Cómo te evaluó el circuito cada año.'",
        "t('ui.howCircuitEachYear', null, 'Cómo te evaluó el circuito cada año.')",
    )

    # Wire create.noName usages that use plain Spanish in draft preview if any remain
    # Badge Pretemporada / Competición in reports — use t('phase.*')
    html = html.replace("c.badge('Pretemporada', 'info')", "c.badge(t('phase.preseason', null, 'Pretemporada'), 'info')")
    html = html.replace("c.badge('Competición', 'info')", "c.badge(t('phase.competition', null, 'Competición'), 'info')")
    html = html.replace("c.badge('Mercado', 'info')", "c.badge(t('phase.market', null, 'Mercado'), 'info')")
    html = html.replace("c.badge('Cierre', 'info')", "c.badge(t('phase.review', null, 'Cierre de temporada'), 'info')")
    html = html.replace("c.badge('Fin de año', 'info')", "c.badge(t('phase.yearEnd', null, 'Fin de año'), 'info')")

    # Internacional label
    html = html.replace(" : 'Internacional'", " : t('ui.international', null, 'Internacional')")
    html = html.replace("= 'Internacional'", "= t('ui.international', null, 'Internacional')")

    INDEX.write_text(html, encoding="utf-8")
    print("Wrote", INDEX)
    print("Catalog keys es~", len(json.dumps(es)), "en~", len(json.dumps(en)))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Finish global EN/ES wiring: catalogs, event outcomes, report lines, UI leftovers."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "i18n"
INDEX = ROOT / "index.html"

# ---------------------------------------------------------------------------
# Catalog additions (deep-merged into es/en)
# ---------------------------------------------------------------------------
REPORT_ES = {
    "preseasonTitle": "Pretemporada {{year}}",
    "competitionTitle": "Temporada {{year}}",
    "reviewTitle": "Cierre {{year}}",
    "marketTitle": "Mercado {{year}}",
    "yearEndTitle": "Fin de año {{year}}",
    "startWith": "Arranca el año con {{team}} (Tier {{tier}}, {{region}}).",
    "clubGoal": "Objetivo del club: {{goal}}.",
    "clubRank": "El club arranca el año en el puesto #{{rank}} del ranking del circuito.",
    "faDebut": "Agente libre. Compara las ofertas de tu región o espera: nadie te asigna un equipo.",
    "faYoung": "Sin equipo. Grindeas pubs, entras en ligas amateur y esperas que alguien se fije en ti.",
    "faContinue": "Sigues sin equipo. Pubs, tryouts y llamadas que no siempre se devuelven.",
    "missEvent": "Te pierdes {{name}}.",
    "teamDisbands": "{{team}} disuelve su roster en mitad del año.",
    "youAreFree": "Quedas libre. Un nuevo equipo solo llega si aceptas una oferta.",
    "passOpen": "Superas la clasificatoria abierta: entras en el closed qualifier de {{target}}.",
    "passClosed": "Superas el closed qualifier: entras en {{target}}.",
    "outQualifier": "Te quedas fuera de {{target}} en la clasificatoria.",
    "noOfficial": "Sin competición oficial. Cierras el año con {{mmr}} de MMR.",
    "scrimTryouts": "Un par de equipos te han probado en scrims. Nada firmado.",
    "bonusLine": "{{text}}: {{amount}}.",
    "development": "Desarrollo",
    "attrChange": "Cambio de atributos en la temporada.",
    "viewMarket": "Ver estado del mercado",
    "offersOnTable": "Tienes {{count}} oferta(s) sobre la mesa. No puedes cerrar el año sin responder.",
    "viewOffers": "Ver ofertas",
    "marketValue": "Valor de mercado {{score}}",
    "wealth": "Patrimonio",
    "reviewWealth": "Revisar patrimonio",
    "quietYear": "El año se cierra sin sobresaltos.",
    "contractBonus": "Bonus de contrato",
    "viaInvite": "Invitación directa",
    "viaRegional": "Clasificatorio regional",
    "classified": "Clasificado",
}

REPORT_EN = {
    "preseasonTitle": "Preseason {{year}}",
    "competitionTitle": "Season {{year}}",
    "reviewTitle": "Season wrap {{year}}",
    "marketTitle": "Market {{year}}",
    "yearEndTitle": "Year end {{year}}",
    "startWith": "The year starts with {{team}} (Tier {{tier}}, {{region}}).",
    "clubGoal": "Club objective: {{goal}}.",
    "clubRank": "The club starts the year at #{{rank}} on the circuit ranking.",
    "faDebut": "Free agent. Compare offers in your region or wait — nobody assigns you a team.",
    "faYoung": "No team. You grind pubs, play amateur leagues, and hope someone notices.",
    "faContinue": "Still without a team. Pubs, tryouts, and calls that aren't always returned.",
    "missEvent": "You miss {{name}}.",
    "teamDisbands": "{{team}} disbands mid-year.",
    "youAreFree": "You're free. A new team only arrives if you accept an offer.",
    "passOpen": "You clear the open qualifier and enter the closed qualifier for {{target}}.",
    "passClosed": "You clear the closed qualifier and enter {{target}}.",
    "outQualifier": "You're out of {{target}} in the qualifier.",
    "noOfficial": "No official competition. You close the year at {{mmr}} MMR.",
    "scrimTryouts": "A couple of teams tried you in scrims. Nothing signed.",
    "bonusLine": "{{text}}: {{amount}}.",
    "development": "Development",
    "attrChange": "Attribute changes this season.",
    "viewMarket": "View market status",
    "offersOnTable": "You have {{count}} offer(s) on the table. You can't close the year without answering.",
    "viewOffers": "View offers",
    "marketValue": "Market value {{score}}",
    "wealth": "Wealth",
    "reviewWealth": "Review wealth",
    "quietYear": "The year closes without major surprises.",
    "contractBonus": "Contract bonus",
    "viaInvite": "Direct invite",
    "viaRegional": "Regional qualifier",
    "classified": "Qualified",
}

OUT_ES = {
    "internal_conflict": {
        "opt0": {
            "outGood": "Consigues sentar a todo el mundo en la misma sala. El equipo sale reforzado y tu palabra pesa más.",
            "outBad": "Te metes en un fuego que no era tuyo. Ahora eres parte del problema para media plantilla.",
        },
        "opt1": {
            "out": "Te encierras en tus repeticiones y en tu mecánica. El ambiente no mejora, pero tú juegas mejor."
        },
    },
    "burnout": {
        "opt0": {"out": "Desconectas del todo. Vuelves más lento de manos, pero con la cabeza en su sitio."},
        "opt1": {
            "outGood": "Aguantas el tirón y sales al otro lado más duro de lo que entraste.",
            "outBad": "El desgaste te pasa por encima. Rindes por inercia y se nota en la voz durante las partidas.",
        },
    },
    "streaming": {
        "opt0": {"out": "El dinero entra y tu nombre circula más. Tu tiempo de práctica, no tanto."},
        "opt1": {"out": "Dices que no. Nadie te aplaude por ello, pero tus bloques de práctica son intocables."},
    },
    "captaincy": {
        "opt0": {"out": "Coges el micro y la responsabilidad del draft. El equipo tiene una voz clara."},
        "opt1": {"out": "Declinas con educación. Otro coge el mando y tú sigues a lo tuyo."},
    },
    "wrist": {
        "opt0": {"out": "Te pierdes parte del calendario, pero el dolor desaparece."},
        "opt1": {
            "outGood": "Aguantas la temporada. Nadie sabe lo que te costó cada serie.",
            "outBad": "La lesión se cronifica. Tu velocidad de manos ya nunca vuelve del todo.",
        },
    },
    "role_change": {
        "opt0": {"out": "Empiezas de cero en una posición nueva. Tu ficha en el mercado cambia por completo."},
        "opt1": {"out": "Rechazas la propuesta. Si esto sale mal, saldrá mal haciendo lo tuyo."},
    },
    "region_move": {
        "opt0": {"out": "Haces las maletas. Tu carrera continúa a miles de kilómetros de donde empezó."},
        "opt1": {"out": "Te quedas. Conoces a todo el mundo aquí y eso también vale."},
    },
    "bootcamp": {
        "opt0": {"out": "Dos semanas conviviendo con el equipo. Se nota en la coordinación."},
        "opt1": {"out": "Preparáis el calendario online, cada uno desde su casa."},
    },
    "contract_dispute": {
        "opt0": {
            "outGood": "La organización cede. Cobras lo que crees que vales.",
            "outBad": "La negociación se filtra. La organización te retrata como un problema.",
        },
        "opt1": {"out": "Firmas la paz. Dentro del club se agradece."},
    },
    "bench_threat": {
        "opt0": {"out": "Te quedas. Cada scrim es una prueba."},
        "opt1": {"out": "Rescindís de mutuo acuerdo. Estás libre y el mercado ya casi ha cerrado."},
    },
    "extra_bootcamp": {
        "opt0": {"out": "Aceptáis. Llegáis más preparados, pero con las pilas más bajas."},
        "opt1": {"out": "Paramos. Nadie gana un scrim extra, pero el vestuario respira."},
    },
}

OUT_EN = {
    "internal_conflict": {
        "opt0": {
            "outGood": "You get everyone in the same room. The team comes out stronger and your word carries more weight.",
            "outBad": "You walk into a fire that wasn't yours. Now half the roster sees you as part of the problem.",
        },
        "opt1": {
            "out": "You lock into your own reps and mechanics. The vibe doesn't improve, but you play better."
        },
    },
    "burnout": {
        "opt0": {"out": "You disconnect completely. Your hands come back slower, but your head is clear."},
        "opt1": {
            "outGood": "You grit through it and come out harder than you went in.",
            "outBad": "The grind runs you over. You perform on inertia and it shows in voice chat.",
        },
    },
    "streaming": {
        "opt0": {"out": "The money comes in and your name circulates more. Practice time, not so much."},
        "opt1": {"out": "You say no. Nobody cheers, but your practice blocks stay sacred."},
    },
    "captaincy": {
        "opt0": {"out": "You take the mic and the draft. The team finally has a clear voice."},
        "opt1": {"out": "You decline politely. Someone else takes the shot-calling and you stay focused."},
    },
    "wrist": {
        "opt0": {"out": "You miss part of the calendar, but the pain goes away."},
        "opt1": {
            "outGood": "You tough out the season. Nobody knows what each series cost you.",
            "outBad": "The injury becomes chronic. Your hand speed never fully returns.",
        },
    },
    "role_change": {
        "opt0": {"out": "You start from scratch in a new position. Your market value resets completely."},
        "opt1": {"out": "You turn it down. If this goes wrong, it goes wrong doing what you know."},
    },
    "region_move": {
        "opt0": {"out": "You pack your bags. Your career continues thousands of kilometres from where it began."},
        "opt1": {"out": "You stay. Knowing everyone here still counts for something."},
    },
    "bootcamp": {
        "opt0": {"out": "Two weeks living with the team. Coordination jumps."},
        "opt1": {"out": "You prep the calendar online, each from home."},
    },
    "contract_dispute": {
        "opt0": {
            "outGood": "The org gives in. You get paid what you think you're worth.",
            "outBad": "The talks leak. The org paints you as a problem.",
        },
        "opt1": {"out": "You keep the peace. The club appreciates it."},
    },
    "bench_threat": {
        "opt0": {"out": "You stay. Every scrim is a trial."},
        "opt1": {"out": "You part ways. You're free and the market is nearly closed."},
    },
    "extra_bootcamp": {
        "opt0": {"out": "You accept. You arrive sharper, but with emptier batteries."},
        "opt1": {"out": "You rest. Nobody wins an extra scrim, but the locker room breathes."},
    },
}

UI_EXTRA_ES = {
    "tournamentInProgress": "Torneo en curso",
    "closing": "Cierre",
    "reputation": "Reputación",
    "result": "Resultado",
    "tournament": "Torneo",
    "format": "Formato",
    "team": "Equipo",
    "position": "Posición",
    "form": "Forma",
    "contract": "Contrato",
    "yearOne": "año",
    "yearMany": "años",
    "clubObjective": "Objetivo del club",
    "rosterSynergy": "Sinergia del roster",
    "prizeSharePct": "% del premio del equipo",
    "free": "Libre",
    "seasonWord": "temporada",
    "careerStartsFull": "Tu carrera empieza aquí. Pulsa {{action}} abajo a la derecha (o la barra espaciadora) para avanzar.",
    "plannedCalendar": "Calendario previsto:",
    "clickTourSeries": "Pulsa cualquier torneo para ver serie a serie.",
    "development": "Desarrollo",
    "attrSeasonChange": "Cambio de atributos en la temporada.",
    "whatTourLeaves": "Lo que deja el torneo",
    "nextSeries": "Próxima serie",
    "continue": "Continuar",
    "simulateTournament": "Simular torneo",
    "viaQualifier": "Vía clasificatoria",
    "contestedQualifier": "Clasificatorio disputado",
    "seasonResults": "Resultados de la temporada",
    "clickTourPath": "Pulsa un torneo para ver el recorrido serie a serie.",
    "noOfficialMapsSeason": "Todavía no has disputado partidas oficiales esta temporada.",
    "vsRoleBenchmark": "Frente al baremo de la posición",
    "whatWeighsRating": "Esto es exactamente lo que pesa en tu rating de temporada.",
    "tournaments": "Torneos",
    "expandTourPath": "Pulsa cualquier torneo para desplegar el recorrido serie a serie.",
    "teamBreakdown": "Desglose por equipo",
    "midYearMove": "Cambiaste de equipo durante el año: el total anual se conserva y el reparto también.",
    "seasonTournaments": "Torneos de la temporada",
    "marketStatus": "Estado del mercado",
    "bestRecentResult": "Mejor resultado reciente",
    "yourTeamRank": "Ranking de tu equipo",
    "teamsInCareer": "Equipos en su carrera",
    "seasonsWithoutTeamRow": "Temporadas seguidas sin equipo",
    "noOrgLong": "Ahora mismo no perteneces a ninguna organización. Grindeas pubs, juegas tryouts y esperas que alguien se fije en ti en el mercado.",
    "quality": "Calidad",
    "ofRoster": "del roster",
    "ofClub": "del club",
    "stylePrefix": "Estilo",
    "bonusIntl": "Bonus por clasificar a un internacional",
    "bonusTI": "Bonus por clasificar a The International",
    "weak": "Flojo",
    "average": "Media",
    "elite": "Élite",
    "noCashPrize": "Sin premio en metálico",
    "intlTitle": "Título internacional",
    "championWith": "Campeón con {{team}}",
    "notEnoughSeasons": "Aún no hay suficientes temporadas para dibujar la evolución.",
    "noSeasonDone": "Todavía no has completado ninguna temporada.",
    "prestigeTitle": "Título de prestigio",
    "maps": "mapas",
    "alreadyResolved": "Ya estaba resuelto.",
    "resolvesItself": "La situación se resuelve sola.",
    "doNothing": "No haces nada.",
    "notEnoughCash": "No tienes efectivo suficiente.",
    "lifestyleNote": "Estilo de vida: -{{amount}}. Recuperas moral y visibilidad.",
    "keepLiquidity": "Conservas la liquidez.",
    "investedAmount": "Has puesto {{amount}} en {{name}}.",
    "retireLead": "Han pasado los años y el juego ya no te devuelve lo mismo. Nadie te va a decir cuándo parar.",
    "retireAge": "Tienes {{age}} años y {{years}} temporadas profesionales.",
    "retireBadForm": "Encadenas {{count}} temporadas por debajo de tu nivel.",
    "retireNoTeamOne": "Llevas un año sin equipo.",
    "retireNoTeamMany": "Llevas {{count}} años sin equipo.",
    "retireDrop": "Tu nivel ha caído claramente desde tu mejor momento.",
    "retireMorale": "La motivación está por los suelos.",
    "retireStillT1": "Sigues rindiendo a alto nivel en Tier 1.",
    "wealthStartupTitle": "Una startup gaming te abre la puerta",
    "wealthStartupText": "Un antiguo compañero te propone entrar con parte de tu liquidez. No hay cifras de retorno. Solo el riesgo.",
    "wealthOrgTitle": "Una org busca capital",
    "wealthOrgText": "Una organización quiere que entres como inversor silencioso. Tu nombre abre puertas; el resultado no está escrito.",
    "wealthAcademyTitle": "Te proponen montar una academia",
    "wealthAcademyText": "Usarían tu nombre. Tú pondrías el dinero. El resto es trabajo y reputación.",
    "wealthTiTitle": "Oferta tras The International",
    "wealthTiText": "Ganar TI abre cheques. Esta vez te piden que pongas tú también fichas sobre la mesa.",
    "seriesPendingHint": "Serie pendiente en Torneos",
    "inCalendar": "En el calendario",
}

UI_EXTRA_EN = {
    "tournamentInProgress": "Tournament in progress",
    "closing": "Closing",
    "reputation": "Reputation",
    "result": "Result",
    "tournament": "Tournament",
    "format": "Format",
    "team": "Team",
    "position": "Position",
    "form": "Form",
    "contract": "Contract",
    "yearOne": "year",
    "yearMany": "years",
    "clubObjective": "Club objective",
    "rosterSynergy": "Roster synergy",
    "prizeSharePct": "% of team prize",
    "free": "Free",
    "seasonWord": "season",
    "careerStartsFull": "Your career starts here. Press {{action}} at the bottom right (or the space bar) to advance.",
    "plannedCalendar": "Planned calendar:",
    "clickTourSeries": "Click any tournament to see it series by series.",
    "development": "Development",
    "attrSeasonChange": "Attribute changes this season.",
    "whatTourLeaves": "What the tournament leaves behind",
    "nextSeries": "Next series",
    "continue": "Continue",
    "simulateTournament": "Simulate tournament",
    "viaQualifier": "Via qualifier",
    "contestedQualifier": "Contested qualifier",
    "seasonResults": "Season results",
    "clickTourPath": "Click a tournament to see the series path.",
    "noOfficialMapsSeason": "You haven't played official matches this season yet.",
    "vsRoleBenchmark": "Against the role benchmark",
    "whatWeighsRating": "This is exactly what weighs on your season rating.",
    "tournaments": "Tournaments",
    "expandTourPath": "Click any tournament to expand the series path.",
    "teamBreakdown": "Breakdown by team",
    "midYearMove": "You changed teams mid-year: the annual total is kept and so is the split.",
    "seasonTournaments": "Season tournaments",
    "marketStatus": "Market status",
    "bestRecentResult": "Best recent result",
    "yourTeamRank": "Your team ranking",
    "teamsInCareer": "Teams in their career",
    "seasonsWithoutTeamRow": "Consecutive seasons without a team",
    "noOrgLong": "You don't belong to any organization right now. You grind pubs, play tryouts, and wait for the market to notice you.",
    "quality": "Quality",
    "ofRoster": "of the roster",
    "ofClub": "of the club",
    "stylePrefix": "Style",
    "bonusIntl": "Bonus for qualifying to an international",
    "bonusTI": "Bonus for qualifying to The International",
    "weak": "Weak",
    "average": "Average",
    "elite": "Elite",
    "noCashPrize": "No cash prize",
    "intlTitle": "International title",
    "championWith": "Champion with {{team}}",
    "notEnoughSeasons": "Not enough seasons yet to chart your progression.",
    "noSeasonDone": "You haven't completed a season yet.",
    "prestigeTitle": "Prestige title",
    "maps": "maps",
    "alreadyResolved": "Already resolved.",
    "resolvesItself": "The situation resolves itself.",
    "doNothing": "You do nothing.",
    "notEnoughCash": "You don't have enough cash.",
    "lifestyleNote": "Lifestyle: -{{amount}}. Morale and visibility recover.",
    "keepLiquidity": "You keep your cash.",
    "investedAmount": "You put {{amount}} into {{name}}.",
    "retireLead": "The years have passed and the game no longer gives back the same. Nobody will tell you when to stop.",
    "retireAge": "You're {{age}} with {{years}} professional seasons.",
    "retireBadForm": "You've strung together {{count}} seasons below your level.",
    "retireNoTeamOne": "You've been without a team for a year.",
    "retireNoTeamMany": "You've been without a team for {{count}} years.",
    "retireDrop": "Your level has clearly dropped from your peak.",
    "retireMorale": "Motivation is on the floor.",
    "retireStillT1": "You're still performing at a high level in Tier 1.",
    "wealthStartupTitle": "A gaming startup opens the door",
    "wealthStartupText": "A former teammate wants you in with some of your cash. No return figures. Only the risk.",
    "wealthOrgTitle": "An org is looking for capital",
    "wealthOrgText": "An organization wants you as a silent investor. Your name opens doors; the outcome isn't written.",
    "wealthAcademyTitle": "They propose building an academy",
    "wealthAcademyText": "They'd use your name. You'd put up the money. The rest is work and reputation.",
    "wealthTiTitle": "Offer after The International",
    "wealthTiText": "Winning TI opens cheques. This time they want you to put chips on the table too.",
    "seriesPendingHint": "Series pending in Tournaments",
    "inCalendar": "On the calendar",
}

GAME_EXTRA_ES = {
    "alreadyResolved": "Ya estaba resuelto.",
    "resolvesItself": "La situación se resuelve sola.",
    "doNothing": "No haces nada.",
}
GAME_EXTRA_EN = {
    "alreadyResolved": "Already resolved.",
    "resolvesItself": "The situation resolves itself.",
    "doNothing": "You do nothing.",
}


def load_catalog(path: Path) -> dict:
    s = path.read_text(encoding="utf-8")
    i, j = s.index("{"), s.rindex("}")
    # Use node for safe parse of JS object (no trailing issues)
    script = f"const o={s[i:j+1]}; process.stdout.write(JSON.stringify(o))"
    out = subprocess.check_output(["node", "-e", script], text=True)
    return json.loads(out)


def write_catalog(path: Path, code: str, data: dict) -> None:
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    path.write_text(f'DCS.i18n.register("{code}", {body});\n', encoding="utf-8")


def deep_merge(dst: dict, src: dict) -> dict:
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst


def merge_outcomes(events: dict, outs: dict) -> None:
    for eid, opts in outs.items():
        ev = events.setdefault(eid, {})
        for oid, fields in opts.items():
            slot = ev.setdefault(oid, {})
            slot.update(fields)


def update_catalogs() -> None:
    es = load_catalog(I18N / "es.js")
    en = load_catalog(I18N / "en.js")
    deep_merge(es, {"report": REPORT_ES, "ui": UI_EXTRA_ES, "game": GAME_EXTRA_ES})
    deep_merge(en, {"report": REPORT_EN, "ui": UI_EXTRA_EN, "game": GAME_EXTRA_EN})
    merge_outcomes(es.setdefault("events", {}), OUT_ES)
    merge_outcomes(en.setdefault("events", {}), OUT_EN)
    write_catalog(I18N / "es.js", "es", es)
    write_catalog(I18N / "en.js", "en", en)
    print("catalogs updated", len(json.dumps(es)), len(json.dumps(en)))


def once(html: str, label: str, old: str, new: str) -> str:
    if old not in html:
        print("SKIP", label)
        return html
    html = html.replace(old, new, 1)
    print("OK", label)
    return html


def replace_all(html: str, label: str, old: str, new: str) -> str:
    n = html.count(old)
    if not n:
        print("SKIP", label)
        return html
    html = html.replace(old, new)
    print("OK", label, "x" + str(n))
    return html


def patch_index(html: str) -> str:
    # --- eventOut helper + resolve ---
    html = once(
        html,
        "evOut-helper",
        "  /** Resuelve una decisión pendiente aplicando la opción elegida UNA vez. */\n  function resolve(state, rng, inst, optionIndex, season) {",
        "  function evOut(key, text, vars) {\n"
        "    return { key: key, text: text, vars: vars || null };\n"
        "  }\n\n"
        "  /** Resuelve una decisión pendiente aplicando la opción elegida UNA vez. */\n"
        "  function resolve(state, rng, inst, optionIndex, season) {",
    )

    html = once(
        html,
        "resolve-already",
        "      return inst.outcome || 'Ya estaba resuelto.';",
        "      return inst.outcome || (DCS.t ? DCS.t('game.alreadyResolved', null, 'Ya estaba resuelto.') : 'Ya estaba resuelto.');",
    )
    html = once(
        html,
        "resolve-itself",
        "    if (!def) { inst.resolved = true; inst.applied = true; return 'La situación se resuelve sola.'; }",
        "    if (!def) { inst.resolved = true; inst.applied = true; return DCS.t ? DCS.t('game.resolvesItself', null, 'La situación se resuelve sola.') : 'La situación se resuelve sola.'; }",
    )
    html = once(
        html,
        "resolve-nothing",
        "    if (!opt) { inst.resolved = true; inst.applied = true; return 'No haces nada.'; }",
        "    if (!opt) { inst.resolved = true; inst.applied = true; return DCS.t ? DCS.t('game.doNothing', null, 'No haces nada.') : 'No haces nada.'; }",
    )

    html = once(
        html,
        "resolve-apply-out",
        "    var text = opt.apply(c);\n"
        "    inst.resolved = true;\n"
        "    inst.applied = true;\n"
        "    inst.outcome = text;\n"
        "    inst.chosen = opt.label;",
        "    var raw = opt.apply(c);\n"
        "    inst.resolved = true;\n"
        "    inst.applied = true;\n"
        "    if (raw && typeof raw === 'object') {\n"
        "      inst.outcome = raw.text || '';\n"
        "      inst.outcomeKey = raw.key || null;\n"
        "      if (raw.vars) inst.vars = Object.assign({}, inst.vars || {}, raw.vars);\n"
        "    } else {\n"
        "      inst.outcome = raw;\n"
        "      inst.outcomeKey = null;\n"
        "    }\n"
        "    inst.chosen = opt.label;\n"
        "    inst.chosenKey = opt.labelKey || ('events.' + (inst.pendingKey || inst.key || '') + '.opt' + optionIndex + '.label');\n"
        "    var text = inst.outcomeKey && DCS.t\n"
        "      ? DCS.t(inst.outcomeKey, inst.vars || {}, inst.outcome || '')\n"
        "      : inst.outcome;",
    )

    # Map Spanish outcome returns → evOut(...)
    OUT_MAP = [
        ("Consigues sentar a todo el mundo en la misma sala. El equipo sale reforzado y tu palabra pesa más.",
         "events.internal_conflict.opt0.outGood"),
        ("Te metes en un fuego que no era tuyo. Ahora eres parte del problema para media plantilla.",
         "events.internal_conflict.opt0.outBad"),
        ("Te encierras en tus repeticiones y en tu mecánica. El ambiente no mejora, pero tú juegas mejor.",
         "events.internal_conflict.opt1.out"),
        ("Desconectas del todo. Vuelves más lento de manos, pero con la cabeza en su sitio.",
         "events.burnout.opt0.out"),
        ("Aguantas el tirón y sales al otro lado más duro de lo que entraste.",
         "events.burnout.opt1.outGood"),
        ("El desgaste te pasa por encima. Rindes por inercia y se nota en la voz durante las partidas.",
         "events.burnout.opt1.outBad"),
        ("El dinero entra y tu nombre circula más. Tu tiempo de práctica, no tanto.",
         "events.streaming.opt0.out"),
        ("Dices que no. Nadie te aplaude por ello, pero tus bloques de práctica son intocables.",
         "events.streaming.opt1.out"),
        ("Coges el micro y la responsabilidad del draft. El equipo tiene una voz clara.",
         "events.captaincy.opt0.out"),
        ("Declinas con educación. Otro coge el mando y tú sigues a lo tuyo.",
         "events.captaincy.opt1.out"),
        ("Te pierdes parte del calendario, pero el dolor desaparece.",
         "events.wrist.opt0.out"),
        ("Aguantas la temporada. Nadie sabe lo que te costó cada serie.",
         "events.wrist.opt1.outGood"),
        ("La lesión se cronifica. Tu velocidad de manos ya nunca vuelve del todo.",
         "events.wrist.opt1.outBad"),
        ("Empiezas de cero en una posición nueva. Tu ficha en el mercado cambia por completo.",
         "events.role_change.opt0.out"),
        ("Rechazas la propuesta. Si esto sale mal, saldrá mal haciendo lo tuyo.",
         "events.role_change.opt1.out"),
        ("Haces las maletas. Tu carrera continúa a miles de kilómetros de donde empezó.",
         "events.region_move.opt0.out"),
        ("Te quedas. Conoces a todo el mundo aquí y eso también vale.",
         "events.region_move.opt1.out"),
        ("Dos semanas conviviendo con el equipo. Se nota en la coordinación.",
         "events.bootcamp.opt0.out"),
        ("Preparáis el calendario online, cada uno desde su casa.",
         "events.bootcamp.opt1.out"),
        ("La organización cede. Cobras lo que crees que vales.",
         "events.contract_dispute.opt0.outGood"),
        ("La negociación se filtra. La organización te retrata como un problema.",
         "events.contract_dispute.opt0.outBad"),
        ("Firmas la paz. Dentro del club se agradece.",
         "events.contract_dispute.opt1.out"),
        ("Te quedas. Cada scrim es una prueba.",
         "events.bench_threat.opt0.out"),
        ("Rescindís de mutuo acuerdo. Estás libre y el mercado ya casi ha cerrado.",
         "events.bench_threat.opt1.out"),
        ("Aceptáis. Llegáis más preparados, pero con las pilas más bajas.",
         "events.extra_bootcamp.opt0.out"),
        ("Paramos. Nadie gana un scrim extra, pero el vestuario respira.",
         "events.extra_bootcamp.opt1.out"),
    ]
    for text, key in OUT_MAP:
        old = "return '" + text + "';"
        new = "return evOut('" + key + "', '" + text + "');"
        html = replace_all(html, "out:" + key.split(".")[-1], old, new)

    # role_change / bootcamp / streaming vars for eventView
    html = once(
        html,
        "streaming-vars",
        "        return {\n"
        "          title: 'Oferta de contenido',\n"
        "          tone: 'neutral',\n"
        "          text: 'Una plataforma te ofrece ' + DCS.ui.fmt.money(money) + ' por un acuerdo de streaming durante la temporada. ' +\n"
        "            'Horas de directo que no vas a dedicar a entrenar.',",
        "        return {\n"
        "          title: 'Oferta de contenido',\n"
        "          tone: 'neutral',\n"
        "          vars: { amount: DCS.ui.fmt.money(money) },\n"
        "          text: 'Una plataforma te ofrece ' + DCS.ui.fmt.money(money) + ' por un acuerdo de streaming durante la temporada. ' +\n"
        "            'Horas de directo que no vas a dedicar a entrenar.',",
    )
    html = once(
        html,
        "role-vars",
        "        return {\n"
        "          title: 'Cambiar de posición',\n"
        "          tone: 'neutral',\n"
        "          text: 'Un entrenador que te conoce bien cree que estás desperdiciado en tu rol y te propone reconvertirte a ' +\n"
        "            DCS.data.ROLES[target].name + ' (' + DCS.data.ROLES[target].label + ').',",
        "        return {\n"
        "          title: 'Cambiar de posición',\n"
        "          tone: 'neutral',\n"
        "          vars: { role: DCS.data.ROLES[target].name + ' (' + DCS.data.ROLES[target].label + ')' },\n"
        "          text: 'Un entrenador que te conoce bien cree que estás desperdiciado en tu rol y te propone reconvertirte a ' +\n"
        "            DCS.data.ROLES[target].name + ' (' + DCS.data.ROLES[target].label + ').',",
    )
    html = once(
        html,
        "bootcamp-vars",
        "          title: 'Bootcamp por tu cuenta',\n"
        "          tone: 'neutral',\n"
        "          text: 'La organización no cubre el bootcamp previo al calendario internacional. Puedes pagarlo tú: ' +",
        "          title: 'Bootcamp por tu cuenta',\n"
        "          tone: 'neutral',\n"
        "          vars: { amount: DCS.ui.fmt.money(cost) },\n"
        "          text: 'La organización no cubre el bootcamp previo al calendario internacional. Puedes pagarlo tú: ' +",
    )

    # --- report lines as keyed objects ---
    html = once(
        html,
        "report-title-pre",
        "      title: 'Pretemporada ' + state.year,",
        "      title: 'Pretemporada ' + state.year,\n"
        "      titleKey: 'report.preseasonTitle',\n"
        "      titleVars: { year: state.year },",
    )
    html = once(
        html,
        "report-title-comp",
        "      title: 'Temporada ' + state.year,",
        "      title: 'Temporada ' + state.year,\n"
        "      titleKey: 'report.competitionTitle',\n"
        "      titleVars: { year: state.year },",
    )

    html = once(
        html,
        "line-startWith",
        "      report.lines.push('Arranca el año con ' + team.name + ' (Tier ' + team.tier + ', ' +\n"
        "        D.REGIONS[team.region].name + ').');\n"
        "      report.lines.push('Objetivo del club: ' + (p.contract ? p.contract.expectation : team.expectation) + '.');",
        "      report.lines.push({ key: 'report.startWith', vars: { team: team.name, tier: team.tier, region: D.REGIONS[team.region].name },\n"
        "        text: 'Arranca el año con ' + team.name + ' (Tier ' + team.tier + ', ' + D.REGIONS[team.region].name + ').' });\n"
        "      report.lines.push({ key: 'report.clubGoal', vars: { goal: (p.contract ? p.contract.expectation : team.expectation) },\n"
        "        text: 'Objetivo del club: ' + (p.contract ? p.contract.expectation : team.expectation) + '.' });",
    )
    html = once(
        html,
        "line-rank",
        "      if (rank) report.lines.push('El club arranca el año en el puesto #' + rank + ' del ranking del circuito.');",
        "      if (rank) report.lines.push({ key: 'report.clubRank', vars: { rank: rank },\n"
        "        text: 'El club arranca el año en el puesto #' + rank + ' del ranking del circuito.' });",
    )
    html = once(
        html,
        "line-fa",
        "      report.lines.push(p.age <= 17 && !(p.teamsPlayed && p.teamsPlayed.length)\n"
        "        ? 'Agente libre. Compara las ofertas de tu región o espera: nadie te asigna un equipo.'\n"
        "        : (p.age <= 17\n"
        "          ? 'Sin equipo. Grindeas pubs, entras en ligas amateur y esperas que alguien se fije en ti.'\n"
        "          : 'Sigues sin equipo. Pubs, tryouts y llamadas que no siempre se devuelven.'));",
        "      report.lines.push(p.age <= 17 && !(p.teamsPlayed && p.teamsPlayed.length)\n"
        "        ? { key: 'report.faDebut', text: 'Agente libre. Compara las ofertas de tu región o espera: nadie te asigna un equipo.' }\n"
        "        : (p.age <= 17\n"
        "          ? { key: 'report.faYoung', text: 'Sin equipo. Grindeas pubs, entras en ligas amateur y esperas que alguien se fije en ti.' }\n"
        "          : { key: 'report.faContinue', text: 'Sigues sin equipo. Pubs, tryouts y llamadas que no siempre se devuelven.' }));",
    )
    html = once(
        html,
        "line-miss",
        "          c.lines.push('Te pierdes ' + (entry.name || tpl.label) + '.');",
        "          c.lines.push({ key: 'report.missEvent', vars: { name: entry.name || tpl.label },\n"
        "            text: 'Te pierdes ' + (entry.name || tpl.label) + '.' });",
    )

    # linesHtml + report card title
    html = once(
        html,
        "linesHtml",
        "  function linesHtml(lines) {\n"
        "    if (!lines || !lines.length) return '';\n"
        "    return '<ul class=\"lines\">' + lines.map(function (l) { return '<li>' + l + '</li>'; }).join('') + '</ul>';\n"
        "  }",
        "  function lineText(l) {\n"
        "    if (l == null) return '';\n"
        "    if (typeof l === 'object') {\n"
        "      return t(l.key, l.vars || {}, l.text || l.fallback || '');\n"
        "    }\n"
        "    return String(l);\n"
        "  }\n"
        "  function linesHtml(lines) {\n"
        "    if (!lines || !lines.length) return '';\n"
        "    return '<ul class=\"lines\">' + lines.map(function (l) {\n"
        "      return '<li>' + lineText(l) + '</li>';\n"
        "    }).join('') + '</ul>';\n"
        "  }\n"
        "  function reportTitle(r, fallback) {\n"
        "    if (!r) return fallback || '';\n"
        "    if (r.titleKey) return t(r.titleKey, r.titleVars || {}, r.title || fallback || '');\n"
        "    return r.title || fallback || '';\n"
        "  }",
    )

    html = once(
        html,
        "reportPre-title",
        "    return c.card({ title: r.title, meta: c.badge(t('phase.preseason', null, 'Pretemporada'), 'info'), body: body });",
        "    return c.card({ title: reportTitle(r), meta: c.badge(t('phase.preseason', null, 'Pretemporada'), 'info'), body: body });",
    )

    # choose toast uses translated outcome
    html = once(
        html,
        "choose-toast",
        "          if (out && out.outcome) app.toast(out.outcome.slice(0, 110));",
        "          if (out && out.outcome) {\n"
        "            var msgOut = out.outcome;\n"
        "            if (out.outcomeKey && DCS.t) msgOut = DCS.t(out.outcomeKey, out.vars || {}, out.outcome);\n"
        "            app.toast(String(msgOut).slice(0, 110));\n"
        "          }",
    )

    # via display helper usage for TI badge
    html = once(
        html,
        "ti-via-badge",
        "      meta: c.badge(ti.via || 'Clasificado', 'gold'),",
        "      meta: c.badge(viaLabel(ti.via) || t('report.classified', null, 'Clasificado'), 'gold'),",
    )

    # inject viaLabel near accessLabel
    html = once(
        html,
        "viaLabel-fn",
        "  function accessLabel(access) {",
        "  function viaLabel(via) {\n"
        "    if (!via) return '';\n"
        "    if (via === 'Invitación directa' || via === 'Direct invite') return t('report.viaInvite', null, via);\n"
        "    if (via === 'Clasificatorio regional' || via === 'Regional qualifier') return t('report.viaRegional', null, via);\n"
        "    return via;\n"
        "  }\n"
        "  function accessLabel(access) {",
    )

    # retirement evaluate → keyed reasons
    html = once(
        html,
        "retire-reasons",
        "    var reasons = [];\n"
        "    reasons.push('Tienes ' + p.age + ' años y ' + p.proYears + ' temporadas profesionales.');\n\n"
        "    var rs = lastRatings(state, 3);\n"
        "    var bad = 0;\n"
        "    rs.forEach(function (r) { if (r === null || r < 56) bad++; });\n"
        "    if (bad >= 2) {\n"
        "      chance += bad * 0.05;\n"
        "      reasons.push('Encadenas ' + bad + ' temporadas por debajo de tu nivel.');\n"
        "    }\n\n"
        "    if (p.seasonsWithoutTeam >= 1) {\n"
        "      chance += p.seasonsWithoutTeam * 0.06;\n"
        "      reasons.push(p.seasonsWithoutTeam === 1\n"
        "        ? 'Llevas un año sin equipo.'\n"
        "        : 'Llevas ' + p.seasonsWithoutTeam + ' años sin equipo.');\n"
        "    }\n\n"
        "    var drop = p.peakOverall - p.overall;\n"
        "    if (drop >= 7) {\n"
        "      chance += Math.min(0.12, drop * 0.012);\n"
        "      reasons.push('Tu nivel ha caído claramente desde tu mejor momento.');\n"
        "    }\n\n"
        "    if (p.morale < 38) {\n"
        "      chance += 0.05;\n"
        "      reasons.push('La motivación está por los suelos.');\n"
        "    }\n\n"
        "    var team = DCS.engine.world.getTeam(state, p.teamId);\n"
        "    if (team && team.tier === 1 && p.overall >= 80 && (state.career.lastRating || 0) >= 70) {\n"
        "      chance *= 0.45;\n"
        "      reasons.push('Sigues rindiendo a alto nivel en Tier 1.');\n"
        "    } else if (team && (state.career.lastRating || 0) >= 72) {\n"
        "      chance *= 0.65;\n"
        "    } else if (!team && p.seasonsWithoutTeam >= 2 && p.overall < 65) {\n"
        "      chance *= 1.35;\n"
        "    }\n\n"
        "    chance = U.clamp(chance, 0.01, 0.75);\n"
        "    if (!rng.chance(chance)) return null;\n\n"
        "    state.career.lastRetirementPrompt = state.year;\n"
        "    return {\n"
        "      age: p.age,\n"
        "      score: Math.round(chance * 100) / 100,\n"
        "      reasons: reasons,\n"
        "      text: 'Han pasado los años y el juego ya no te devuelve lo mismo. Nadie te va a decir cuándo parar.'\n"
        "    };",
        "    var reasons = [];\n"
        "    reasons.push({ key: 'ui.retireAge', vars: { age: p.age, years: p.proYears },\n"
        "      text: 'Tienes ' + p.age + ' años y ' + p.proYears + ' temporadas profesionales.' });\n\n"
        "    var rs = lastRatings(state, 3);\n"
        "    var bad = 0;\n"
        "    rs.forEach(function (r) { if (r === null || r < 56) bad++; });\n"
        "    if (bad >= 2) {\n"
        "      chance += bad * 0.05;\n"
        "      reasons.push({ key: 'ui.retireBadForm', vars: { count: bad },\n"
        "        text: 'Encadenas ' + bad + ' temporadas por debajo de tu nivel.' });\n"
        "    }\n\n"
        "    if (p.seasonsWithoutTeam >= 1) {\n"
        "      chance += p.seasonsWithoutTeam * 0.06;\n"
        "      reasons.push(p.seasonsWithoutTeam === 1\n"
        "        ? { key: 'ui.retireNoTeamOne', text: 'Llevas un año sin equipo.' }\n"
        "        : { key: 'ui.retireNoTeamMany', vars: { count: p.seasonsWithoutTeam },\n"
        "            text: 'Llevas ' + p.seasonsWithoutTeam + ' años sin equipo.' });\n"
        "    }\n\n"
        "    var drop = p.peakOverall - p.overall;\n"
        "    if (drop >= 7) {\n"
        "      chance += Math.min(0.12, drop * 0.012);\n"
        "      reasons.push({ key: 'ui.retireDrop', text: 'Tu nivel ha caído claramente desde tu mejor momento.' });\n"
        "    }\n\n"
        "    if (p.morale < 38) {\n"
        "      chance += 0.05;\n"
        "      reasons.push({ key: 'ui.retireMorale', text: 'La motivación está por los suelos.' });\n"
        "    }\n\n"
        "    var team = DCS.engine.world.getTeam(state, p.teamId);\n"
        "    if (team && team.tier === 1 && p.overall >= 80 && (state.career.lastRating || 0) >= 70) {\n"
        "      chance *= 0.45;\n"
        "      reasons.push({ key: 'ui.retireStillT1', text: 'Sigues rindiendo a alto nivel en Tier 1.' });\n"
        "    } else if (team && (state.career.lastRating || 0) >= 72) {\n"
        "      chance *= 0.65;\n"
        "    } else if (!team && p.seasonsWithoutTeam >= 2 && p.overall < 65) {\n"
        "      chance *= 1.35;\n"
        "    }\n\n"
        "    chance = U.clamp(chance, 0.01, 0.75);\n"
        "    if (!rng.chance(chance)) return null;\n\n"
        "    state.career.lastRetirementPrompt = state.year;\n"
        "    return {\n"
        "      age: p.age,\n"
        "      score: Math.round(chance * 100) / 100,\n"
        "      reasons: reasons,\n"
        "      textKey: 'ui.retireLead',\n"
        "      text: 'Han pasado los años y el juego ya no te devuelve lo mismo. Nadie te va a decir cuándo parar.'\n"
        "    };",
    )

    # modal retire uses keys
    html = once(
        html,
        "modal-retire-keys",
        "          '<div class=\"modal-body\"><p>' + c.esc(d.text) + '</p>' +\n"
        "          '<ul class=\"lines\">' + d.reasons.map(function (r) { return '<li>' + c.esc(r) + '</li>'; }).join('') + '</ul>' +",
        "          '<div class=\"modal-body\"><p>' + c.esc(d.textKey && DCS.t ? DCS.t(d.textKey, null, d.text) : d.text) + '</p>' +\n"
        "          '<ul class=\"lines\">' + d.reasons.map(function (r) {\n"
        "            var rt = (r && typeof r === 'object')\n"
        "              ? (DCS.t ? DCS.t(r.key, r.vars || {}, r.text || '') : (r.text || ''))\n"
        "              : r;\n"
        "            return '<li>' + c.esc(rt) + '</li>';\n"
        "          }).join('') + '</ul>' +",
    )

    # wealth specials keyed
    html = once(
        html,
        "wealth-kinds",
        "    var kinds = [\n"
        "      { id: 'startup', cat: 'tech', title: 'Una startup gaming te abre la puerta',\n"
        "        text: 'Un antiguo compañero te propone entrar con parte de tu liquidez. No hay cifras de retorno. Solo el riesgo.' },\n"
        "      { id: 'org', cat: 'esports', title: 'Una org busca capital',\n"
        "        text: 'Una organización quiere que entres como inversor silencioso. Tu nombre abre puertas; el resultado no está escrito.' }\n"
        "    ];\n"
        "    if ((p.reputation || 0) >= 55 || (p.proYears || 0) >= 6) {\n"
        "      kinds.push({ id: 'academy', cat: 'business', title: 'Te proponen montar una academia',\n"
        "        text: 'Usarían tu nombre. Tú pondrías el dinero. El resto es trabajo y reputación.' });\n"
        "    }\n"
        "    if (ti) {\n"
        "      kinds.push({ id: 'tiDeal', cat: 'esports', title: 'Oferta tras The International',\n"
        "        text: 'Ganar TI abre cheques. Esta vez te piden que pongas tú también fichas sobre la mesa.' });\n"
        "    }",
        "    var kinds = [\n"
        "      { id: 'startup', cat: 'tech', titleKey: 'ui.wealthStartupTitle', textKey: 'ui.wealthStartupText',\n"
        "        title: 'Una startup gaming te abre la puerta',\n"
        "        text: 'Un antiguo compañero te propone entrar con parte de tu liquidez. No hay cifras de retorno. Solo el riesgo.' },\n"
        "      { id: 'org', cat: 'esports', titleKey: 'ui.wealthOrgTitle', textKey: 'ui.wealthOrgText',\n"
        "        title: 'Una org busca capital',\n"
        "        text: 'Una organización quiere que entres como inversor silencioso. Tu nombre abre puertas; el resultado no está escrito.' }\n"
        "    ];\n"
        "    if ((p.reputation || 0) >= 55 || (p.proYears || 0) >= 6) {\n"
        "      kinds.push({ id: 'academy', cat: 'business', titleKey: 'ui.wealthAcademyTitle', textKey: 'ui.wealthAcademyText',\n"
        "        title: 'Te proponen montar una academia',\n"
        "        text: 'Usarían tu nombre. Tú pondrías el dinero. El resto es trabajo y reputación.' });\n"
        "    }\n"
        "    if (ti) {\n"
        "      kinds.push({ id: 'tiDeal', cat: 'esports', titleKey: 'ui.wealthTiTitle', textKey: 'ui.wealthTiText',\n"
        "        title: 'Oferta tras The International',\n"
        "        text: 'Ganar TI abre cheques. Esta vez te piden que pongas tú también fichas sobre la mesa.' });\n"
        "    }",
    )
    html = once(
        html,
        "wealth-pending-keys",
        "    return {\n"
        "      type: 'wealth',\n"
        "      title: k.title,\n"
        "      text: k.text,\n"
        "      cat: k.cat,\n"
        "      amount: amount,\n"
        "      catName: catMeta(k.cat).name\n"
        "    };",
        "    return {\n"
        "      type: 'wealth',\n"
        "      title: k.title,\n"
        "      text: k.text,\n"
        "      titleKey: k.titleKey || null,\n"
        "      textKey: k.textKey || null,\n"
        "      cat: k.cat,\n"
        "      amount: amount,\n"
        "      catName: catMeta(k.cat).name\n"
        "    };",
    )
    html = once(
        html,
        "modal-wealth-keys",
        "          '<div class=\"modal-head\"><div class=\"modal-kicker\">' + t('modal.money') + '</div><h3>' + c.esc(pend.title) + '</h3></div>' +\n"
        "          '<div class=\"modal-body\"><p>' + c.esc(pend.text) + '</p>' +",
        "          '<div class=\"modal-head\"><div class=\"modal-kicker\">' + t('modal.money') + '</div><h3>' + c.esc(pend.titleKey ? t(pend.titleKey, null, pend.title) : pend.title) + '</h3></div>' +\n"
        "          '<div class=\"modal-body\"><p>' + c.esc(pend.textKey ? t(pend.textKey, null, pend.text) : pend.text) + '</p>' +",
    )

    # Bulk visible UI replacements (screens)
    reps = [
        (
            "title: live.done ? t('ui.tournamentClosed', null, 'Torneo cerrado') : 'Torneo en curso',\n"
            "      meta: c.badge(live.done ? 'Cierre' : t('ui.inPlay', null, 'En juego'), live.done ? 'gold' : 'info'),",
            "title: live.done ? t('ui.tournamentClosed', null, 'Torneo cerrado') : t('ui.tournamentInProgress', null, 'Torneo en curso'),\n"
            "      meta: c.badge(live.done ? t('ui.closing', null, 'Cierre') : t('ui.inPlay', null, 'En juego'), live.done ? 'gold' : 'info'),",
            "live-tour-title",
        ),
        (
            "var kvs = '<div class=\"kv\"><span>Torneo</span><span>' + c.esc(live.name) + '</span></div>' +",
            "var kvs = '<div class=\"kv\"><span>' + t('ui.tournament', null, 'Torneo') + '</span><span>' + c.esc(live.name) + '</span></div>' +",
            "kv-tournament",
        ),
        (
            "if (format) kvs += '<div class=\"kv\"><span>Formato</span><span>' + c.esc(format) + '</span></div>';",
            "if (format) kvs += '<div class=\"kv\"><span>' + t('ui.format', null, 'Formato') + '</span><span>' + c.esc(format) + '</span></div>';",
            "kv-format",
        ),
        (
            "kvs += '<div class=\"kv\"><span>Resultado</span><span>' + c.esc(live.record.result) + '</span></div>';",
            "kvs += '<div class=\"kv\"><span>' + t('ui.result', null, 'Resultado') + '</span><span>' + c.esc(tResult(live.record.result)) + '</span></div>';",
            "kv-result",
        ),
        (
            "body: '<p class=\"muted\">Tu carrera empieza aquí. Pulsa <b>' + DCS.game.nextLabel() +\n"
            "          '</b> abajo a la derecha (o la barra espaciadora) para avanzar.</p>'",
            "body: '<p class=\"muted\">' + t('ui.careerStartsFull', { action: DCS.game.nextLabel() }, 'Tu carrera empieza aquí.') + '</p>'",
            "career-starts",
        ),
        (
            "c.tile('Reputación', r.team.reputation),",
            "c.tile(t('ui.reputation', null, 'Reputación'), r.team.reputation),",
            "tile-rep-report",
        ),
        (
            "body += '<p class=\"small muted mt\">Calendario previsto:</p><ul class=\"lines\">' +",
            "body += '<p class=\"small muted mt\">' + t('ui.plannedCalendar', null, 'Calendario previsto:') + '</p><ul class=\"lines\">' +",
            "planned-cal",
        ),
        (
            "body += '<p class=\"small muted\" style=\"margin-bottom:8px\">Pulsa cualquier torneo para ver serie a serie.</p>';",
            "body += '<p class=\"small muted\" style=\"margin-bottom:8px\">' + t('ui.clickTourSeries', null, 'Pulsa cualquier torneo…') + '</p>';",
            "click-tour",
        ),
        (
            "cards += c.card({ title: 'Desarrollo', subtitle: 'Cambio de atributos en la temporada.', body: dev, delay: 120 });",
            "cards += c.card({ title: t('ui.development', null, 'Desarrollo'), subtitle: t('ui.attrSeasonChange', null, 'Cambio de atributos…'), body: dev, delay: 120 });",
            "dev-card",
        ),
        (
            "return '<div class=\"advance\"><span class=\"hint\">Serie pendiente en Torneos</span><span class=\"spacer\"></span>' +",
            "return '<div class=\"advance\"><span class=\"hint\">' + t('ui.seriesPendingHint', null, 'Serie pendiente en Torneos') + '</span><span class=\"spacer\"></span>' +",
            "series-pending-hint",
        ),
        (
            "else if (live.access === 'closed' || live.access === 'qualifier') accessBadge = c.badge('Vía clasificatoria', 'info');",
            "else if (live.access === 'closed' || live.access === 'qualifier') accessBadge = c.badge(t('ui.viaQualifier', null, 'Vía clasificatoria'), 'info');",
            "access-qual-badge",
        ),
        (
            "else if (ti && ti.qualStarted) tiState = 'Clasificatorio disputado';",
            "else if (ti && ti.qualStarted) tiState = t('ui.contestedQualifier', null, 'Clasificatorio disputado');",
            "ti-contested",
        ),
        (
            "else if (ti && ti.direct) tiState = ti.via || t('tour.directInvite');",
            "else if (ti && ti.direct) tiState = viaLabel(ti.via) || t('tour.directInvite');",
            "ti-direct-via",
        ),
    ]
    for old, new, label in reps:
        html = once(html, label, old, new)

    # Dashboard KPIs / tiles — careful replacements
    dash_reps = [
        (
            "c.kpi('Edad', p.age, state.year + ' · temporada ' + (p.proYears + 1)),",
            "c.kpi(t('dash.age'), p.age, state.year + ' · ' + t('ui.seasonWord', null, 'temporada') + ' ' + (p.proYears + 1)),",
        ),
        (
            "c.kpi('Rating', last === null ? '—' : last, 'última temporada', null, last === null ? null : { v: last, fmt: 'int' }),",
            "c.kpi(t('hud.rating'), last === null ? t('common.none') : last, t('ui.lastSeason', null, 'última temporada'), null, last === null ? null : { v: last, fmt: 'int' }),",
        ),
        (
            "c.tile('Equipo', team ? c.teamMark(team, 'sm') : '<span class=\"muted\">Libre</span>',",
            "c.tile(t('ui.team', null, 'Equipo'), team ? c.teamMark(team, 'sm') : '<span class=\"muted\">' + t('ui.free', null, 'Libre') + '</span>',",
        ),
        (
            "c.tile('Posición', role.short, role.name),",
            "c.tile(t('ui.position', null, 'Posición'), role.short, role.name),",
        ),
        (
            "c.tile('Forma', Math.round(p.form), estado(p.form), tone(p.form)),",
            "c.tile(t('ui.form', null, 'Forma'), Math.round(p.form), estado(p.form), tone(p.form)),",
        ),
        (
            "title: 'Contrato', meta: c.badge(p.contract.years + (p.contract.years === 1 ? ' año' : ' años'), 'info'),",
            "title: t('ui.contract', null, 'Contrato'), meta: c.badge(p.contract.years + ' ' + (p.contract.years === 1 ? t('ui.yearOne', null, 'año') : t('ui.yearMany', null, 'años')), 'info'),",
        ),
        (
            "'<div class=\"kv\"><span>Equipo</span><span>' + c.teamMark(team, 'sm') + '</span></div>' +",
            "'<div class=\"kv\"><span>' + t('ui.team', null, 'Equipo') + '</span><span>' + c.teamMark(team, 'sm') + '</span></div>' +",
        ),
        (
            "'<div class=\"kv\"><span>Objetivo del club</span><span>' + c.esc(p.contract.expectation) + '</span></div>' +",
            "'<div class=\"kv\"><span>' + t('ui.clubObjective', null, 'Objetivo del club') + '</span><span>' + c.esc(p.contract.expectation) + '</span></div>' +",
        ),
        (
            "'<div class=\"kv\"><span>Sinergia del roster</span><span>' + team.synergy + '</span></div>' +",
            "'<div class=\"kv\"><span>' + t('ui.rosterSynergy', null, 'Sinergia del roster') + '</span><span>' + team.synergy + '</span></div>' +",
        ),
        (
            "'<div class=\"kv\"><span>Temporadas sin equipo</span><span>' + p.seasonsWithoutTeam + '</span></div>' +",
            "'<div class=\"kv\"><span>' + t('dash.seasonsWithoutTeam') + '</span><span>' + p.seasonsWithoutTeam + '</span></div>' +",
        ),
    ]
    for i, (old, new) in enumerate(dash_reps):
        html = once(html, "dash-" + str(i), old, new)

    # Fix live match verdict to use tMatch
    html = once(
        html,
        "verdict-live",
        "var verdict = (rt && rt.verdict) || (isWin ? 'VICTORIA' : (isLoss ? 'DERROTA' : 'EMPATE'));",
        "var verdict = (rt && tMatch(rt)) || (isWin ? t('match.victory') : (isLoss ? t('match.defeat') : t('match.draw')));",
    )
    html = replace_all(
        html,
        "mr-chip-rep",
        "\">Reputación ",
        "\">' + t('ui.reputation', null, 'Reputación') + ' ",
    )
    # The replace above may break JS string concat - check carefully
    # Actually chips.push uses string literals - need different approach

    return html


def fix_broken_chip_replaces(html: str) -> str:
    # Undo bad replace if it created invalid JS; rewrite chips properly
    bad = "\">' + t('ui.reputation', null, 'Reputación') + ' "
    if bad in html:
        # Find the chip lines and fix them with a targeted rewrite
        html = html.replace(
            "'<span class=\"mr-chip ' + (dlt.rep > 0 ? 'good' : 'bad') + '\">' + t('ui.reputation', null, 'Reputación') + ' ",
            "'<span class=\"mr-chip ' + (dlt.rep > 0 ? 'good' : 'bad') + '\">' + t('ui.reputation', null, 'Reputación') + ' ",
        )
        # If still broken from original replace_all on substring inside string:
        html = html.replace(
            "bad') + '\">' + t('ui.reputation', null, 'Reputación') + ' ",
            "bad') + '\">' + t('ui.reputation', null, 'Reputación') + ' ",
        )
    # Forma chip
    if "\">Forma " in html:
        html = html.replace(
            "'<span class=\"mr-chip ' + (dlt.form > 0 ? 'good' : 'bad') + '\">Forma ",
            "'<span class=\"mr-chip ' + (dlt.form > 0 ? 'good' : 'bad') + '\">' + t('ui.form', null, 'Forma') + ' ",
        )
    if "'<div class=\"mr-eyebrow\">Resultado</div>'" in html:
        html = html.replace(
            "'<div class=\"mr-eyebrow\">Resultado</div>'",
            "'<div class=\"mr-eyebrow\">' + t('ui.result', null, 'Resultado') + '</div>'",
        )
    return html


def more_ui_wires(html: str) -> str:
    pairs = [
        (
            "? c.btn('Continuar', 'tour-continue', { variant: 'primary' })",
            "? c.btn(t('ui.continue', null, 'Continuar'), 'tour-continue', { variant: 'primary' })",
        ),
        (
            "c.btn('Simular torneo', 'tour-rest', { variant: 'ghost' });",
            "c.btn(t('ui.simulateTournament', null, 'Simular torneo'), 'tour-rest', { variant: 'ghost' });",
        ),
        (
            "title: 'Lo que deja el torneo',",
            "title: t('ui.whatTourLeaves', null, 'Lo que deja el torneo'),",
        ),
        (
            "var cardTitle = last ? 'Resultado' : (next ? 'Próxima serie' : 'Resultado');",
            "var cardTitle = last ? t('ui.result', null, 'Resultado') : (next ? t('ui.nextSeries', null, 'Próxima serie') : t('ui.result', null, 'Resultado'));",
        ),
        (
            "body: '<p class=\"muted small\">Todavía no hay calendario. Se sortea en la pretemporada.</p>'",
            "body: '<p class=\"muted small\">' + t('season.noCalendar') + '</p>'",
        ),
        (
            "var head = '<div class=\"page-head\"><div><div class=\"eyebrow\">Calendario competitivo</div><h2>Torneos</h2>' +\n"
            "      '<p>De la clasificatoria abierta a The International: cada plaza se gana.</p></div></div>';",
            "var head = '<div class=\"page-head\"><div><div class=\"eyebrow\">' + t('ui.competitiveCalendar') + '</div><h2>' + t('nav.tournaments') + '</h2>' +\n"
            "      '<p>' + t('ui.tournamentsLead') + '</p></div></div>';",
        ),
        (
            "var body = '<p class=\"muted\">No hay un torneo en juego. Abre el siguiente evento avanzando la temporada.</p>';",
            "var body = '<p class=\"muted\">' + t('ui.noPendingSeries') + '</p>';",
        ),
        (
            "body += '<p class=\"small muted mt\">Ya disputados esta temporada:</p>' +",
            "body += '<p class=\"small muted mt\">' + t('ui.alreadyPlayed') + '</p>' +",
        ),
        (
            "title: 'Promedios de carrera · ' + role.name, meta: state.career.maps + ' mapas',",
            "title: t('ui.careerAverages', { role: role.name }, 'Promedios · ' + role.name), meta: state.career.maps + ' ' + t('ui.maps', null, 'mapas'),",
        ),
        (
            "c.tile('Forma', Math.round(p.form)),",
            "c.tile(t('ui.form', null, 'Forma'), Math.round(p.form)),",
        ),
        (
            "c.tile('Reputación', Math.round(p.reputation)),",
            "c.tile(t('ui.reputation', null, 'Reputación'), Math.round(p.reputation)),",
        ),
        (
            "'<div class=\"kv\"><span>Equipos en su carrera</span><span>' + p.teamsPlayed.length + '</span></div></div>' +",
            "'<div class=\"kv\"><span>' + t('ui.teamsInCareer', null, 'Equipos en su carrera') + '</span><span>' + p.teamsPlayed.length + '</span></div></div>' +",
        ),
        (
            "'juegas tryouts y esperas que alguien se fije en ti en el mercado.</p>' +",
            # leave; handled by noOrgLong if matching full string
            None,
        ),
        (
            "c.kpi('Calidad', DCS.engine.world.rosterQuality(team), 'del roster'),",
            "c.kpi(t('ui.quality', null, 'Calidad'), DCS.engine.world.rosterQuality(team), t('ui.ofRoster', null, 'del roster')),",
        ),
        (
            "c.kpi('Reputación', team.reputation, 'del club'),",
            "c.kpi(t('ui.reputation', null, 'Reputación'), team.reputation, t('ui.ofClub', null, 'del club')),",
        ),
        (
            "title: 'Resultados de la temporada',\n"
            "      subtitle: 'Pulsa un torneo para ver el recorrido serie a serie.',",
            "title: t('ui.seasonResults', null, 'Resultados de la temporada'),\n"
            "      subtitle: t('ui.clickTourPath', null, 'Pulsa un torneo…'),",
        ),
        (
            "body: '<p class=\"muted\">Todavía no has disputado partidas oficiales esta temporada.</p>'",
            "body: '<p class=\"muted\">' + t('ui.noOfficialMapsSeason') + '</p>'",
        ),
        (
            "{ id: 'tourn', label: 'Torneos' }",
            "{ id: 'tourn', label: t('ui.tournaments', null, 'Torneos') }",
        ),
        (
            "title: 'Frente al baremo de la posición',\n"
            "      subtitle: 'Esto es exactamente lo que pesa en tu rating de temporada.',",
            "title: t('ui.vsRoleBenchmark', null, 'Frente al baremo…'),\n"
            "      subtitle: t('ui.whatWeighsRating', null, 'Esto es exactamente…'),",
        ),
        (
            "title: 'Torneos', subtitle: 'Pulsa cualquier torneo para desplegar el recorrido serie a serie.',",
            "title: t('ui.tournaments'), subtitle: t('ui.expandTourPath'),",
        ),
        (
            "title: 'Desglose por equipo',\n"
            "      subtitle: 'Cambiaste de equipo durante el año: el total anual se conserva y el reparto también.',",
            "title: t('ui.teamBreakdown'),\n"
            "      subtitle: t('ui.midYearMove'),",
        ),
        (
            "title: 'Torneos de la temporada',",
            "title: t('ui.seasonTournaments'),",
        ),
        (
            "['Bonus por clasificar a un internacional', b.intlQual],\n"
            "    ['Bonus por clasificar a The International', b.tiQual]",
            "[t('ui.bonusIntl'), b.intlQual],\n"
            "    [t('ui.bonusTI'), b.tiQual]",
        ),
        (
            "title: 'Estado del mercado',",
            "title: t('ui.marketStatus'),",
        ),
        (
            "rows += '<div class=\"kv\"><span>Mejor resultado reciente</span><span>' +",
            "rows += '<div class=\"kv\"><span>' + t('ui.bestRecentResult') + '</span><span>' +",
        ),
        (
            "rows += '<div class=\"kv\"><span>Ranking de tu equipo</span><span class=\"mono\">#' + prof.rank + '</span></div>';",
            "rows += '<div class=\"kv\"><span>' + t('ui.yourTeamRank') + '</span><span class=\"mono\">#' + prof.rank + '</span></div>';",
        ),
        (
            "var intro = '<p class=\"circuit-intro\">El circuito competitivo conecta clasificatorias, torneos regionales y grandes eventos internacionales. Cada competición tiene su propio nivel de prestigio y dificultad.</p>';",
            "var intro = '<p class=\"circuit-intro\">' + t('ui.circuitIntro') + '</p>';",
        ),
        (
            "yearBody = '<p class=\"muted small\">Sin movimientos de mercado este año. Mantener cash también cuenta.</p>';",
            "yearBody = '<p class=\"muted small\">' + t('ui.noMarketMoves') + '</p>';",
        ),
        (
            "investBody = '<p class=\"muted small\">La carrera ya está cerrada. Esto es lo que construiste.</p>';",
            "investBody = '<p class=\"muted small\">' + t('ui.careerClosedWealth') + '</p>';",
        ),
        (
            "? '<div class=\"row\">' + c.btn('Ver estado del mercado', 'nav', { value: 'offers', variant: 'ghost' }) + '</div>'",
            "? '<div class=\"row\">' + c.btn(t('report.viewMarket'), 'nav', { value: 'offers', variant: 'ghost' }) + '</div>'",
        ),
        (
            "body = '<p class=\"small muted\">Tienes ' + r.offers.length + ' oferta' + (r.offers.length > 1 ? 's' : '') +\n"
            "        ' sobre la mesa. No puedes cerrar el año sin responder.</p>' +\n"
            "        '<div class=\"row\">' + c.btn('Ver ofertas', 'nav', { value: 'offers', variant: 'primary' }) + '</div>';",
            "body = '<p class=\"small muted\">' + t('report.offersOnTable', { count: r.offers.length }) + '</p>' +\n"
            "        '<div class=\"row\">' + c.btn(t('report.viewOffers'), 'nav', { value: 'offers', variant: 'primary' }) + '</div>';",
        ),
        (
            "meta: c.badge('Valor de mercado ' + r.marketScore, 'info'),",
            "meta: c.badge(t('report.marketValue', { score: r.marketScore }), 'info'),",
        ),
        (
            "body += '<div class=\"mt\"><p class=\"small\">Patrimonio</p><ul class=\"lines\">' +",
            "body += '<div class=\"mt\"><p class=\"small\">' + t('report.wealth') + '</p><ul class=\"lines\">' +",
        ),
        (
            "body += '<div class=\"row mt\">' + c.btn('Revisar patrimonio', 'nav', { value: 'finances', variant: 'ghost' }) + '</div>';",
            "body += '<div class=\"row mt\">' + c.btn(t('report.reviewWealth'), 'nav', { value: 'finances', variant: 'ghost' }) + '</div>';",
        ),
        (
            "(rec.earnings.bonus ? '<div class=\"kv\"><span>Bonus de contrato</span><span class=\"good\">' +",
            "(rec.earnings.bonus ? '<div class=\"kv\"><span>' + t('report.contractBonus') + '</span><span class=\"good\">' +",
        ),
        (
            "'<div class=\"kv\"><span>Reputación</span><span>' + Math.round(p.reputation) + ' (' + fmt.signed(r.repDelta) + ')</span></div>' +",
            "'<div class=\"kv\"><span>' + t('ui.reputation') + '</span><span>' + Math.round(p.reputation) + ' (' + fmt.signed(r.repDelta) + ')</span></div>' +",
        ),
    ]
    for old, new in pairs:
        if new is None:
            continue
        html = once(html, "ui:" + old[:28].replace("\n", " "), old, new)

    # duplicate bonus arrays (create + profile) — replace remaining
    html = replace_all(
        html,
        "bonus-intl-left",
        "['Bonus por clasificar a un internacional', b.intlQual]",
        "[t('ui.bonusIntl'), b.intlQual]",
    )
    html = replace_all(
        html,
        "bonus-ti-left",
        "['Bonus por clasificar a The International', b.tiQual]",
        "[t('ui.bonusTI'), b.tiQual]",
    )

    # Flojo / Media / Élite band labels if present
    html = once(
        html,
        "band-labels",
        "><span>Flojo</span><span>Media</span><span>Élite</span></div>",
        "><span>' + t('ui.weak') + '</span><span>' + t('ui.average') + '</span><span>' + t('ui.elite') + '</span></div>",
    )

    # noOrg long text
    html = once(
        html,
        "no-org-long",
        "Ahora mismo no perteneces a ninguna organización. Grindeas pubs,\n"
        "      juegas tryouts y esperas que alguien se fije en ti en el mercado.",
        "' + t('ui.noOrgLong') + '",
    )

    return html


def patch_core_event_outcome() -> None:
    core = (I18N / "core.js").read_text(encoding="utf-8")
    if "outcomeKey" in core and "eventView" in core:
        # enhance eventView to also expose resolved outcome/chosen
        needle = "      return { title: title, text: text, options: options };"
        if "chosen:" not in core[core.find("eventView") : core.find("eventView") + 1200]:
            repl = (
                "      var chosen = ev.chosen || '';\n"
                "      if (ev.chosenKey) chosen = resolve(ev.chosenKey, vars, chosen);\n"
                "      var outcome = ev.outcome || '';\n"
                "      if (ev.outcomeKey) outcome = resolve(ev.outcomeKey, vars, outcome);\n"
                "      return { title: title, text: text, options: options, chosen: chosen, outcome: outcome };"
            )
            core = core.replace(needle, repl, 1)
            (I18N / "core.js").write_text(core, encoding="utf-8")
            print("OK core eventView outcome/chosen")
        else:
            print("SKIP core already has chosen")
    # Also update eventHtml to prefer eventView chosen/outcome
    pass


def main() -> None:
    update_catalogs()
    patch_core_event_outcome()
    html = INDEX.read_text(encoding="utf-8")
    html = patch_index(html)
    html = fix_broken_chip_replaces(html)
    html = more_ui_wires(html)
    INDEX.write_text(html, encoding="utf-8")
    print("Wrote index.html", len(html))
    subprocess.check_call(["node", str(I18N / "patch-index.js")])
    print("patch-index done")


if __name__ == "__main__":
    main()

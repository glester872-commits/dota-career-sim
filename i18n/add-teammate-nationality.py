#!/usr/bin/env python3
"""Add teammate countryCode + flag/name UI (ES/EN)."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "i18n"
INDEX = ROOT / "index.html"

COUNTRIES_ES = json.loads(Path("/tmp/countries_es.json").read_text(encoding="utf-8"))
COUNTRIES_EN = json.loads(Path("/tmp/countries_en.json").read_text(encoding="utf-8"))


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


def main() -> None:
    es, en = load_cat(I18N / "es.js"), load_cat(I18N / "en.js")
    es["countries"] = COUNTRIES_ES
    en["countries"] = COUNTRIES_EN
    es.setdefault("ui", {})["nationality"] = "Nacionalidad"
    en.setdefault("ui", {})["nationality"] = "Nationality"
    es["ui"]["you"] = "Tú"
    en["ui"]["you"] = "You"
    write_cat(I18N / "es.js", "es", es)
    write_cat(I18N / "en.js", "en", en)
    print("catalogs: countries", len(COUNTRIES_ES))

    # --- core.js: country helper ---
    core = (I18N / "core.js").read_text(encoding="utf-8")
    if "country: function" not in core:
        needle = "    stageKey: stageKey,\n    resultKey: resultKey,"
        insert = (
            "    /** Localized country name from ISO 3166-1 alpha-2. */\n"
            "    country: function (code) {\n"
            "      if (!code || code === 'XX' || code === 'UNKNOWN') {\n"
            "        return resolve('countries.UNKNOWN', null, 'Desconocida');\n"
            "      }\n"
            "      var k = String(code).toUpperCase();\n"
            "      return resolve('countries.' + k, null, k);\n"
            "    },\n\n"
            "    stageKey: stageKey,\n"
            "    resultKey: resultKey,"
        )
        if needle not in core:
            raise SystemExit("core needle missing")
        core = core.replace(needle, insert, 1)
        (I18N / "core.js").write_text(core, encoding="utf-8")
        print("OK core country()")
    else:
        print("SKIP core country already")

    html = INDEX.read_text(encoding="utf-8")

    # --- CSS ---
    css = """
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
  background: repeating-linear-gradient(
    -45deg, #2a3140, #2a3140 3px, #1a1f2a 3px, #1a1f2a 6px
  );
  border: 1px solid rgba(255,255,255,.14);
}
.flag-sm, .flag-lg { object-fit: contain; }
@media (max-width: 720px) {
  .mate-line .mate-country { display: none; }
}
"""
    if "DCS_MATE_NAT_CSS" not in html:
        html = html.replace("</style>", css + "\n</style>", 1)
        print("OK css")
    else:
        print("SKIP css")

    # --- Expand NAT_ISO module ---
    old_nat_end = """  function flagFor(name) {
    var iso = NAT_ISO[name];
    if (!iso || iso.length !== 2) return '🏳️';
    var a = iso.toUpperCase().charCodeAt(0) - 65;
    var b = iso.toUpperCase().charCodeAt(1) - 65;
    return String.fromCodePoint(0x1F1E6 + a, 0x1F1E6 + b);
  }

  function flagMark(name, size) {
    var iso = NAT_ISO[name];
    var lg = size === 'lg';
    if (!iso || iso.length !== 2) {
      return '<span class="flag-fallback">' + flagFor(name) + '</span>';
    }
    return '<img class="' + (lg ? 'flag-lg' : 'flag-sm') + '" alt="" width="' + (lg ? 40 : 22) +
      '" height="' + (lg ? 28 : 15) + '" src="https://flagcdn.com/w40/' + iso.toLowerCase() + '.png">';
  }

  DCS.data = DCS.data || {};
  DCS.data.NAT_ISO = NAT_ISO;
  DCS.data.flagFor = flagFor;
  DCS.data.flagMark = flagMark;
})(window.DCS = window.DCS || {});"""

    new_nat_end = r"""  var ISO_NAT = {};
  Object.keys(NAT_ISO).forEach(function (n) { ISO_NAT[NAT_ISO[n]] = n; });

  function codeFromNationality(name) {
    if (!name) return null;
    if (/^[A-Za-z]{2}$/.test(name)) return name.toUpperCase();
    return NAT_ISO[name] || null;
  }

  function countryLabel(code) {
    if (DCS.i18n && DCS.i18n.country) return DCS.i18n.country(code);
    if (!code) return 'Desconocida';
    return ISO_NAT[String(code).toUpperCase()] || String(code).toUpperCase();
  }

  function flagFor(nameOrCode) {
    var iso = codeFromNationality(nameOrCode) || nameOrCode;
    if (!iso || String(iso).length !== 2) return '🏳️';
    iso = String(iso).toUpperCase();
    var a = iso.charCodeAt(0) - 65;
    var b = iso.charCodeAt(1) - 65;
    if (a < 0 || a > 25 || b < 0 || b > 25) return '🏳️';
    return String.fromCodePoint(0x1F1E6 + a, 0x1F1E6 + b);
  }

  function escAttr(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/"/g, '&quot;')
      .replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  /** Official flag image from ISO code (or Spanish nationality name). */
  function flagMark(nameOrCode, size) {
    var iso = codeFromNationality(nameOrCode);
    var lg = size === 'lg';
    var label = countryLabel(iso);
    var w = lg ? 40 : 22;
    var h = lg ? 28 : 15;
    var cls = lg ? 'flag-lg' : 'flag-sm';
    if (!iso || iso.length !== 2) {
      return '<span class="flag-neutral ' + cls + '" role="img" aria-label="' +
        escAttr(label) + '" title="' + escAttr(label) + '"></span>';
    }
    return '<img class="' + cls + '" alt="' + escAttr(label) + '" title="' + escAttr(label) +
      '" width="' + w + '" height="' + h +
      '" src="https://flagcdn.com/w40/' + iso.toLowerCase() + '.png" loading="lazy" decoding="async">';
  }

  function flagByCode(code, size) {
    return flagMark(code, size);
  }

  /** Ensure regions expose countryCodes derived from nationality pools. */
  function wireRegionCountryCodes() {
    var regions = DCS.data && DCS.data.REGIONS;
    if (!regions) return;
    Object.keys(regions).forEach(function (id) {
      var r = regions[id];
      if (!r || r.countryCodes) return;
      r.countryCodes = (r.nationalities || []).map(function (n) {
        return NAT_ISO[n];
      }).filter(Boolean);
    });
  }
  wireRegionCountryCodes();

  DCS.data = DCS.data || {};
  DCS.data.NAT_ISO = NAT_ISO;
  DCS.data.ISO_NAT = ISO_NAT;
  DCS.data.codeFromNationality = codeFromNationality;
  DCS.data.countryLabel = countryLabel;
  DCS.data.flagFor = flagFor;
  DCS.data.flagMark = flagMark;
  DCS.data.flagByCode = flagByCode;
})(window.DCS = window.DCS || {});"""

    html = once(html, "nat-module", old_nat_end, new_nat_end)

    # --- makeNpc ---
    html = once(
        html,
        "makeNpc",
        """  function makeNpc(rng, world, region, role, quality) {
    var age = U.clamp(rng.gaussInt(24, 4), 17, 35);
    var rating = U.clamp(Math.round(rng.gauss(quality, 4.5)), 15, 97);
    return {
      id: 'n' + (world.nextId++),
      nick: genNick(rng, world.usedNicks),
      name: genRealName(rng, region),
      role: role,
      age: age,
      rating: rating,
      isPlayer: false
    };
  }""",
        """  function pickCountryCode(rng, region) {
    var reg = D.REGIONS[region];
    var codes = (reg && reg.countryCodes) || [];
    if (!codes.length && reg && reg.nationalities && DCS.data.NAT_ISO) {
      codes = reg.nationalities.map(function (n) { return DCS.data.NAT_ISO[n]; }).filter(Boolean);
    }
    if (!codes.length) return null;
    return rng.pick(codes);
  }

  function makeNpc(rng, world, region, role, quality) {
    var age = U.clamp(rng.gaussInt(24, 4), 17, 35);
    var rating = U.clamp(Math.round(rng.gauss(quality, 4.5)), 15, 97);
    return {
      id: 'n' + (world.nextId++),
      nick: genNick(rng, world.usedNicks),
      name: genRealName(rng, region),
      role: role,
      age: age,
      rating: rating,
      countryCode: pickCountryCode(rng, region),
      isPlayer: false
    };
  }""",
    )

    # --- joinTeam: include countryCode ---
    html = once(
        html,
        "joinTeam-cc",
        "    team.roster[idx] = { id: 'you', nick: p.nick, name: p.name, role: p.role, age: p.age, rating: p.overall, isPlayer: true };",
        "    team.roster[idx] = {\n"
        "      id: 'you', nick: p.nick, name: p.name, role: p.role, age: p.age, rating: p.overall, isPlayer: true,\n"
        "      countryCode: (DCS.data.codeFromNationality && DCS.data.codeFromNationality(p.nationality)) || null\n"
        "    };",
    )

    # Export pickCountryCode / ensure on world engine
    html = once(
        html,
        "export-makeNpc",
        "    makeNpc: makeNpc,",
        "    makeNpc: makeNpc,\n    pickCountryCode: pickCountryCode,\n    ensureRosterCountries: ensureRosterCountries,",
    )

    # Add ensureRosterCountries before joinTeam
    html = once(
        html,
        "ensureRosterCountries-fn",
        "  function joinTeam(state, team, contract) {",
        """  /** Backfill countryCode on NPC rosters (stable per id; never from display name alone). */
  function ensureRosterCountries(state) {
    if (!state || !state.world || !state.world.teams) return;
    state.world.teams.forEach(function (team) {
      if (!team || !team.roster) return;
      var codes = (D.REGIONS[team.region] && D.REGIONS[team.region].countryCodes) || [];
      if (!codes.length && D.REGIONS[team.region] && D.REGIONS[team.region].nationalities && DCS.data.NAT_ISO) {
        codes = D.REGIONS[team.region].nationalities.map(function (n) {
          return DCS.data.NAT_ISO[n];
        }).filter(Boolean);
      }
      team.roster.forEach(function (m) {
        if (!m) return;
        if (m.isPlayer) {
          if (!m.countryCode && state.player) {
            m.countryCode = (DCS.data.codeFromNationality &&
              DCS.data.codeFromNationality(state.player.nationality)) || null;
          }
          return;
        }
        if (m.countryCode) return;
        if (!codes.length) { m.countryCode = null; return; }
        var h = 0;
        var sid = String(m.id || m.nick || '');
        for (var i = 0; i < sid.length; i++) h = ((h << 5) - h + sid.charCodeAt(i)) | 0;
        m.countryCode = codes[Math.abs(h) % codes.length];
      });
    });
  }

  function joinTeam(state, team, contract) {""",
    )

    # migrate hook
    html = once(
        html,
        "migrate-roster-cc",
        "    injectMissingCatalogTeams(state);\n    migrateContractTerms(state);",
        "    injectMissingCatalogTeams(state);\n"
        "    if (DCS.engine.world && DCS.engine.world.ensureRosterCountries) {\n"
        "      DCS.engine.world.ensureRosterCountries(state);\n"
        "    }\n"
        "    migrateContractTerms(state);",
    )

    # --- UI helper mateLine ---
    html = once(
        html,
        "ui-mateLine",
        "  DCS.ui.c = {\n"
        "    esc: esc, cls: cls, card: card,\n"
        "    tile: tile, tiles: tiles, kpi: kpi, kpis: kpis,\n"
        "    bar: bar, attrRow: attrRow, statBar: statBar, statBars: statBars,\n"
        "    badge: badge, tierBadge: tierBadge, posChip: posChip, posChipFull: posChipFull,\n"
        "    ratingChip: ratingChip, ratingBand: ratingBand,\n"
        "    tabs: tabs, table: table, btn: btn, empty: empty,\n"
        "    statGrid: statGrid, resultRow: resultRow, seriesList: seriesList,\n"
        "    levelBadge: levelBadge, prizeBreakdown: prizeBreakdown,\n"
        "    toneClass: toneClass, teamMark: teamMark\n"
        "  };",
        """  /** Flag + optional localized country for a roster member. */
  function mateNat(m, opts) {
    opts = opts || {};
    var code = m && m.countryCode;
    if (!code && m && m.isPlayer && DCS.game && DCS.game.state && DCS.game.state.player) {
      code = DCS.data.codeFromNationality &&
        DCS.data.codeFromNationality(DCS.game.state.player.nationality);
    }
    var label = DCS.data.countryLabel ? DCS.data.countryLabel(code) : (code || '');
    var flag = DCS.data.flagByCode
      ? DCS.data.flagByCode(code, opts.size || 'sm')
      : (DCS.data.flagMark ? DCS.data.flagMark(code) : '');
    var showName = opts.showName !== false;
    return '<span class="mate-nat" title="' + esc(label) + '">' + flag + '</span>' +
      (showName ? '<span class="mate-country">— ' + esc(label) + '</span>' : '');
  }

  function mateLine(m, opts) {
    opts = opts || {};
    if (!m) return '';
    var nick = m.isPlayer
      ? '<span class="nick">' + esc(m.nick) + '</span>'
      : esc(m.nick);
    return '<span class="mate-line">' +
      mateNat(m, { showName: opts.showCountry !== false, size: 'sm' }) +
      '<span class="mate-nick">' + nick + '</span></span>';
  }

  DCS.ui.c = {
    esc: esc, cls: cls, card: card,
    tile: tile, tiles: tiles, kpi: kpi, kpis: kpis,
    bar: bar, attrRow: attrRow, statBar: statBar, statBars: statBars,
    badge: badge, tierBadge: tierBadge, posChip: posChip, posChipFull: posChipFull,
    ratingChip: ratingChip, ratingBand: ratingBand,
    tabs: tabs, table: table, btn: btn, empty: empty,
    statGrid: statGrid, resultRow: resultRow, seriesList: seriesList,
    levelBadge: levelBadge, prizeBreakdown: prizeBreakdown,
    toneClass: toneClass, teamMark: teamMark,
    mateNat: mateNat, mateLine: mateLine
  };""",
    )

    # --- Team roster rows ---
    html = once(
        html,
        "team-roster-rows",
        """    var rows = team.roster.map(function (m) {
      return {
        attrs: m.isPlayer ? 'class="you"' : '',
        cells: [
          (m.isPlayer ? '<span class="nick">' + c.esc(m.nick) + '</span>' : c.esc(m.nick)),
          c.posChip(m.role),
          '<span class="mono">' + m.rating + '</span>',
          m.age + '',
          m.isPlayer ? '<span class="muted">Tú</span>' : c.esc(m.name)
        ]
      };
    });""",
        """    var rows = team.roster.map(function (m) {
      return {
        attrs: m.isPlayer ? 'class="you"' : '',
        cells: [
          c.mateLine(m),
          c.posChip(m.role),
          '<span class="mono">' + m.rating + '</span>',
          m.age + '',
          m.isPlayer
            ? '<span class="muted">' + t('ui.you', null, 'Tú') + '</span>'
            : c.esc(m.name)
        ]
      };
    });""",
    )

    # Create screen: localize country labels via ISO while keeping Spanish value
    html = once(
        html,
        "create-nat-label",
        """      return '<button type="button" class="nat-item' + (draft.nationality === n ? ' sel' : '') +
        '" data-action="set-nat" data-value="' + c.esc(n) + '">' +
        '<span class="nat-flag">' + D.flagMark(n) + '</span><span>' + c.esc(n) + '</span></button>';""",
        """      var natCode = D.codeFromNationality ? D.codeFromNationality(n) : null;
      var natLabel = D.countryLabel ? D.countryLabel(natCode) : n;
      return '<button type="button" class="nat-item' + (draft.nationality === n ? ' sel' : '') +
        '" data-action="set-nat" data-value="' + c.esc(n) + '">' +
        '<span class="nat-flag">' + D.flagMark(n) + '</span><span>' + c.esc(natLabel) + '</span></button>';""",
    )

    # Dashboard / legacy player nationality localized
    html = once(
        html,
        "dash-player-nat",
        "'<div class=\"sub\">' + c.esc(p.name) + ' · ' + c.esc(p.nationality) + ' · ' +",
        "'<div class=\"sub\">' + c.esc(p.name) + ' · ' + c.esc((D.countryLabel && D.countryLabel(D.codeFromNationality && D.codeFromNationality(p.nationality))) || p.nationality) + ' · ' +",
    )

    # There may be two similar lines (dash + legacy)
    html = html.replace(
        "'<div class=\"muted small\">' + c.esc(p.name) + ' · ' + c.esc(p.nationality) + ' · ' +",
        "'<div class=\"muted small\">' + c.esc(p.name) + ' · ' + c.esc((D.countryLabel && D.countryLabel(D.codeFromNationality && D.codeFromNationality(p.nationality))) || p.nationality) + ' · ' +",
        1,
    )
    print("OK legacy-player-nat (replace)")

    # Create card title uses nationality - localize display
    html = once(
        html,
        "pcard-flag-title",
        "'<div class=\"pcard-flag\" title=\"' + c.esc(draft.nationality) + '\">' + flag + '</div>' +",
        "'<div class=\"pcard-flag\" title=\"' + c.esc((D.countryLabel && D.countryLabel(D.codeFromNationality && D.codeFromNationality(draft.nationality))) || draft.nationality) + '\">' + flag + '</div>' +",
    )

    INDEX.write_text(html, encoding="utf-8")
    subprocess.check_call(["node", str(I18N / "patch-index.js")], stdout=subprocess.DEVNULL)
    print("patched + synced", INDEX.stat().st_size)


if __name__ == "__main__":
    main()

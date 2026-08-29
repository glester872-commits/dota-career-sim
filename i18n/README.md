# i18n — DOTA 2 Career Sim

Lightweight localization (no i18next). Default language: **Español**.

## Layout

- `core.js` — `DCS.i18n` + `DCS.t` (interpolation, plurals, stage/result/match helpers, event view)
- `es.js` / `en.js` — catalogs registered via `DCS.i18n.register`
- Catalogs are **embedded** into `index.html` for GitHub Pages (single-file upload safe)
- `patch-index.js` — reinjects catalogs into `index.html`

## Usage

```js
DCS.t('home.newCareer')
DCS.i18n.setLang('en') // re-renders UI; persists to localStorage `dcs.lang`
DCS.i18n.eventView(eventInstance) // title/text/options from keys + vars
```

## Adding a language

1. Copy `en.js` → `pt.js` (etc.), change `register("pt", …)`
2. Translate leaf strings
3. Run `node i18n/patch-index.js` (or reinject scripts)
4. Add code to `SUPPORTED` via register (automatic)

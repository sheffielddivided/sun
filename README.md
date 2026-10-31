# Solflekker – data, historie og hva dataene sier om sol og jord

Statisk nettsted på norsk bokmål om solflekker og solsyklusen. All data hentes fra åpne kilder (SILSO, NOAA SWPC, GFZ, NASA, Met Office, Oulu, Smithsonian GVP m.fl.), analyseres automatisk (surrogattester, korreksjon for autokorrelasjon og multiple tester) og vises med evidensmerking (godt etablert / omdiskutert / uten støtte).

**Nettsted:** https://sheffielddivided.github.io/sun/

## Arkitektur

```
pipeline/            Python 3.12: én modul per kilde (sources/), analyser (analysis/), tester (tests/ med ekte fixtures)
public/data/         Genererte JSON-filer + manifest.json (kilde, URL, tidspunkt, siste datapunkt, rader, status)
src/                 Vite + TypeScript, Observable Plot; grafer i src/charts/, felles kode i src/lib/
content/nb/          Tekster (Markdown), UI-tekster (ui.json), tidslinje (timeline.json); content/svg/: illustrasjoner
scripts/gen-pages.mjs  Bygger HTML-sider fra Markdown, binder tall fra JSON ({{sti|format}})
tests/               Playwright-røyktest
.github/workflows/   deploy, update-daily/-monthly/-yearly (+ _update, ci)
```

Pipeline: `fetch → parse → validate → build JSON` per kilde. Feiler en kilde, beholdes siste gode versjon, markeres «stale» i manifestet, og de andre kjører videre. Analyser kjøres etterpå (`analysis_*.json`).

## Kjøre lokalt

```bash
make install      # pip install -r requirements.txt && npm ci
make data         # hent alle data + kjør analyser (GROUP=daily|monthly|yearly|all)
make dev          # utviklingsserver (genererer sider først)
make test         # pytest + typecheck + lint
make build        # typecheck + produksjonsbygg til dist/
make e2e          # Playwright (CHROMIUM_PATH kan peke på lokal Chromium)
make lighthouse   # Lighthouse mot forsiden
```

## Oppdateringsplan

| Workflow | Tid | Innhold |
|---|---|---|
| `update-daily.yml` | daglig 06:00 UTC | daglig solflekktall + EISN, F10.7, Kp, prognose |
| `update-monthly.yml` | den 2. hver måned | månedlige serier, temperatur, kosmisk stråling, NAO/ENSO, TSI, Kp-historikk, **alle analyser** |
| `update-yearly.yml` | 15. januar | vulkandatabasen, IVI2, gruppetall, sommerfugldata + analyser |
| `deploy.yml` | push til `main` | bygg og publiser til GitHub Pages |

Alle kan startes manuelt (workflow_dispatch). Data committes bare hvis innholdet har endret seg.

## Legge til en ny datakilde

1. Lag `pipeline/sources/<navn>.py` med `SOURCE = Source(...)` (eller `SOURCES = [...]`): `fetch()` (bytes, bruk `http_get` og `ensure_not_html`), `parse()` (tåler små formatendringer, kast `ValidationError` ved feil), `build()` → `({filnavn: json}, {"rows", "last_point"})`, samt lisens, kildehenvisning, frekvens og kjente svakheter.
2. Legg modulnavnet i `MODULES` i `pipeline/sources/__init__.py`.
3. Lagre et ekte utdrag i `pipeline/tests/fixtures/` og skriv en parser-test.
4. Vis dataene: legg til en graf i `src/charts/` og registrer den i `registry.ts`; bruk `:::chart <id>` i en Markdown-side. Kilden dukker automatisk opp på «Metode og kilder».

## Engelsk versjon

Kopier `content/nb/` til `content/en/`, oversett, og bygg med `SITE_LANG=en VITE_LANG=en npm run build`. Tekster ligger ikke i komponentene.

## Kvalitetssikring

- `pytest`: parsere (ekte filutdrag), statistikk, surrogattest uten falske positive på tilfeldige data, syklusdeteksjon, vulkan-nulltest, kjerne (stale/feil).
- ESLint + Prettier + `tsc`; Playwright røyktest (alle sider, alle grafer uten konsollfeil, tema, CSV, periodevalg).
- Lighthouse (forsiden, mobilprofil, lokalt 2026-10-31): Performance 99, Accessibility 96, Best Practices 100, SEO 100.

## Manuelle steg

Kode og workflows er pushet til `main`. Pages-aktivering og første vellykkede deploy kunne ikke verifiseres fra byggemiljøet (`gh` hadde ugyldig token, og MCP-verktøyene kan ikke endre Pages-innstillinger). Gjør dette én gang:

1. GitHub → repoet **sheffielddivided/sun** → **Settings → Pages → Build and deployment → Source: «GitHub Actions»**.
2. **Settings → Actions → General → Workflow permissions: «Read and write permissions»** (kreves for at oppdateringsworkflows kan committe data), og huk av «Allow GitHub Actions to create and approve pull requests» er *ikke* nødvendig.
3. **Actions → Deploy → Run workflow** (branch `main`). Siden publiseres på https://sheffielddivided.github.io/sun/.
4. Kjør deretter **Oppdater månedlig** manuelt én gang (Actions → Run workflow) for å teste hele kjeden: hent → valider → analyser → commit → deploy.
5. Hvis depotet er privat og planen ikke støtter Pages for private depoter, må depotet gjøres offentlig eller planen oppgraderes.

## Lisens

Kode: MIT (`LICENSE`). Data følger kildenes lisenser og krav til kildehenvisning – se `public/data/manifest.json` og siden «Metode og kilder».

# PLAN – Solflekker-nettsted

Sjekklisten oppdateres underveis. `[x]` = ferdig og verifisert.

## Fase 0 – Rekognosering av kilder
- [x] Hver URL lastet ned og format lest (se DECISIONS.md for funn og reserveløsninger)

## Fase 1 – Prosjektskjelett
- [x] Git-branch, mappestruktur
- [ ] `Makefile`, `requirements.txt`, `package.json`, Vite/TS/ESLint/Prettier-konfig
- [ ] `.gitignore`, `LICENSE` (MIT)

## Fase 2 – Datapipeline (`pipeline/`)
- [ ] Felles kjerne: nedlasting med retry, JSON-skriving, manifest, validering, «behold siste gode versjon»
- [ ] Kilder (én modul hver): SILSO, NOAA SWPC, GFZ Kp, TSI (NOAA NCEI NNL + LASP TSIS-1), GISTEMP + HadCRUT5, kosmisk stråling (Oulu Φ), NAO/ONI (CPC), GVP-vulkaner + IVI2, sommerfugldata (RGO/NASA MSFC)
- [ ] Syklusdeteksjon (start, maks, lengde)
- [ ] Statistikk: effektive frihetsgrader, fase-surrogater, lag-skanning med multippel-testkorreksjon
- [ ] Analyser: TSI, temperatur, kosmisk stråling, geomagnetisk, Maunder/vulkan-kontekst, NAO/ENSO, vulkan (superposed epoch + permutasjon), spuriøse korrelasjoner
- [ ] pytest: parsere (fixtures fra ekte filer), statistikk, falsk-positiv-test for surrogater

## Fase 3 – Frontend (`src/`, `content/`)
- [ ] Sidegenerator (Markdown → HTML, verdibinding fra JSON), layout, tema (lys/mørk), WCAG AA
- [ ] Grafer (Observable Plot) med tabell-alternativ og CSV-nedlasting
- [ ] Sider: forside, hva er solflekker, historien (tidslinje), data, sol-og-jord (8 undersider), metode og kilder
- [ ] SVG-illustrasjoner
- [ ] Evidensmerking (tre nivåer)

## Fase 4 – QA
- [ ] Lint, typecheck, pytest, build
- [ ] Playwright-røyktest
- [ ] Lighthouse (lokalt)
- [ ] Faktagjennomgang av alle tekster

## Fase 5 – Automatisering og publisering
- [ ] Workflows: deploy, update-daily, update-monthly, update-yearly
- [ ] Push, Pages-aktivering, kjør workflows, verifiser
- [ ] README (inkl. «Manuelle steg»), DECISIONS.md, sluttrapport

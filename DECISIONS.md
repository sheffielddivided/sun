# Beslutninger

Format: **beslutning** – alternativer – begrunnelse. Datoer er byggedato 2026-10-31.

## Datakilder (verifisert ved nedlasting)

1. **SILSO-URL-er: `/silso/DATA/*.csv`.** De gamle `/SILSO/INFO/snchrono/…`-URL-ene gir 404; `INFO/*.php`-endepunktene fungerer også, men `/silso/DATA/` er stabile filer. Daglig EISN fra `DATA/EISN/EISN_current.csv`.
2. **Gruppesolflekktall: backbone (GNbb2) og Hoyt & Schatten (GNhs), ikke bare én.** Forfatterne er uenige om langtidsnivået (SILSOs egen note); viser begge. Active-days- og Cliver–Ling-seriene utelatt for å holde siden enkel.
3. **Oulu nøytronmonitor: Oulus publiserte modulasjonspotensial Φ (`phi/Phi_mon.txt`) i stedet for råtellerater.** Oulus spørre-CGI (`onlinequery.cgi`) ga HTTP 500 for alle gyldige parametre; NMDB (`nest.nmdb.eu`) ga 401. Et forsøk med forfalskede nettleser-headere ble ikke gjort (omgåelse av tilgangskontroll). Φ er avledet fra nøytronmonitorer (Usoskin m.fl.) og dekker 1936–forrige år. Dokumentert i manifest og på kildesiden.
4. **TSI: NOAA CDR NNLTSI (modell, 1610–) + LASP TSIS-1 (måling, 2018–).** PMOD-sidens data er ikke maskinlesbare (HTML), og LISIRD «composite_tsi» finnes ikke (404). NetCDF4 leses med `h5py` (avvik fra «pandas/numpy/scipy/requests»-listen; nødvendig for HDF5).
5. **Vulkaner: GVP WFS (`webservices.volcano.si.edu/geoserver`) i stedet for volcano.si.edu.** Nettsiden svarte «temporarily unavailable»; WFS gir samme data som GeoJSON. Filtrert til VEI ≥ 3 og år ≥ 1500 på serversiden.
6. **Vulkansk forcing: IVI2 (Gao m.fl. 2008) fra NOAA NCEI i stedet for NASA GISS.** GISS’ tau-fil ga 404 på den gamle URL-en. IVI2 dekker bare til 2000, så den brukes kun i Maunder-/historisk kontekst.
7. **Sommerfugldiagram: Hathaway/NASA MSFC `bflydata.txt`.** Åpen og pålitelig; breddeorienteringen (bin 0 = sør) ble verifisert mot Hathaways nord-/sør-månedsfiler.
8. **Kp siste 30 dager: GFZ nowcast, reserve NOAA (7 dager). Kp-historikk: GFZ `Kp_ap_since_1932.txt`** (gammel datapub-URL gir 404). F10.7 siste 30 dager: NOAA `daily-solar-indices.txt` (JSON-endepunktet har uregelmessige flere målinger per dag).
9. **ONI-sesonger tilordnes midtmåneden** (DJF→januar … NDJ→desember). NAO fra den enkle `.ascii`-filen.
10. **Temperatur: begge serier omregnet til referanseperiode 1961–1990** for sammenligning; HadCRUT5-URL prøver nyere versjonsnummer først.

## Arkitektur

11. **Flersidet statisk nettsted (Vite MPA) med sider generert fra Markdown av `scripts/gen-pages.mjs`.** Alternativer: SPA med hash-ruting (dårligere tilgjengelighet/URL-er), Astro/Next (tungt rammeverk, forbudt). Genererte HTML-filer ligger i `.gitignore` og bygges i `predev`/`prebuild`.
12. **Dataavhengige tall i tekst bindes ved bygging (`{{sti|format}}`)** fra JSON; manglende sti gir byggefeil. Betingede avsnitt (`:::when`) sørger for at konklusjoner ikke blir stående feil hvis fremtidige data endrer resultatet.
13. **Språk: alle tekster i `content/nb/` (inkl. `ui.json`, `timeline.json`).** Engelsk versjon: kopier mappen til `content/en/` og bygg med `SITE_LANG=en VITE_LANG=en`.
14. **Observable Plot uten tungt rammeverk; hver graf lastes i egen chunk og først når den nærmer seg skjermen.** Alle grafer har tekstalternativ, tabell og CSV (med kildehenvisning i kommentarlinjer). Periodevalg (fra/til + knapper) i stedet for drag-zoom, fordi det er tastaturvennlig.
15. **Basesti `/sun/`** (depotnavnet) via `VITE_BASE`; settes automatisk i Actions fra depotnavnet.
16. **Python 3.12 i CI**; lokalt fungerer 3.13.
17. **`manifest.json` oppdaterer `fetched_at` bare når innholdet endres**, slik at workflows ikke lager tomme commits. «Sist endret» ≠ «sist sjekket».
18. **Én kilde som feiler → siste gode versjon beholdes, status «stale»; bygget feiler aldri.** Validering: skjema/parsing, plausible verdiområder, radantall ≥ 90 % av forrige (unntatt rullerende 30-dagersserier).

## Analyse

19. **Effektive frihetsgrader etter Bretherton m.fl. (1999); fase-surrogater av solflekkserien; Holm-korreksjon + familievis p fra maks-|r|-fordelingen.** Alternativ: Monte Carlo med AR(1)-modell (antar for mye struktur).
20. **Temperatur trendfjernes med andregrads polynom før lag-skanning** (surrogattesten forutsetter stasjonaritet). Simuleringen viser at surrogattesten *ikke* er perfekt for to uavhengige trender (20 % falske positive) – dette er opplyst på nettstedet.
21. **Årlige data for temperatur, kosmisk stråling, regionale mønstre og stormdøgn** (færre autokorrelasjonsproblemer enn månedlige). Lag: 0–10 (temperatur), −2…+3 (Φ), 0–4 (geomagnetisk), 0–5 (NAO/ONI).
22. **Vulkaner: primærscenarier valgt før kjøring (A: VEI≥4 1850–2019; B: VEI≥5 1755–2019)** ut fra stabilitet i antall per 50 år. Nullhypotese: sirkulært skiftet utbruddsrekke (bevarer klynging og registreringstrend). Seks primærtester Holm-justert; fire følsomhetsscenarier. Avsluttes 2019 (kun fullførte sykluser). Tambora registreres i GVP med start 1812 (episode til 1815): scenario F bruker bare presise startdatoer; GVP-data ellers uendret.
23. **Ingen skydata → ingen direkte test av Svensmark-hypotesen**; siden sier det eksplisitt og tester kun hva som kan testes (Φ mot SSN/temperatur).
24. **Evidensnivåer A/B/C er vurderinger** (litteratur + egne tester); merket med ikon + tekst + farge.
25. **Referanser:** bare artikler jeg er sikker på finnes (full bibliografisk info). Uvisse detaljer (f.eks. tittelens årsintervall) er utelatt eller kontrollert.
26. **Jordskjelv, børs og helse er ikke testet** (ingen data hentet); siden skiller tydelig mellom testet og ikke-testet.

## Publisering

27. **Hovedgren `main` fikk koden ved fast-forward fra `claude/sunspots-site`.** Pages-kilde = GitHub Actions (se README «Manuelle steg» for det som evt. krever klikk).
28. **Reusable workflow `_update.yml`** brukes av de tre tidsplanlagte workflows; commit med `GITHUB_TOKEN` utløser ikke `deploy.yml`, så deploy kalles eksplisitt etter vellykket datacommit.

## Svensmark-test (lagt til senere)

29. **Skydata: ISCCP-H månedlige 1°-filer fra NOAA NCEI (1983–2017, lavt/midt/høyt via IR-topptrykk).** Vurdert og forkastet: PATMOS-x (daglige filer, svært store), CM SAF CLARA (krever bestilling), NCEP-reanalyse (modell, ikke måling; nedlasting blokkert), CERES/MODIS (ikke tilgjengelig herfra). ISCCP er avsluttet, så kilden har gruppe `static` og kjøres bare med `python -m pipeline.run --only isccp`; råfilene (≈1,7 GB) bufres i `pipeline/.cache/` (ikke i git), og bare breddebånd-aggregater (areavektet) lagres i `cloud_isccp_monthly.json`.
30. **Hypotesen testes som positiv korrelasjon mellom −Φ og lavt skydekke** (årlige anomalier, lineært trendfjernet pga. kjente ISCCP-artefakter). 6 serier × 4 forsinkelser (−1…2 år) = 24 tester med Holm over alle, pluss delperioder (1984–2000, 2001–2016) og en styrkeberegning. Delperiodene er et «utforskende» tillegg og er ikke del av Holm-familien.

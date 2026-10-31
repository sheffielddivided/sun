---
route: /sol-og-jord/kosmisk-straling/
title: Kosmisk stråling og Svensmark-hypotesen
nav: sol-og-jord
slug: kosmisk
parent: sol-og-jord
order: 3
evidence: b
description: Hvordan solaktivitet skjermer Jorden mot kosmisk stråling (nøytronmonitorer, Oulu), og en test av hypotesen om at kosmisk stråling styrer skydannelse mot ISCCP-skydata 1984–2016.
---

Jorden bombarderes hele tiden av ladde partikler fra verdensrommet, **galaktisk kosmisk stråling**. Solvinden og Solens magnetfelt skjermer delvis mot den, og skjermingen er sterkere når Solen er aktiv. Resultatet er at intensiteten av kosmisk stråling ved Jorden er *lavest ved solmaksimum og høyest ved solminimum* – i motfase til solflekkene. Den mest sikre sammenhengen her er derfor en annen enn den som ofte påstås: at solaktivitet påvirker kosmisk stråling (nivå A). At kosmisk stråling igjen påvirker klima, er en omdiskutert hypotese (nivå B).

## Dataene: nøytronmonitorer og modulasjonspotensial

Når kosmisk stråling treffer atmosfæren, dannes sekundære partikler. Nøytronmonitorer, blant dem stasjonen i Oulu i Finland, teller nøytroner på bakken, og telleraten er et mål for intensiteten av kosmisk stråling. Oulu-gruppen bruker nøytronmonitorene i et verdensomspennende nettverk til å beregne **modulasjonspotensialet Φ** (i megavolt, MV): jo høyere Φ, jo sterkere skjerming og jo *lavere* intensitet av kosmisk stråling.

Den direkte spørretjenesten for råtellerater fra Oulu svarte med feilmeldinger (HTTP 500) da dette nettstedet ble bygget, og NMDB-databasen krever pålogging. Derfor brukes Oulus publiserte Φ-tabell, som dekker 1936–siste fullførte år.

:::chart cosmic-series

Φ følger solflekktallet tett, men med en forsinkelse: kosmisk stråling reagerer ikke umiddelbart, fordi endringene i solvindens magnetfelt bruker tid på å nå ytterst i heliosfæren.

:::chart cosmic-lag

Korrelasjonen mellom årlig solflekktall og Φ er sterkest ved forsinkelse {{cosmic.scan_phi_ssn.best_lag|n0}} år (r = {{cosmic.scan_phi_ssn.best_r|n2}}, {{cosmic.scan_phi_ssn.period.0|year}}–{{cosmic.scan_phi_ssn.period.1|year}}; familievis p {{cosmic.scan_phi_ssn.p_family|p}}, {{cosmic.scan_phi_ssn.n_tests|n0}} lag testet). Sammenhengen er altså sterk og statistisk klar. Dette stemmer med fysikken bak såkalte Forbush-nedganger og solsyklusmodulasjonen som er kjent fra nøytronmonitorene siden 1950-tallet.

## Svensmark-hypotesen om skydannelse

I 1997 foreslo Henrik Svensmark og Eigil Friis-Christensen at kosmisk stråling kan påvirke dannelsen av skyer: ionisering fra kosmisk stråling kunne øke dannelsen av kondensasjonskjerner, flere lavskyer ville reflektere mer sollys, og klimaet ville bli kjøligere når Solen er svak (og kosmisk stråling sterk). Tanken er at dette forsterker den svake direkte solpåvirkningen.

Det er forskjellige ledd i kjeden, og de har ulik status:

1. Ionisering fra kosmisk stråling kan øke partikkeldannelse i laboratoriet. **Støttet.** CLOUD-eksperimentet ved CERN (Kirkby m.fl. 2011) viste at ioner kan øke nukleasjonsraten av små aerosolpartikler, særlig under visse forhold.
2. De nye partiklene vokser til kondensasjonskjerner for skydråper i atmosfæren i en størrelse som betyr noe. **Svakt/omdiskutert.** Modellstudier (for eksempel Pierce & Adams 2009) finner at effekten på skykjerner er for liten til å gi merkbare utslag i skydekke.
3. Det finnes en målbar sammenheng mellom kosmisk stråling og globalt skydekke i satellittdata. **Omdiskutert.** Svensmark & Friis-Christensen (1997) rapporterte en korrelasjon, men senere analyser (for eksempel Sloan & Wolfendale 2008; Laken m.fl. 2012) har ikke funnet en robust sammenheng, og resultatene avhenger av hvilke data og perioder man velger.
4. Kosmisk stråling har bidratt merkbart til observert global oppvarming. **Uten støtte.** Kosmisk stråling har ikke hatt en retning som kan forklare oppvarmingen siden 1980 (se under).

Ledd 3 kan vi nå teste direkte, med skydata. Ledd 2 (partikkeldannelse og vekst til skykjerner) kan ikke testes med satellittdata på dette nivået.

## Test mot skydata: ISCCP 1984–2016

Vi bruker ISCCP-H, den lengste homogeniserte satellittserien av skydekke, fra NOAA (månedlige 1°-data 1983–2017). Skyene er delt etter topptrykk i lave (under ca. 3 km), midlere og høye skyer; Svensmark-hypotesen gjelder særlig **lave skyer**. Vi regner ut areavektede månedlige anomalier (avvik fra månedsnormal) for hele kloden, tropene og midlere breddegrader (30–60°), tar årsmiddel for hele år og bruker −Φ som mål for intensiteten av kosmisk stråling. Hypotesen forutsier en *positiv* korrelasjon (mer kosmisk stråling, mer lavt skydekke).

:::chart cloud-series

ISCCP har en kjent svakhet: endringer i satellitter, kalibrering og visningsvinkel gir kunstige langtidstrender (Evan m.fl. 2007), og det globale lave skydekket har en nedadgående trend på {{svensmark.main.linear_trend_pct_per_decade|n1}} prosentpoeng per tiår (95 % konfidensintervall {{svensmark.main.linear_trend_ci.0|n1}} til {{svensmark.main.linear_trend_ci.1|n1}}) som delvis er kunstig. Derfor fjerner vi en lineær trend fra skydekket før vi korrelerer. Det er bare ca. {{svensmark.main.n_years|n0}} år, dvs. tre solsykluser, så antallet uavhengige punkter er svært lavt.

:::chart cloud-lag

**Resultat.** For globalt lavt skydekke ({{svensmark.main.period.0|year}}–{{svensmark.main.period.1|year}}) er korrelasjonen med kosmisk stråling r = {{svensmark.main.detrended.r|n2}} (95 % konfidensintervall {{svensmark.main.detrended.ci_lo|n2}} til {{svensmark.main.detrended.ci_hi|n2}}; surrogat-p {{svensmark.main.detrended.p_surrogate|p}}) etter trendfjerning, og r = {{svensmark.main.raw.r|n2}} uten trendfjerning. Med seks skyserier og fire forsinkelser ({{svensmark.n_tests|n0}} tester totalt i denne analysen) er den minste justerte p-verdien {{svensmark.min_p_holm_all|p}}.

Regresjonen gir {{svensmark.main.slope_pct_per_100mv|n2}} prosentpoeng lavt skydekke per 100 MV (konfidensintervall {{svensmark.main.slope_ci.0|n2}} til {{svensmark.main.slope_ci.1|n2}}). Over et typisk spenn i kosmisk stråling (5.–95. persentil, ca. {{svensmark.main.cr_range_mv_p5_p95|n0}} MV) tilsvarer det {{svensmark.main.implied_cycle_change_pct|n2}} prosentpoeng, med konfidensintervall {{svensmark.main.implied_cycle_ci.0|n1}} til {{svensmark.main.implied_cycle_ci.1|n1}}. Svensmark & Friis-Christensen (1997) rapporterte variasjoner i skydekke på noen få prosentpoeng over en solsyklus.

**Første og andre halvdel.** Den opprinnelige påstanden bygger på begynnelsen av ISCCP-perioden. Når vi deler opp, får vi r = {{svensmark.subperiods.early.r|n2}} for {{svensmark.subperiods.early.period.0|year}}–{{svensmark.subperiods.early.period.1|year}} (N_eff-p {{svensmark.subperiods.early.p_neff|p}}, surrogat-p {{svensmark.subperiods.early.p_surrogate|p}}) og r = {{svensmark.subperiods.late.r|n2}} for {{svensmark.subperiods.late.period.0|year}}–{{svensmark.subperiods.late.period.1|year}} (N_eff-p {{svensmark.subperiods.late.p_neff|p}}, surrogat-p {{svensmark.subperiods.late.p_surrogate|p}}). I første halvdel stemmer altså dataene med hypotesen, i andre halvdel peker de motsatt vei. At sammenhengen snur i den lengre serien, passer med kritikken i litteraturen (blant annet Sloan & Wolfendale 2008; Laken m.fl. 2012) om at den opprinnelige korrelasjonen ikke holder seg gjennom hele satellittperioden. Delperiodene er mindre enn 17 år hver og gir enda færre uavhengige punkter.

**Statistisk kraft.** Med ca. {{svensmark.main.detrended.neff|n0}} effektive frihetsgrader kan analysen bare påvise korrelasjoner over r ≈ {{svensmark.min_detectable_r|n2}} (80 % styrke). En ekte, men moderat sammenheng kan altså ikke oppdages med disse dataene.

:::when svensmark.min_p_holm_all >= 0.05
**Konklusjon av testen:** ingen skyserie viser en signifikant sammenheng med kosmisk stråling etter korreksjon for flere tester, og tegnet på sammenhengen skifter mellom perioder og forsinkelser. Dataene støtter ikke hypotesen, men har heller ikke styrke nok til å utelukke en liten effekt; konfidensintervallet for effekten over en syklus omfatter både null og noen tideler til ca. {{svensmark.main.implied_cycle_ci.1|n0}} prosentpoeng.
:::endwhen
:::when svensmark.min_p_holm_all < 0.05
**Konklusjon av testen:** minst én skyserie viser en signifikant sammenheng etter korreksjon (minste justerte p = {{svensmark.min_p_holm_all|p}}). Gitt ISCCPs kjente artefakter, de få sykluser og at andre solpåvirkninger varierer i takt, må dette bekreftes i uavhengige data før det kan regnes som støtte for hypotesen.
:::endwhen

**Hva en bedre test krever.** Analyser av Forbush-nedganger (raske, kortvarige fall i kosmisk stråling etter solutbrudd) kan skille kosmisk stråling fra de andre solpåvirkningene fordi de skjer på dagsskala. Det krever daglige skydata og nøytronmonitorer; de daglige PATMOS-x-filene er svært store, og CM SAFs CLARA-data krever bestilling, så de er ikke med her. Skydata fra nyere satellitter (MODIS, CERES) dekker bare to sykluser og har ikke vært undersøkt her.

## Hva sier dataene om temperatur og kosmisk stråling?

Siden 1980 har Φ endret seg med {{cosmic.phi_trend_1980_mv_per_decade|n0}} MV per tiår (95 % konfidensintervall {{cosmic.phi_trend_1980_ci.0|n0}} til {{cosmic.phi_trend_1980_ci.1|n0}} MV per tiår), altså ingen entydig langsiktig trend – kosmisk stråling har gått opp og ned i takt med solsyklusene, ikke i en retning som matcher oppvarmingen.

Korrelasjonen mellom årlig Φ og årlig global temperatur ({{cosmic.phi_temp_period.0|year}}–{{cosmic.phi_temp_period.1|year}}, GISTEMP) er r = {{cosmic.phi_vs_temp_raw.r|n2}} (konfidensintervall {{cosmic.phi_vs_temp_raw.ci_lo|n2}} til {{cosmic.phi_vs_temp_raw.ci_hi|n2}}, surrogat-p {{cosmic.phi_vs_temp_raw.p_surrogate|p}}) når temperaturen brukes som den er, og r = {{cosmic.phi_vs_temp_detrended.r|n2}} (konfidensintervall {{cosmic.phi_vs_temp_detrended.ci_lo|n2}} til {{cosmic.phi_vs_temp_detrended.ci_hi|n2}}) etter at en jevn trend er fjernet. For den trendfjernede varianten gir de to metodene for p-verdi litt ulike svar (N_eff-justert p = {{cosmic.phi_vs_temp_detrended.p_neff|p}}, surrogat-p = {{cosmic.phi_vs_temp_detrended.p_surrogate|p}}). Når to rimelige metoder spriker slik, er resultatet følsomt for metodevalg, og vi regner det ikke som evidens. Fortegnet (høyere Φ, altså *mindre* kosmisk stråling, sammen med varmere år) er dessuten det samme som en generell solsyklussammenheng og kan ikke skilles fra den.

Hovedproblemet er at kosmisk stråling, solinnstråling, ultrafiolett stråling og magnetisk aktivitet alle varierer i takt med solsyklusen. Det er derfor i praksis umulig å skille effekten av kosmisk stråling fra andre solpåvirkninger ved å se på 11-årssyklusen alene. I alt ble {{cosmic.n_tests|n0}} tester kjørt for denne siden.

:::evidence b Kosmisk stråling og klima
- [[a]] **Solaktivitet modulerer kosmisk stråling ved Jorden** (høy solaktivitet gir lav kosmisk stråling), med en forsinkelse på omtrent ett år.
- [[b]] **Kosmisk stråling påvirker skydannelse og dermed klima (Svensmark-hypotesen).** Laboratorieforsøk viser at ioner kan øke partikkeldannelsen, men det er ikke vist at effekten er stor nok i atmosfæren til å endre skydekke merkbart. Vår egen test mot ISCCP-skydata gir ingen signifikant sammenheng etter korreksjon, med motstridende fortegn mellom perioder, men har lav statistisk kraft; studier av satellittdata er motstridende.
- [[c]] **Kosmisk stråling forklarer oppvarmingen siden 1980.** Φ har ikke endret seg i en retning som passer, og de fysiske anslagene for effekten er små.
:::

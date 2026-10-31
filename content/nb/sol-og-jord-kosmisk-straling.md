---
route: /sol-og-jord/kosmisk-straling/
title: Kosmisk stråling og Svensmark-hypotesen
nav: sol-og-jord
slug: kosmisk
parent: sol-og-jord
order: 3
evidence: b
description: Hvordan solaktivitet skjermer Jorden mot kosmisk stråling (nøytronmonitorer, Oulu), og status for hypotesen om at kosmisk stråling styrer skydannelse og dermed klima.
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

Dette nettstedet har ikke egne skydata og kan derfor ikke teste ledd 2 og 3 direkte. Det vi kan teste er om *kosmisk stråling selv* viser en langtidsutvikling som kunne gi en langvarig oppvarming, og om Φ korrelerer med global temperatur.

## Hva sier dataene om temperatur og kosmisk stråling?

Siden 1980 har Φ endret seg med {{cosmic.phi_trend_1980_mv_per_decade|n0}} MV per tiår (95 % konfidensintervall {{cosmic.phi_trend_1980_ci.0|n0}} til {{cosmic.phi_trend_1980_ci.1|n0}} MV per tiår), altså ingen entydig langsiktig trend – kosmisk stråling har gått opp og ned i takt med solsyklusene, ikke i en retning som matcher oppvarmingen.

Korrelasjonen mellom årlig Φ og årlig global temperatur ({{cosmic.phi_temp_period.0|year}}–{{cosmic.phi_temp_period.1|year}}, GISTEMP) er r = {{cosmic.phi_vs_temp_raw.r|n2}} (konfidensintervall {{cosmic.phi_vs_temp_raw.ci_lo|n2}} til {{cosmic.phi_vs_temp_raw.ci_hi|n2}}, surrogat-p {{cosmic.phi_vs_temp_raw.p_surrogate|p}}) når temperaturen brukes som den er, og r = {{cosmic.phi_vs_temp_detrended.r|n2}} (konfidensintervall {{cosmic.phi_vs_temp_detrended.ci_lo|n2}} til {{cosmic.phi_vs_temp_detrended.ci_hi|n2}}) etter at en jevn trend er fjernet. For den trendfjernede varianten gir de to metodene for p-verdi litt ulike svar (N_eff-justert p = {{cosmic.phi_vs_temp_detrended.p_neff|p}}, surrogat-p = {{cosmic.phi_vs_temp_detrended.p_surrogate|p}}). Når to rimelige metoder spriker slik, er resultatet følsomt for metodevalg, og vi regner det ikke som evidens. Fortegnet (høyere Φ, altså *mindre* kosmisk stråling, sammen med varmere år) er dessuten det samme som en generell solsyklussammenheng og kan ikke skilles fra den.

Hovedproblemet er at kosmisk stråling, solinnstråling, ultrafiolett stråling og magnetisk aktivitet alle varierer i takt med solsyklusen. Det er derfor i praksis umulig å skille effekten av kosmisk stråling fra andre solpåvirkninger ved å se på 11-årssyklusen alene. I alt ble {{cosmic.n_tests|n0}} tester kjørt for denne siden.

:::evidence b Kosmisk stråling og klima
- [[a]] **Solaktivitet modulerer kosmisk stråling ved Jorden** (høy solaktivitet gir lav kosmisk stråling), med en forsinkelse på omtrent ett år.
- [[b]] **Kosmisk stråling påvirker skydannelse og dermed klima (Svensmark-hypotesen).** Laboratorieforsøk viser at ioner kan øke partikkeldannelsen, men det er ikke vist at effekten er stor nok i atmosfæren til å endre skydekke merkbart, og studier av satellittdata er motstridende.
- [[c]] **Kosmisk stråling forklarer oppvarmingen siden 1980.** Φ har ikke endret seg i en retning som passer, og de fysiske anslagene for effekten er små.
:::

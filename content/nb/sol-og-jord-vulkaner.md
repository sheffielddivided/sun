---
route: /sol-og-jord/vulkaner/
title: Vulkansk aktivitet og solsyklusen
nav: sol-og-jord
slug: vulkaner
parent: sol-og-jord
order: 7
evidence: c
description: En direkte test av påstanden om at store vulkanutbrudd (VEI ≥ 4 og ≥ 5, Smithsonian GVP) er ujevnt fordelt over solsyklusens faser eller mellom høy og lav solaktivitet – med superposed epoch-analyse og permutasjonstest.
---

En vanlig påstand er at store vulkanutbrudd skjer oftere ved solminimum eller ved bestemte faser i solsyklusen. Spørsmålet er undersøkt i flere artikler, for eksempel Stothers (1989). Det er ikke funnet noen akseptert fysisk mekanisme som kan overføre en så liten endring i Solens utstråling eller i kosmisk stråling til magmakamre flere kilometer under bakken. Her tester vi påstanden direkte, og vi presenterer resultatet slik det kommer, også når det er null.

## Dataene og avgrensningen

Utbruddene er hentet fra Smithsonian Global Volcanism Program (GVP), som registrerer utbrudd i Holocen med en eksplosivitetsindeks (VEI) fra 0 til 8. Vi bruker bare **bekreftede** utbrudd med **VEI ≥ 4** (og separat **VEI ≥ 5**). Eksplosivitetsindeksen måler utbruddets størrelse, ikke klimapåvirkningen; den siste avhenger blant annet av svovelmengden og breddegraden.

:::chart volcano-timeline

### Rapporteringsskjevhet og valg av periode

Eldre utbrudd er dårligere registrert, og små og mellomstore utbrudd er mer utsatt for å bli oversett jo lenger tilbake man går. Dette skaper en tilsynelatende økning i antall utbrudd mot nåtid som ikke er reell:

:::chart volcano-reporting

Antallet VEI ≥ 4-utbrudd per 50 år øker markant fra 1500-tallet til 1900-tallet, men flater ut etter omtrent 1850. Antallet VEI ≥ 5-utbrudd er mer stabilt, noe man forventer for så store hendelser, som merkes selv i avsidesliggende områder. Vi har derfor valgt to **primærscenarier** før vi kjørte testene:

- **Scenario A: VEI ≥ 4, 1850–2019.** Fra rundt 1850 er registreringen rimelig stabil per 50 år.
- **Scenario B: VEI ≥ 5, 1755–2019.** Store utbrudd regnes som tilstrekkelig fullstendig registrert fra solsyklus 1 (1755).

Analysen avsluttes i 2019, ved starten av syklus 25, fordi vi trenger fullførte sykluser for å beregne fase. Fire **følsomhetsscenarier** (C–F) varierer terskelen og perioden, og scenario F bruker bare utbrudd med presis startdato (Tambora er for eksempel registrert med start i 1812, mens hovedutbruddet var i 1815, og blir derfor ikke tatt med).

## Metode

Nullhypotesen er at utbruddstidspunktene er uavhengige av solsyklusen. Vi lager nullfordelingen ved å *forskyve hele utbruddsrekken sirkulært* med et tilfeldig antall år, {{volcano.n_shifts|n0}} ganger. Det bevarer utbruddenes antall, avstandene mellom dem (klynging) og eventuelle langsiktige endringer i registrering, men bryter koblingen til solsyklusen. Tre tester kjøres for hvert scenario:

1. **Fase i syklusen.** Hver syklus deles i fire like deler. Testen sammenligner antallet utbrudd i hver del med det som forventes ut fra hvor mye tid vinduet bruker i hver del (χ²).
2. **Høy mot lav aktivitet.** Antall utbrudd i måneder der glattet solflekktall ligger over medianen, mot det forventede (halvparten av tiden).
3. **Superposed epoch.** Gjennomsnittlig standardisert solflekktall for hvert av årene −5 til +5 rundt utbruddsåret, mot det tilfeldige utbruddsrekker gir. Én global test over alle 11 årene (maks |z|) gir p-verdien.

Seks primærtester (tre for hvert primærscenario) er justert med Holm-metoden. Alle seks scenariene gir til sammen {{volcano.n_tests|n0}} tester.

## Resultater

:::chart volcano-phase

Scenario A ({{volcano.scenarios.A.n_events|n0}} utbrudd): utbruddene fordeler seg på fasene som {{volcano.scenarios.A.phase.observed.0|n0}}, {{volcano.scenarios.A.phase.observed.1|n0}}, {{volcano.scenarios.A.phase.observed.2|n0}} og {{volcano.scenarios.A.phase.observed.3|n0}}, mot forventet {{volcano.scenarios.A.phase.expected.0|n1}}, {{volcano.scenarios.A.phase.expected.1|n1}}, {{volcano.scenarios.A.phase.expected.2|n1}} og {{volcano.scenarios.A.phase.expected.3|n1}} (p = {{volcano.scenarios.A.phase.p|p}}). Scenario B ({{volcano.scenarios.B.n_events|n0}} utbrudd): {{volcano.scenarios.B.phase.observed.0|n0}}, {{volcano.scenarios.B.phase.observed.1|n0}}, {{volcano.scenarios.B.phase.observed.2|n0}} og {{volcano.scenarios.B.phase.observed.3|n0}} mot forventet ca. {{volcano.scenarios.B.phase.expected.0|n1}} i hver del (p = {{volcano.scenarios.B.phase.p|p}}). Ingen fase skiller seg ut.

:::chart volcano-sea

Høy mot lav aktivitet: I scenario A skjedde {{volcano.scenarios.A.high_low.n_high|n0}} av {{volcano.scenarios.A.n_events|n0}} utbrudd ({{volcano.scenarios.A.high_low.observed_share_high|pct0}}) i perioder med solflekktall over medianen, mot {{volcano.scenarios.A.high_low.expected_share_high|pct0}} forventet; ujustert p = {{volcano.scenarios.A.high_low.p|p}}. Den superposed epoch-testen i scenario A gir ujustert global p = {{volcano.scenarios.A.sea.p_global|p}} (største avvik {{volcano.scenarios.A.sea.max_abs_z|n1}} standardavvik). I scenario B er p = {{volcano.scenarios.B.high_low.p|p}} for høy/lav og {{volcano.scenarios.B.sea.p_global|p}} for epoketesten.

:::chart volcano-scenarios

:::when volcano.min_p_primary_adjusted >= 0.05
Etter justering for de seks primærtestene er den minste p-verdien **{{volcano.min_p_primary_adjusted|p}}**. Ingen primærtest er signifikant. De nominelt lave p-verdiene i scenario A (rundt {{volcano.scenarios.A.high_low.p|p}} for høy/lav) forsvinner når man tar hensyn til at seks tester ble kjørt, og de gjentas ikke i noen av følsomhetsscenariene. Det er det man typisk ser når et tilfeldig mønster i støy finnes frem etter flere forsøk. Konklusjonen er at **dataene ikke gir støtte til at store vulkanutbrudd er ujevnt fordelt over solsyklusen**.
:::endwhen
:::when volcano.min_p_primary_adjusted < 0.05
Etter justering for de seks primærtestene er den minste p-verdien **{{volcano.min_p_primary_adjusted|p}}**, altså under 0,05. Resultatet er hverken forklart med en kjent mekanisme eller bekreftet i følsomhetsscenariene, og må replikeres i uavhengige data (og kontrolleres mot rapporteringsskjevhet) før det kan regnes som et funn.
:::endwhen

### Begrensninger

- **Statistisk kraft.** Med {{volcano.scenarios.B.n_events|n0}} utbrudd i scenario B kan bare store avvik påvises. «Ikke signifikant» betyr ikke «ingen sammenheng», men at en eventuell sammenheng er mindre enn det dataene kan avsløre.
- **Rapporteringsskjevhet.** Selv etter 1850 er registreringen ikke fullstendig, og det er mulig at fullstendigheten har variert i takt med faktorer som har sammenheng med tiden snarere enn solsyklusen. Sirkulær forskyvning beskytter mot dette bare delvis.
- **Datoer.** Mange eldre utbrudd har dato kjent bare til år eller månedsnivå; flerårige episoder har bare registrert starttid.
- **VEI er et grovt mål.** Utbrudd med lik VEI kan ha svært forskjellig svovelutslipp og klimaeffekt.
- **Vulkaner og klima er en annen sak.** Store vulkanutbrudd påvirker klimaet, ved at sulfataerosoler i stratosfæren reflekterer sollys og kjøler Jorden i noen år (Robock 2000). Denne siden handler om hvorvidt *Solen* påvirker *utbruddene*, ikke om at utbrudd påvirker klima. Se [Maunder-minimumet og Den lille istid](/sol-og-jord/maunder-og-lille-istid/).

:::evidence c Solsyklus og vulkanutbrudd
- [[c]] **Store vulkanutbrudd er ujevnt fordelt over solsyklusen eller mellom høy og lav solaktivitet.** Ikke støttet i vår analyse etter korreksjon for flere tester; ingen akseptert fysisk mekanisme.
- [[a]] **Registreringen av vulkanutbrudd er ufullstendig i eldre tid.** Derfor må alle slike analyser avgrenses til perioder med rimelig komplett registrering.
- [[b]] **Publiserte mønstre i enkeltstudier.** Slike funn må testes i nye data og med riktig korreksjon for antallet analyser før de kan regnes som etablert.
:::

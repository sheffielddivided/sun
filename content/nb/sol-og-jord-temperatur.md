---
route: /sol-og-jord/temperatur/
title: Global temperatur mot solaktivitet
nav: sol-og-jord
slug: temperatur
parent: sol-og-jord
order: 2
evidence: a
description: Global temperatur (GISTEMP og HadCRUT5) mot solflekktall, med lag-analyse, korreksjon for autokorrelasjon og multiple tester, og det tydelige bruddet mellom seriene etter ca. 1980.
---

Er global temperatur påvirket av solaktivitet? Spørsmålet har to deler: (1) Gir solsyklusen et lite, regelmessig utslag i global temperatur? (2) Kan endret solaktivitet forklare den kraftige oppvarmingen de siste tiårene? Dataene gir et tydelig svar på den andre delen og et usikkert på den første.

## Dataene

:::chart temp-series

Langs den øverste aksen vises årlig global temperatur fra to uavhengige analyser, NASA GISTEMP v4 og HadCRUT5 fra Met Office/UEA, begge omregnet til samme referanseperiode (1961–1990). Under vises solflekktallet som 11-årig glidende middel. Solflekktallet svinger i sykluser uten tydelig langtidsstigning siden 1950-tallet og er lavere i syklus 24 enn i syklus 21–23, mens temperaturen stiger jevnt. Seriene går altså i hver sin retning etter ca. 1980.

## Hva viser tallene etter 1980?

Mellom {{temperature.trend_1980_2025.period.0|year}} og {{temperature.trend_1980_2025.period.1|year}} økte global temperatur med {{temperature.trend_1980_2025.gistemp_c_per_decade|n2}} °C per tiår i GISTEMP (95 % konfidensintervall {{temperature.trend_1980_2025.gistemp_ci.0|n2}} til {{temperature.trend_1980_2025.gistemp_ci.1|n2}}) og {{temperature.trend_1980_2025.hadcrut5_c_per_decade|n2}} °C per tiår i HadCRUT5. Over hele perioden tilsvarer det en økning på ca. {{temperature.trend_1980_2025.gistemp_total_change_c|n1}} °C. Solflekktallet hadde i samme periode en trend på {{temperature.trend_1980_2025.ssn_per_decade|n1}} per tiår (konfidensintervall {{temperature.trend_1980_2025.ssn_ci.0|n0}} til {{temperature.trend_1980_2025.ssn_ci.1|n0}}, altså statistisk ikke forskjellig fra null), og den modellerte solinnstrålingen endret seg med {{temperature.trend_1980_2025.tsi_wm2_per_decade|s2}} W/m² per tiår (konfidensintervall {{temperature.trend_1980_2025.tsi_ci.0|n2}} til {{temperature.trend_1980_2025.tsi_ci.1|n2}}). Konfidensintervallene er justert for autokorrelasjon.

Hva ville solen kunne forklart om koblingen i perioden før 1980 hadde vært fullt kausal? Regresjonen av trendfjernet temperatur på solflekktall for {{temperature.subperiods.pre1980.period.0|year}}–{{temperature.subperiods.pre1980.period.1|year}} gir en koeffisient på {{temperature.trend_1980_2025.regression_pre1980_c_per_100ssn|n3}} °C per 100 enheter solflekktall (95 % konfidensintervall {{temperature.trend_1980_2025.regression_ci.0|n2}} til {{temperature.trend_1980_2025.regression_ci.1|n2}}). Ganger vi denne med den observerte endringen i solflekktall siden 1980, gir det en solrelatert temperaturendring på **{{temperature.trend_1980_2025.implied_solar_change_c|s2}} °C** – mot den observerte økningen på ca. {{temperature.trend_1980_2025.gistemp_total_change_c|s2}} °C. Koeffisientens konfidensintervall omfatter null, så anslaget er usikkert, men uansett er det som kan tilskrives solen i størrelsesorden langt under observert endring.

## Er det en sammenheng i solsyklusen?

Vi testet korrelasjonen mellom årlig solflekktall og trendfjernet temperatur (andregrads polynom fjernet for å ta bort den jevne langtidsendringen) for forsinkelser på 0 til 10 år – temperaturen kan jo reagere forsinket. Det gir 11 tester per temperaturserie.

:::chart temp-lag

For GISTEMP ({{temperature.scan_gistemp.period.0|year}}–{{temperature.scan_gistemp.period.1|year}}) er den sterkeste korrelasjonen r = {{temperature.scan_gistemp.best_r|n2}} ved forsinkelse {{temperature.scan_gistemp.best_lag|n0}} år. For HadCRUT5 ({{temperature.scan_hadcrut5.period.0|year}}–{{temperature.scan_hadcrut5.period.1|year}}) er den r = {{temperature.scan_hadcrut5.best_r|n2}} ved forsinkelse {{temperature.scan_hadcrut5.best_lag|n0}} år. Familievise p-verdier (som tar hensyn til at vi valgte det beste av 11 lag) er {{temperature.scan_gistemp.p_family|p}} og {{temperature.scan_hadcrut5.p_family|p}}. :::when temperature.scan_gistemp.min_p_holm >= 0.05
:::when temperature.scan_hadcrut5.min_p_holm >= 0.05
Ingen forsinkelse er signifikant etter Holm-korreksjon: den minste Holm-justerte p-verdien er {{temperature.scan_gistemp.min_p_holm|p}} (GISTEMP) og {{temperature.scan_hadcrut5.min_p_holm|p}} (HadCRUT5).
:::endwhen
:::endwhen
:::when temperature.scan_gistemp.min_p_holm < 0.05
Minst én forsinkelse er signifikant etter Holm-korreksjon i GISTEMP (minste justerte p = {{temperature.scan_gistemp.min_p_holm|p}}). Resultatet bør tolkes forsiktig og sjekkes mot flere serier.
:::endwhen
:::when temperature.scan_hadcrut5.min_p_holm < 0.05
Minst én forsinkelse er signifikant etter Holm-korreksjon i HadCRUT5 (minste justerte p = {{temperature.scan_hadcrut5.min_p_holm|p}}). Resultatet bør tolkes forsiktig og sjekkes mot flere serier.
:::endwhen

Delt i to perioder (lag 0, uten forsinkelse): før 1980 er korrelasjonen r = {{temperature.subperiods.pre1980.raw.r|n2}} (95 % konfidensintervall {{temperature.subperiods.pre1980.raw.ci_lo|n2}} til {{temperature.subperiods.pre1980.raw.ci_hi|n2}}, surrogat-p {{temperature.subperiods.pre1980.raw.p_surrogate|p}}), og etter 1980 r = {{temperature.subperiods.post1980.raw.r|n2}} (konfidensintervall {{temperature.subperiods.post1980.raw.ci_lo|n2}} til {{temperature.subperiods.post1980.raw.ci_hi|n2}}, surrogat-p {{temperature.subperiods.post1980.raw.p_surrogate|p}}). :::when temperature.subperiods.pre1980.raw.p_surrogate >= 0.05
:::when temperature.subperiods.post1980.raw.p_surrogate >= 0.05
Ingen av dem er signifikant.
:::endwhen
:::endwhen
Totalt ble {{temperature.n_tests|n0}} tester kjørt for denne siden.

## Hvorfor er signalet så vanskelig å finne?

- **Støy.** Naturlig variasjon som El Niño–La Niña (ENSO), vulkanutbrudd og menneskeskapte aerosoler varierer like mye som eller mer enn et mulig solsyklussignal på rundt 0,1 °C eller mindre.
- **Få uavhengige sykluser.** Siden 1880 finnes det bare rundt 13 sykluser, og effektivt antall frihetsgrader er enda lavere enn antall år.
- **Menneskeskapt trend.** Den bratte trenden siden 1970-tallet må fjernes eller modelleres, og valg av metode påvirker resultatet.
- **Metodebegrensninger her.** Analysen bruker årlige gjennomsnitt og fjerner en polynomtrend; den bruker ikke en fullstendig klimamodell. Studier som kontrollerer for ENSO, vulkaner og menneskeskapte påvirkninger anslår et 11-årig signal i størrelsesorden en tiendedels grad eller mindre (for eksempel Lean & Rind 2008; Gray m.fl. 2010).

:::evidence a Solens rolle for global temperatur
- [[a]] **Solaktivitet er ikke årsaken til oppvarmingen siden 1980.** Solflekktall og solinnstråling har ikke økt i perioden, mens temperaturen har steget kraftig. IPCC AR6 anslår at endringer i sol og vulkaner til sammen bidro med mellom −0,1 og +0,1 °C til global temperatur fra 1850–1900 til 2010–2019 (IPCC AR6 WG1, Summary for Policymakers).
- [[b]] **Et lite 11-årig signal i global temperatur.** Publiserte estimater (se for eksempel Lean & Rind 2008 og oversikten til Gray m.fl. 2010) peker på en effekt i størrelsesorden en tiendedels grad eller mindre, og våre egne analyser av årlige data er ikke i stand til å påvise det (se lag-analysen over), og estimatene avhenger av hvilke andre påvirkninger man trekker fra.
- [[c]] **«Solen forklarer klimaendringene».** Står i strid med data på størrelsesordenen, retningen etter 1980 og fysikken.
:::

Lockwood & Fröhlich (2007) viste allerede for to tiår siden at solindikatorene og temperaturen gikk i hver sin retning de siste tiårene. Referanser finnes på [Metode og kilder](/metode/#referanser).

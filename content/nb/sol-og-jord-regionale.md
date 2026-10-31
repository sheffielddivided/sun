---
route: /sol-og-jord/regionale-monstre/
title: Regionale klimamønstre: NAO og ENSO
nav: sol-og-jord
slug: regionale
parent: sol-og-jord
order: 6
evidence: b
description: Publiserte, omdiskuterte signaler om at solsyklusen påvirker vintermønstre i Atlanterhavet (NAO) og Stillehavet (ENSO) – testet mot dataene med korreksjon for autokorrelasjon og multiple tester.
---

Selv om solsyklusen gir lite utslag i global middeltemperatur, har flere forskere foreslått at den kan påvirke *regionale* mønstre, særlig vintervær i Nord-Atlanteren. Idéen er at endringer i ultrafiolett stråling påvirker temperaturen i stratosfæren og dermed vindene der, som igjen påvirker været nedover i troposfæren (Gray m.fl. 2010). Den bakenforliggende fysikken er plausibel, men det statistiske signalet er svakt og har vist seg vanskelig å reprodusere.

## Hvilke mønstre?

- **NAO (Nord-Atlanterhavsoscillasjonen)** måler trykkforskjellen mellom Azorene og Island og styrer vind og nedbør i Vest-Europa og Norge, spesielt om vinteren. Ineson m.fl. (2011) fant i en modell og i observasjoner at lav solaktivitet kan gi vinteren en tendens til negativ NAO (kaldere og tørrere i Nord-Europa). Gray m.fl. (2013) fant et mønster i vinterdata som kom med en forsinkelse på 3–4 år etter solmaksimum.
- **ENSO (El Niño–La Niña)** er den dominerende naturlige klimasvingningen i Stillehavet med en periode på 2–7 år. Noen studier har pekt på at solaktiviteten kan modulere ENSO; funnene er motstridende.

## Dataene

:::chart regional-nao

Vi bruker NOAAs månedlige NAO-indeks og Oceanic Niño Index (ONI) fra Climate Prediction Center, begge fra 1950. Vi tar gjennomsnittet for desember–februar (DJF) i hvert år og korrelerer med årlig solflekktall for forsinkelser fra 0 til 5 år (6 tester per indeks, {{regional.n_tests|n0}} tester totalt).

:::chart regional-lag

For NAO ({{regional.scan_nao_djf.period.0|year}}–{{regional.scan_nao_djf.period.1|year}}) er den sterkeste korrelasjonen r = {{regional.scan_nao_djf.best_r|n2}} ved forsinkelse {{regional.scan_nao_djf.best_lag|n0}} år (familievis p {{regional.scan_nao_djf.p_family|p}}, minste Holm-justerte p {{regional.scan_nao_djf.min_p_holm|p}}). For ONI er den sterkeste r = {{regional.scan_oni_djf.best_r|n2}} ved forsinkelse {{regional.scan_oni_djf.best_lag|n0}} år (familievis p {{regional.scan_oni_djf.p_family|p}}, minste Holm-justerte p {{regional.scan_oni_djf.min_p_holm|p}}).

:::when regional.scan_nao_djf.min_p_holm >= 0.05
:::when regional.scan_oni_djf.min_p_holm >= 0.05
Ingen av forsinkelsene er signifikante etter korreksjon for flere tester. Det betyr ikke at det ikke finnes en effekt: tidsserien dekker bare omkring {{regional.n_cycles_covered|n1}} solsykluser, så den statistiske kraften er lav, og en effekt som i litteraturen anslås til noen få prosent av variansen kan ikke påvises med så få sykluser. Resultatet gir altså hverken støtte til eller avkreftelse av de publiserte signalene.
:::endwhen
:::endwhen
:::when regional.scan_nao_djf.min_p_holm < 0.05
For NAO er minst én forsinkelse signifikant etter korreksjon (minste justerte p = {{regional.scan_nao_djf.min_p_holm|p}}). Siden tidsserien bare dekker ca. {{regional.n_cycles_covered|n1}} solsykluser, bør dette regnes som et funn som må bekreftes i uavhengige data.
:::endwhen
:::when regional.scan_oni_djf.min_p_holm < 0.05
For ENSO er minst én forsinkelse signifikant etter korreksjon (minste justerte p = {{regional.scan_oni_djf.min_p_holm|p}}). Siden tidsserien bare dekker ca. {{regional.n_cycles_covered|n1}} solsykluser, bør dette regnes som et funn som må bekreftes i uavhengige data.
:::endwhen

## Hvorfor er dette området så omstridt?

- **Svært få sykluser.** Observasjonene av NAO og ENSO går bare tilbake til 1950, altså rundt seks sykluser. Mye av litteraturen bygger på modeller eller korte perioder.
- **Mye støtte fra tilfeldig variasjon.** NAO har store svingninger fra år til år som ikke har noe med Solen å gjøre.
- **Fleksibel analyse.** Når man kan velge sesong, forsinkelse, indeks og periode fritt, er det lett å finne et «signal». Derfor korrigerer vi her for antallet tester.
- **Ulike modeller gir ulike svar.** Resultatene av klimamodeller med god stratosfære er mer overbevisende enn modeller uten, men de er heller ikke enige om størrelsen.

:::evidence b Regionale klimamønstre
- [[b]] **Solsyklusen modulerer vinter-NAO, muligens med en forsinkelse på noen år.** Publisert i flere studier (Ineson m.fl. 2011, Gray m.fl. 2013), men ikke bekreftet av vår enkle analyse, og effekten er liten sammenlignet med naturlig variasjon.
- [[b]] **Solsyklusen modulerer ENSO.** Motstridende resultater i litteraturen; vår analyse viser ingen påviselig sammenheng.
- [[c]] **Man kan bruke solflekktallet til å forutsi været i en enkelt vinter.** Ingen dokumentert prediktiv verdi.
:::

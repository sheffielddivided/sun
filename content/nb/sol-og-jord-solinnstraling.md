---
route: /sol-og-jord/solinnstraling/
title: Total solinnstråling (TSI)
nav: sol-og-jord
slug: tsi
parent: sol-og-jord
order: 1
evidence: a
description: Hvor mye solinnstrålingen varierer gjennom en solsyklus, hva som er målt og hva som er modellert, og hvorfor variasjonen er liten sammenlignet med menneskeskapt pådriv.
---

**Total solinnstråling (TSI)** er den samlede energien fra Solen som treffer et flatt areal vinkelrett mot strålene, utenfor atmosfæren, ved Jordens middelavstand. Verdien er rundt 1 361 W/m². Siden 1978 har satellitter målt den kontinuerlig, og målingene viser at den varierer litt i takt med solsyklusen.

## Hva er målt – og hva er modell?

Datagrunnlaget her er i to deler, og forskjellen er viktig:

- **NNLTSI (NOAA Climate Data Record).** En *modell* fra NASA/NOAA/LASP som beregner TSI fra flekk- og faklindekser, tilbake til 1610. Modellen er kalibrert mot satellittmålingene, men før 1978 er alt modellresultat. Årlige verdier brukes her.
- **TSIS-1 (LASP/Univ. of Colorado).** En *måling* fra instrumentet TIM om bord på Den internasjonale romstasjonen siden 2018, brukt her som månedsmiddel. Måleserien er kort, men svært presis.

:::chart tsi-series

Satellitt-kompositter fra 1978 og fremover (blant annet PMOD og ACRIM) er ikke fullt enige om hvordan nivået utviklet seg mellom solminima, fordi instrumentene har ulik drift og det var et opphold i målingene på 1980-tallet. Dette er en kjent og ikke avklart usikkerhet i langtidstrenden; den påvirker ikke konklusjonen om størrelsen på 11-årsvariasjonen.

## Hvor mye varierer den?

Fra solminimum til solmaksimum øker TSI med omtrent 1 W/m². I modellen er gjennomsnittet av forskjellen mellom høyeste og laveste årsmiddel innenfor syklus 20–24 **{{tsi.mean_range_cycles_20_24|n2}} W/m²**, eller **{{tsi.mean_range_pct|n3}} %** av middelverdien. De målte verdiene fra TSIS-1 viser at 13-måneders midlet økte med {{tsi.tsis_rise_wm2|n2}} W/m² ({{tsi.tsis_rise_pct|n3}} %) fra minimum i {{tsi.tsis_min_t|my}} til toppen i {{tsi.tsis_max_t|my}} i syklus 25.

:::chart tsi-cycle-range

Hvis variasjonen midles over hele Jordens overflate og justeres for at jorden reflekterer omtrent {{tsi.albedo_assumed|pct0}} (antatt albedo) og at kloden er en kule (faktor 1/4), tilsvarer {{tsi.mean_range_cycles_20_24|n2}} W/m² et endret strålingspådriv på ca. **{{tsi.forcing_equiv_wm2|n2}} W/m²** mellom minimum og maksimum. Til sammenligning anslår IPCCs sjette hovedrapport at det totale menneskeskapte pådrivet i 2019 var omtrent {{tsi.ar6_anthropogenic_erf_wm2|n1}} W/m² større enn i 1750 (IPCC AR6 WG1, kap. 7). Solsyklusens bidrag er altså godt under en tidel av det menneskeskapte pådrivet, og det går opp og ned i løpet av 11 år i stedet for å akkumulere.

## Korrelasjon med solflekktallet – og en advarsel

Den årlige NNLTSI-modellen korrelerer sterkt med årlig solflekktall ({{tsi.corr_period.0|year}}–{{tsi.corr_period.1|year}}): r = {{tsi.corr_nnl_ssn.r|n2}} (95 % konfidensintervall {{tsi.corr_nnl_ssn.ci_lo|n2}} til {{tsi.corr_nnl_ssn.ci_hi|n2}}, effektive frihetsgrader N_eff ≈ {{tsi.corr_nnl_ssn.neff|n0}} av N = {{tsi.corr_nnl_ssn.n|n0}}; surrogat-p {{tsi.corr_nnl_ssn.p_surrogate|p}}). **Dette er ikke et uavhengig funn**: modellen bruker flekk- og faklindekser som innspill, så høy korrelasjon er bygget inn. Det uavhengige beviset er satellittmålingene siden 1978, som bekrefter at TSI faktisk øker med flekkaktiviteten.

:::evidence a Solinnstrålingens variasjon
- [[a]] **TSI varierer med solsyklusen med omtrent 0,1 %.** Målt av flere satellitter og bekreftet av TSIS-1.
- [[a]] **Variasjonen er for liten til å forklare nylig global oppvarming.** Både størrelsen ({{tsi.forcing_equiv_wm2|n2}} W/m² pådriv per syklus) og retningen (ingen økende trend i solaktivitet de siste tiårene) stemmer med IPCCs vurdering.
- [[b]] **Langtidstrend i TSI før 1978 og mellom minima.** Modellrekonstruksjoner spriker, og satellittkompositter er uenige om nivået på 1980-tallet.
:::

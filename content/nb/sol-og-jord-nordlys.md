---
route: /sol-og-jord/nordlys/
title: Geomagnetiske stormer og nordlys
nav: sol-og-jord
slug: nordlys
parent: sol-og-jord
order: 4
evidence: a
description: Her er sammenhengen mellom solaktivitet og romvær sterk og godt dokumentert: Kp-indeksen, stormdøgn per år, faseprofil gjennom solsyklusen og hva det betyr for nordlys i Norge.
---

Sammenhengen mellom solaktivitet og **geomagnetiske stormer** er den best dokumenterte koblingen mellom Solen og Jorden. Allerede i 1852 viste Edward Sabine, Rudolf Wolf og Alfred Gautier at variasjonen i Jordens magnetfelt følger flekksyklusen. I dag forstår vi mekanismen: koronamasseutkast og raske solvindstrømmer presser og kobler seg til Jordens magnetfelt, setter strøm i gang i magnetosfæren og ioniserer atmosfæren; det siste er det vi ser som nordlys.

## Måleinstrumentet: Kp og ap

**Kp-indeksen** (0–9) beregnes av GFZ i Potsdam ut fra magnetometre på midlere breddegrader og beskriver hvor urolig Jordens magnetfelt er, i tre-timersintervaller. Verdien Kp ≥ 5 tilsvarer en geomagnetisk storm på nivå G1 på NOAAs skala. **ap** er en lineær versjon av samme størrelse. Vi bruker de lange seriene fra 1932, og teller «stormdøgn» som døgn med Kp ≥ 5 på minst ett tidspunkt. I gjennomsnitt er det ca. {{geomag.annual_storm_days_mean|n0}} slike døgn per år, men tallet varierer mye.

:::chart geomag-annual

Antall stormdøgn følger solsyklusen: det er flere i år med mange flekker. Men toppene sammenfaller ikke akkurat med flekkmaksimum.

## Hvor sterk er sammenhengen?

Vi testet korrelasjonen mellom årlig solflekktall og årlig antall stormdøgn ({{geomag.scan_storm_days.period.0|year}}–{{geomag.scan_storm_days.period.1|year}}) for forsinkelser fra 0 til 4 år (5 tester): den sterkeste er r = {{geomag.scan_storm_days.best_r|n2}} ved forsinkelse {{geomag.scan_storm_days.best_lag|n0}} år (familievis p {{geomag.scan_storm_days.p_family|p}}). For årlig gjennomsnittlig ap er det r = {{geomag.scan_ap.best_r|n2}} ved forsinkelse {{geomag.scan_ap.best_lag|n0}} år (familievis p {{geomag.scan_ap.p_family|p}}). :::when geomag.scan_storm_days.p_family < 0.05
Begge er signifikante også etter korreksjon for autokorrelasjon og flere tester (10 tester totalt).
:::endwhen
:::when geomag.scan_storm_days.p_family >= 0.05
Med dagens data er sammenhengen ikke lenger signifikant etter korreksjon for flere tester (10 tester totalt); resultatet bør vurderes på nytt.
:::endwhen

## Når i syklusen kommer stormene?

:::chart geomag-phase

Aktiviteten er lavest nær solminimum og høyest *etter* flekkmaksimum (som i gjennomsnitt kommer omtrent 40 % ut i syklusen), i den avtagende fasen, med toppen i faseintervallet {{geomag.phase_profile.storm_peak_from_pct|n0}}–{{geomag.phase_profile.storm_peak_to_pct|n0}} % av syklusen (0 % = solminimum, 100 % = neste minimum). Forklaringene er kjente fra litteraturen: i den avtagende fasen er det mange koronale hull som gir raske solvindstrømmer som gjentar seg hver 27. dag, og store koronamasseutkast kan fortsatt forekomme. Dessuten ligger de store stormene gjerne rundt jevndøgn (Russell & McPherron 1973) – en effekt som ikke er undersøkt på denne siden.

## Hva betyr det for nordlys?

Nordlys opptrer i et ovalt belte rundt de geomagnetiske polene, **nordlysovalen**. Nord-Norge ligger under eller nær ovalen, så nordlys kan sees mange kvelder i året også ved lav geomagnetisk aktivitet. Under sterke stormer utvider ovalen seg sørover, og nordlys kan sees i Sør-Norge og i enda lavere breddegrader, slik det skjedde i mai 2024. Jo høyere Kp, jo lenger sør kan nordlys sees. Siden stormene er hyppigere i den avtagende fasen enn ved selve flekkmaksimum, behøver ikke de beste nordlysårene å falle sammen med flekkmaksimum – og de er uansett forskjellige fra år til år.

Nordlys måles ikke i dataene på denne siden; Kp er et mål på geomagnetisk uro, ikke på hvor synlig nordlyset er. Sikt og skydekke avgjør hva man faktisk ser.

## Konsekvenser

Kraftige stormer kan indusere strømmer i lange ledninger. Det er årsaken til strømbruddet i Québec 13. mars 1989 og de dokumenterte forstyrrelsene i telegrafsystemene i 1859 (Carrington-hendelsen). Satellitter, navigasjon og kortbølgeradio er også utsatt. Derfor overvåker NOAA og andre romværtjenester Kp og solaktivitet kontinuerlig, og varslene brukes i flytrafikk, kraftnett og satellittdrift.

:::evidence a Solaktivitet og geomagnetiske stormer
- [[a]] **Geomagnetisk aktivitet følger solsyklusen.** Sterk korrelasjon, kjent mekanisme (solvind og koronamasseutkast), målt kontinuerlig siden 1932 og indirekte lenger tilbake.
- [[a]] **De største stormene kan komme også i svake sykluser.** Kraftige stormer er kjent fra både sterke og svake sykluser (Carrington-hendelsen i 1859 kom i en middels sterk syklus).
- [[b]] **Hvilken fase i syklusen som gir flest storstormer** (og forklaringen på det) er fortsatt gjenstand for forskning, og tallene her bygger på bare {{geomag.phase_profile.n_cycles|n0}} sykluser.
:::

---
route: /sol-og-jord/pastander-uten-stotte/
title: Påstander uten støtte
nav: sol-og-jord
slug: pastander
parent: sol-og-jord
order: 8
evidence: c
description: Jordskjelv, børskurser, helse og andre vanlige nettpåstander om solflekker – og en forklaring av hvorfor tilfeldige korrelasjoner oppstår så lett, med simuleringer fra datapipelinen.
---

På nettet finnes det lange lister over ting solflekkene angivelig påvirker: jordskjelv, børskurser, kriger, hjerteinfarkt, valgresultater, dyrs oppførsel. Felles for mange er at de bygger på en graf der to kurver «ser ut til å følge hverandre». Her forklarer vi hvorfor slike grafer er lette å lage og lite å stole på.

## Noen vanlige påstander

**Jordskjelv.** Påstanden er at solaktivitet eller kosmisk stråling utløser jordskjelv. Vi har ikke testet jordskjelvdata her. Energien i jordskjelv er lagret som elastisk spenning i jordskorpen og er mange størrelsesordener større enn det solaktivitet kan tilføre; vi kjenner ingen akseptert mekanisme. Den enkleste forklaringen på rapporterte sammenfall er at begge seriene er korte, støyfylte og analysert med fleksible valg (periode, størrelsesgrense, forsinkelse). Påstanden havner i nivå C inntil noen viser en robust sammenheng som holder i uavhengige data.

**Børskurser og økonomi.** Aksjekurser og priser er såkalte ikke-stasjonære serier: de trender oppover eller nedover over lange perioder. Når man sammenligner to slike trender, får man ofte høy korrelasjon uten noen sammenheng – nøyaktig det simuleringene under viser. Vi har ikke testet finansdata her.

**Helse (hjerteinfarkt, fødsler, psykisk helse).** Disse seriene har sterke sesongvariasjoner og langtidstrender som må fjernes først, og tidsserier for helse har ofte endringer i registrering og diagnostikk. Flere studier har gjort forsøk, men resultatene varierer mellom perioder og land. Vi har ikke testet helsedata her. Den eneste solpåvirkningen med solid fysikalsk grunnlag på helse er stråling og kosmisk stråling for flypersonell og astronauter, som er uten forbindelse til disse påstandene.

**«Solen styrer været i hver enkelt uke eller sesong».** Se [regionale mønstre](/sol-og-jord/regionale-monstre/): selv det mest omtalte signalet er svakt og omdiskutert.

## Hvorfor tilfeldige korrelasjoner oppstår

1. **Få uavhengige observasjoner.** Naboverdier i en tidsserie ligner hverandre. En serie med 100 årsverdier kan ha bare 10–20 virkelig uavhengige punkter. Vanlige signifikanstester forutsetter 100.
2. **Trender.** To serier som begge stiger eller faller over tid, korrelerer, uavhengig av om de har noe med hverandre å gjøre.
3. **Mange kandidater (datafisking).** Det finnes millioner av tidsserier. Hvis man tester nok av dem, vil noen se ut som de følger solflekkene.
4. **Fleksible valg.** Man kan velge periode, glatting, forsinkelse og utvalg etter at man har sett dataene. Hvert valg er en ekstra test som ikke telles.
5. **Utvalgsskjevhet.** Det er bare de «treffene» som publiseres og deles, ikke de hundrevis av forsøk som ikke ga noe.

## Simulering: hva skjer med helt tilfeldige data?

Datapipelinen genererer tilfeldige serier uten noen forbindelse til Solen og korrelerer dem med det faktiske årlige solflekktallet ({{spurious.period.0|year}}–{{spurious.period.1|year}}). Den måler hvor ofte tre ulike tester gir «signifikant» (p < 0,05) når den riktige svaren er «nei»:

:::chart spurious-rates

For to uavhengige tilfeldige vandringer (to «trender») gir en naiv korrelasjonstest hele {{spurious.scenarios.3.false_positive_naive|pct0}} falske positive, i stedet for de 5 % man forventer. Mot solflekktallet og en tilfeldig vandring er andelen {{spurious.scenarios.2.false_positive_naive|pct0}}. Testen vi bruker på de andre sidene, fase-surrogattesten, holder seg nær 5 % for ikke-trendende støy ({{spurious.scenarios.0.false_positive_surrogate|pct1}} for hvit støy og {{spurious.scenarios.1.false_positive_surrogate|pct1}} for autokorrelert støy), og er enda mer forsiktig for en tilfeldig vandring mot solflekktallet ({{spurious.scenarios.2.false_positive_surrogate|pct1}}). Den er derimot ikke perfekt for to uavhengige trender ({{spurious.scenarios.3.false_positive_surrogate|pct0}} falske positive), og derfor fjerner vi trender før vi tester, slik for eksempel i temperaturanalysen.

Datafisking: Hvis du tester 20 uavhengige tilfeldige vandringer mot solflekktallet med den naive testen, er sannsynligheten for å få minst én «signifikant» {{spurious.at_least_one_of_20_naive_random_walk|pct0}}. I pipelinen ble det også generert {{spurious.example.n_candidates|n0}} tilfeldige serier; den beste av dem har en korrelasjon på r = {{spurious.example.r|n2}} med solflekktallet:

:::chart spurious-example

Hvis man hadde vist bare denne kurven, uten å si at den var den beste av {{spurious.example.n_candidates|n0}}, ville det sett ut som en sammenheng. Det var ingen.

## Slik sjekker du en påstand

- Hvor mange uavhengige sykluser eller hendelser bygger den på? (Ikke bare hvor mange datapunkter.)
- Er trender fjernet, eller er det to stigende kurver?
- Hvor mange perioder, forsinkelser og serier ble prøvd før dette ble funnet?
- Finnes det en fysisk mekanisme som gir riktig størrelsesorden?
- Holder sammenhengen i data som ikke ble brukt til å finne den?

:::evidence c Vanlige nettpåstander om solflekker
- [[c]] **Solflekker forutsier børskurser.** Ingen mekanisme, og samme feilkilder som i simuleringen over.
- [[c]] **Solflekker utløser jordskjelv.** Ingen akseptert mekanisme; energiforholdene taler imot. Ikke testet her.
- [[c]] **En enkelt graf der to kurver «følger hverandre» er bevis.** Simuleringene viser at den naive testen gir mange falske positive; kurver som følger hverandre kan komme av tilfeldigheter.
:::

---
route: /
title: Solflekker og solsyklusen – hva dataene viser
nav: home
slug: home
description: Dagens solflekktall, solsyklus 25 mot prognosen, radiofluks (F10.7) og geomagnetisk aktivitet (Kp) – med åpne data og ærlig statistikk om forholdet mellom Sola og Jorda.
---

Solflekker er mørke, kjøligere områder på Solens overflate der sterke magnetfelt hindrer varme i å strømme opp fra dypet. Antallet flekker svinger i en syklus på rundt 11 år, og er en av de lengste kontinuerlige observasjonsseriene i astronomien: daglige tellinger finnes tilbake til 1818 og månedlige gjennomsnitt tilbake til 1749. Dette nettstedet følger den pågående syklusen, forklarer hva flekkene er, og går gjennom hva åpne data faktisk sier om koblingene mellom solaktivitet, klima og romvær – både der sammenhengen er sterk og der den ikke finnes.

:::dashboard

## Solsyklus 25 mot prognosen

:::chart home-cycle25

Syklus 25 begynte i {{cycles.cycles.24.start_t|my}}. Den høyeste glattede verdien så langt er {{cycles.cycles.24.max_smoothed|n0}}, nådd i {{cycles.cycles.24.max_t|my}}. Til sammenligning nådde syklus 24 en topp på {{cycles.cycles.23.max_smoothed|n0}} og syklus 23 en topp på {{cycles.cycles.22.max_smoothed|n0}}. Gjennomsnittet for alle {{cycles.summary.n_complete|n0}} fullførte sykluser siden 1755 er {{cycles.summary.mean_max_smoothed|n0}}, og den høyeste noensinne (syklus {{cycles.summary.highest_cycle|n0}}) var {{cycles.summary.highest_max|n0}}.

Det glattede tallet er et 13-måneders glidende middel og kan derfor først beregnes seks måneder etter selve målingen. Det betyr at toppen av en syklus bare kan fastslås i ettertid – fordi tallet kan stige igjen etter en midlertidig nedgang. NOAA-prognosen (stiplet linje med bånd) er en statistisk modell som revideres jevnlig; den er ikke en fysisk forutsigelse.

## Siste to år, dag for dag

:::chart home-ssn-daily

Daglige solflekktall hopper mye, fordi flekkgrupper roterer inn og ut av synsfeltet (Solen roterer på omtrent 27 døgn sett fra Jorden) og fordi de utvikler seg raskt. Derfor brukes månedlige og glattede verdier for å se utviklingen i syklusen. Det foreløpige estimatet (EISN) publiseres nesten i sanntid, mens den endelige SILSO-verdien kommer en til to måneder senere.

## Radiofluks og geomagnetisk aktivitet

:::chart home-f107

**F10.7** er Solens radiostråling ved bølgelengden 10,7 cm, oppgitt i solar flux units (1 sfu = 10⁻²² W m⁻² Hz⁻¹). Den måles uavhengig av vær og dagslys, påvirkes lite av enkeltflekker, og følger solaktiviteten tett. Typiske verdier er rundt 65–70 sfu ved solminimum og godt over 150 ved solmaksimum.

:::chart home-kp

**Kp** er en indeks fra 0 til 9 som måler hvor urolig Jordens magnetfelt er, beregnet av GFZ i Potsdam ut fra målinger ved observatorier på midlere breddegrader. Kp ≥ 5 tilsvarer en geomagnetisk storm på nivå G1 («svak storm») eller høyere på NOAAs skala, Kp = 9 er nivå G5 («ekstrem»). Nordlys kan sees i Nord-Norge selv ved lav Kp, men jo høyere Kp, jo lenger sør kan det sees. Kp følger solsyklusen, men toppene kommer gjerne etter flekkmaksimum – se [Geomagnetiske stormer og nordlys](/sol-og-jord/nordlys/).

## Gå videre

- [Hva er solflekker?](/hva-er-solflekker/) – fysikken, hvordan tallet beregnes, syklusene og koblingen til solutbrudd.
- [Historien](/historien/) – fra kinesiske observasjoner til versjon 2.0 av serien i 2015.
- [Data](/dataserier/) – interaktive grafer med zoom, alle sykluser lagt over hverandre, sommerfugldiagram og CSV-nedlasting.
- [Sol og jord](/sol-og-jord/) – hva sier dataene om solinnstråling, temperatur, kosmisk stråling, nordlys, Maunder-minimumet, regionale klimamønstre og vulkaner? Hver påstand er merket som godt etablert, omdiskutert eller uten støtte.
- [Metode og kilder](/metode/) – alle datakilder, lisenser, kjente svakheter og referanser.

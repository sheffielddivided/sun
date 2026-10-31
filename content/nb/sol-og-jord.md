---
route: /sol-og-jord/
title: Sol og jord – hva sier dataene?
nav: sol-og-jord
slug: sol-og-jord
description: Åtte temaer om forholdet mellom solaktivitet og Jorden – solinnstråling, temperatur, kosmisk stråling, nordlys, Maunder-minimumet, regionale klimamønstre, vulkaner og påstander uten støtte – med statistikk og evidensmerking.
---

Det er mange påstander om at solflekker «styrer» alt fra været til jordskjelv. Noen er godt dokumentert. Andre er svake hypoteser, og noen har ingen støtte i data. Denne delen av nettstedet tester dem med de samme åpne dataene du finner på [Data-siden](/dataserier/), og merker hver konklusjon med et av tre nivåer.

## De tre evidensnivåene

- [[a]] **Godt etablert.** Målt gjentatte ganger, med en kjent fysisk mekanisme og bred enighet i fagmiljøet. Eksempel: solaktivitet styrer geomagnetiske stormer.
- [[b]] **Omdiskutert hypotese.** Det finnes publiserte signaler eller mulige mekanismer, men evidensen er svak, motstridende eller ikke reprodusert. Eksempel: solens påvirkning på regionale vintermønstre i Atlanterhavet.
- [[c]] **Uten støtte.** Ingen robust statistisk sammenheng i data, ingen akseptert mekanisme, eller direkte motbevist. Eksempel: at solflekker forutsier børskurser.

Merkingen følger de samme fargene, ikonene og tekstene på alle sidene, slik at nivået aldri formidles bare med farge.

## Temaene

:::topics

## Slik testes påstandene

Hver side viser først dataene, deretter en statistisk analyse og til slutt en boks med vurdering av evidensen. Metodene er de samme på alle sidene:

- **Usikkerhet.** Korrelasjoner vises med 95 %-konfidensintervall, beregnet med *effektive frihetsgrader* som tar hensyn til at nabopunkter i en tidsserie ikke er uavhengige.
- **Signifikans.** p-verdier hentes fra *fase-surrogattester* (tilfeldige serier med samme frekvensinnhold som solflekkserien, men uten kobling til den andre serien). For hendelsesdata (vulkaner) brukes permutasjonstester.
- **Flere tester.** Når flere forsinkelser (lag) testes, korrigeres p-verdiene (Holm), og vi oppgir også en familievis p-verdi. Hver analyse oppgir hvor mange tester som ble kjørt.
- **Automatisk oppdatering.** Alle analysene kjøres på nytt i datapipelinen når nye data kommer inn. Tall i teksten hentes fra de genererte JSON-filene.

Antall tester i hver analyse per i dag: temperatur {{temperature.n_tests|n0}}, kosmisk stråling {{cosmic.n_tests|n0}}, geomagnetisk aktivitet {{geomag.n_tests|n0}}, regionale mønstre {{regional.n_tests|n0}}, vulkaner {{volcano.n_tests|n0}} og 1 for solinnstråling. I tillegg bruker simuleringene på siden om [påstander uten støtte](/sol-og-jord/pastander-uten-stotte/) {{spurious.n_tests|n0}} kunstige tester. Detaljer står på [Metode og kilder](/metode/#statistikk).

:::box Et viktig forbehold
Dataene her kan vise om en sammenheng finnes i målingene. De kan aldri alene bevise at en sammenheng er *kausal*, og at ingen statistisk sammenheng finnes betyr ikke at ingen fysisk påvirkning finnes – bare at den er for liten til å oppdages i dataene vi har. Kortere serier (som kosmisk stråling fra 1936, NAO fra 1950) gir få uavhengige solsykluser og dermed liten statistisk kraft.
:::

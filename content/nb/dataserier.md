---
route: /dataserier/
title: Data
nav: data
slug: data
description: Interaktive grafer for månedlig og årlig solflekktall, gruppesolflekktall, alle solsykluser lagt over hverandre, hemisfæriske data og sommerfugldiagram – med nedlasting som CSV og kildehenvisning.
---

Alle grafene kan zoomes ved å velge periode (fra/til eller en av hurtigknappene). Hver graf har en tabell som alternativ til figuren og en knapp for å laste ned dataene som CSV. CSV-filene begynner med kommentarlinjer (`#`) som oppgir kilde, lisens og kildehenvisning, slik at hentehenvisninger følger med dataene.

Dataene hentes direkte fra SILSO (Kongelig observatorium i Belgia), NASA og NOAA. Mer om lisens, oppdateringsfrekvens og kjente svakheter står på [Metode og kilder](/metode/).

## Månedlig og glattet månedlig solflekktall

:::chart data-ssn-monthly

Den glattede kurven er et 13-måneders glidende middel der de to endemånedene har halv vekt; det er den kurven som vanligvis brukes til å angi syklusmaksima og -minima. De siste seks månedene har derfor ingen glattet verdi ennå. Måneder merket som foreløpige (i tabellen) kan bli endret.

## Årlig solflekktall siden 1700

:::chart data-ssn-yearly

Før 1749 finnes bare årlige tall, og de bygger på få observasjoner. Usikkerheten er derfor stor og opplyst i tabellen som standardavvik, der det finnes.

## Gruppesolflekktall før 1749

:::chart data-group

Gruppesolflekktallet teller bare antall solflekkgrupper (ikke enkeltflekker) og kan derfor rekonstrueres lenger tilbake, helt til de første teleskopobservasjonene i 1610. Det finnes flere rekonstruksjoner som er uenige om langtidsnivået. Hoyt & Schatten (1998) har en tydelig stigning fra 1700-tallet til 1900-tallet, mens «backbone»-metoden til Svalgaard & Schatten (2016) ikke har den. Forskjellen er fortsatt ikke avklart av forskersamfunnet, og SILSO viser derfor flere serier. Perioden rundt 1645–1715 (Maunder-minimumet) er preget av få flekker i begge. Vær oppmerksom på at gruppetallet har en annen enhet enn solflekktallet.

## Alle solsykluser lagt over hverandre

:::chart data-cycles

Syklusstart er definert som minimum i det glattede solflekktallet. Syklus 1 begynner i {{cycles.cycles.0.start_t|my}}. Tabellen under grafen viser lengde, maksimum og tidspunkt for maksimum for alle sykluser. Siste syklus (25) er ikke ferdig, så lengden mangler.

## Nordlige og sørlige halvkule

:::chart data-hemispheric

Fra 1992 oppgir SILSO tall for nordlige og sørlige halvkule hver for seg. Halvkulene følger ikke alltid hverandre; asymmetrien kan være en viktig kilde til informasjon om hvordan Solens magnetfelt fungerer.

## Sommerfugldiagram

:::chart data-butterfly

Dataene er solflekkarealer etter breddegrad fra Royal Observatory Greenwich (1874–1976) og det amerikanske flyvåpenet/NOAA (1977–2016), samlet og vedlikeholdt av David Hathaway ved NASA Marshall. Arealene fra og med 1977 er multiplisert med 1,4 av Hathaway for å tilsvare Greenwich-målingene. Breddebinene er jevnt fordelt i sinus til breddegraden, så de dekker like store areal på Solen, men omregnet til grader er de ikke like brede.

## Datafiler

Alle ferdigbehandlede datafiler ligger åpent som JSON under `data/` på dette nettstedet, og `manifest.json` oppgir kilde, URL, tidspunkt for hentet data, siste datapunkt og antall rader for hver serie. Filene er endelige nedlastinger fra de opprinnelige kildene og må siteres etter kildenes retningslinjer (se [Metode og kilder](/metode/)).

| Fil | Innhold |
| --- | --- |
| [manifest.json](/data/manifest.json) | Kilder, lisenser, status og siste datapunkt |
| [ssn_monthly.json](/data/ssn_monthly.json) | Månedlig og glattet solflekktall 1749– |
| [ssn_yearly.json](/data/ssn_yearly.json) | Årlig solflekktall 1700– |
| [ssn_daily_recent.json](/data/ssn_daily_recent.json) | Daglig solflekktall siste ca. 800 dager + EISN |
| [group_yearly.json](/data/group_yearly.json) | Gruppesolflekktall 1610–2015 |
| [cycles.json](/data/cycles.json) | Solsykluser (start, lengde, maksimum) |
| [ssn_hemispheric_monthly.json](/data/ssn_hemispheric_monthly.json) | Halvkulene, 1992– |
| [butterfly.json](/data/butterfly.json) | Flekkareal etter breddegrad per Carrington-rotasjon |
| [cycle25_forecast.json](/data/cycle25_forecast.json) | NOAA-prognose for syklus 25 |

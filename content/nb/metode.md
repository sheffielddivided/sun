---
route: /metode/
title: Metode og kilder
nav: metode
slug: metode
description: Alle datakilder med lenker, lisens, oppdateringsfrekvens og kjente svakheter; de statistiske metodene; evidensnivåene og en referanseliste med fagfellevurderte artikler og IPCC AR6.
---

Alt på dette nettstedet kommer fra åpne data som lastes ned automatisk og behandles av en datapipeline i Python. Ingen tall er lagt inn for hånd; tall i teksten som avhenger av data hentes fra de genererte JSON-filene når siden bygges. Koden og alle beslutningene bak er åpne i [GitHub-depotet](https://github.com/sheffielddivided/sun) (filene `README.md`, `DECISIONS.md` og `pipeline/`).

## Datakilder

Hver kilde har en egen modul i pipelinen, som laster ned rådata, leser dem og kontrollerer dem. Kontrollen omfatter blant annet at formatet stemmer, at verdiene er plausible og at antallet rader ikke har falt dramatisk. Hvis en kilde ikke svarer eller kontrollen feiler, beholdes siste gode versjon av kilden, den merkes «Utdatert» her og i grafene, og de andre kildene oppdateres som vanlig. Tidspunktet under «Sist endret» viser når innholdet i kilden sist endret seg, ikke når pipelinen sist sjekket.

:::sources

## Statistikk

**Korrelasjon og usikkerhet.** Vi bruker Pearsons korrelasjonskoeffisient r. Siden nabopunkter i en tidsserie ikke er uavhengige, beregnes konfidensintervallet (95 %) med *effektive frihetsgrader*: N_eff = N·(1 − r₁ˣ·r₁ʸ)/(1 + r₁ˣ·r₁ʸ), der r₁ er lag-1-autokorrelasjonen i hver serie (Bretherton m.fl. 1999), og Fisher-transformasjonen brukes med N_eff − 3 frihetsgrader.

**Surrogattest.** For å teste signifikans lager vi {{temperature.n_surrogates|n0}} *fase-surrogater* av solflekkserien: fasene i Fourier-spekteret randomiseres, men amplitudene beholdes. Surrogatene har dermed samme middelverdi, varians og autokorrelasjon (inkludert 11-årssyklusen) som originalen, men er uavhengige av den andre serien. p-verdien er andelen surrogater som gir minst like stor |r| som observert, med +1 i teller og nevner (Theiler m.fl. 1992; Schreiber & Schmitz 2000). Metoden forutsetter stasjonære serier; derfor fjernes en trend fra temperaturserien før testing. Simuleringene på siden om [påstander uten støtte](/sol-og-jord/pastander-uten-stotte/) viser at testen holder seg nær nominelt nivå for ikke-trendende tilfeldige serier, men ikke er perfekt for to uavhengige trender.

**Flere tester.** Når flere forsinkelser (lag) testes, justerer vi p-verdiene per forsinkelse med Holm-metoden (Holm 1979). I tillegg oppgir vi en *familievis p-verdi*: andelen surrogater der største |r| over alle lag er minst like stor som den observerte største |r|. Den tar hensyn til at nabolag er korrelerte og er det vi bruker for å vurdere «det beste lagget». Hver analyse oppgir antallet tester. For at tallene skal være reproduserbare er alle tilfeldige tall trukket fra en generator med fast frø.

**Trender.** Lineære trender estimeres med minste kvadrater. Standardfeilen justeres for autokorrelasjon i residualene med en AR(1)-tilnærming.

**Vulkaner.** Nullfordelingen lages ved å forskyve hele utbruddsrekken sirkulært innenfor analysevinduet, {{volcano.n_shifts|n0}} ganger. Det bevarer antall utbrudd, klynging og langsiktige endringer i registrering, men bryter koblingen til solsyklusen. Superposed epoch-analysen bruker maksimum av de standardiserte avvikene over 11 forsinkelser som teststørrelse, slik at én global p-verdi tar hensyn til flere forsinkelser. Primærtestene korrigeres med Holm.

**Syklusdeteksjon.** Syklusminima er lokale minima i 13-måneders glattet solflekktall (±36 måneder, minst 7 år mellom). Syklus 1 er minimum rundt 1755. Syklusfase er tid siden minimum delt på syklusens lengde.

## Evidensnivåer

Alle temasider bruker de samme tre nivåene:

- [[a]] **Godt etablert:** målt gjentatte ganger, med kjent fysisk mekanisme og bred enighet i fagmiljøet (for eksempel IPCC-vurderinger eller lærebokkunnskap).
- [[b]] **Omdiskutert hypotese:** publiserte signaler eller plausible mekanismer, men svak, motstridende eller ikke reprodusert evidens, eller for få data til å avgjøre.
- [[c]] **Uten støtte:** ingen robust statistisk sammenheng og ingen akseptert mekanisme, eller direkte motbevist.

Nivået settes av oss ut fra publisert litteratur og testene på nettstedet. Det er en vurdering, ikke en måling, og kan endres hvis ny evidens kommer.

## Automatisk oppdatering

Tre planlagte kjøringer i GitHub Actions oppdaterer data: **daglig** (06:00 UTC: daglig solflekktall, F10.7, Kp og prognose), **månedlig** (den 2. hver måned: månedlige serier, temperatur, kosmisk stråling, NAO/ENSO, TSI og alle analyser) og **årlig** (15. januar: vulkandatabasen og årsserier). Etter hver kjøring valideres dataene, analysene kjøres, og nettstedet bygges og publiseres på nytt. Endringer i data lagres bare hvis innholdet faktisk har endret seg.

## Tilgjengelighet og personvern

Nettstedet bruker ingen sporing, ingen informasjonskapsler og ingen eksterne tjenester eller skrifttyper under kjøring; alt er bundlet. Eneste lagring i nettleseren er valget mellom lys og mørk modus (`localStorage`), som bare ligger hos deg. Grafer har tekstalternativer og tabeller som alternativ, og kan nås med tastatur. Fargene er kontrastsjekket for WCAG AA i både lys og mørk modus, og evidensnivåene merkes med både ikon og tekst, ikke bare farge.

## Kjente begrensninger

- Analysene viser *statistiske sammenhenger i målinger*; de kan ikke alene bevise årsakssammenhenger.
- Flere serier er korte (kosmisk stråling fra 1936, NAO og ENSO fra 1950) og dekker få solsykluser, så statistisk kraft er lav.
- Total solinnstråling før 1978 er modellert, ikke målt, og korrelasjonen mellom modellen og solflekktallet er delvis bygget inn.
- Rå nøytronmonitor-tellerater fra Oulu var ikke tilgjengelige da nettstedet ble bygget; Oulus publiserte modulasjonspotensial (Φ) brukes i stedet.
- Smithsonian-nettstedet for vulkandatabasen var nede ved bygging; dataene hentes fra deres WFS-tjeneste, som gir de samme dataene.
- Gruppesolflekktall før 1749 er usikre og rekonstruksjonene er uenige.
- Pipelinen overvåker ikke hvordan kildene endrer sine definisjoner over tid, utover de automatiske kontrollene.

## Referanser

Bare referanser vi har kontrollert at finnes, er tatt med.

- Bretherton, C. S., Widmann, M., Dymnikov, V. P., Wallace, J. M. & Bladé, I. (1999). The effective number of spatial degrees of freedom of a time-varying field. *Journal of Climate*, 12, 1990–2004.
- Carrington, R. C. (1859). Description of a singular appearance seen in the Sun on September 1, 1859. *Monthly Notices of the Royal Astronomical Society*, 20, 13–15.
- Clette, F., Svalgaard, L., Vaquero, J. M. & Cliver, E. W. (2014). Revisiting the Sunspot Number: A 400-year perspective on the solar cycle. *Space Science Reviews*, 186, 35–103.
- Clette, F. & Lefèvre, L. (2016). The new Sunspot Number: Assembling all corrections. *Solar Physics*, 291, 2629–2651.
- Cliver, E. W. & Dietrich, W. F. (2013). The 1859 space weather event revisited: limits of extreme activity. *Journal of Space Weather and Space Climate*, 3, A31.
- Coddington, O., Lean, J. L., Pilewskie, P., Snow, M. & Lindholm, D. (2016). A solar irradiance climate data record. *Bulletin of the American Meteorological Society*, 97, 1265–1282.
- Eddy, J. A. (1976). The Maunder Minimum. *Science*, 192, 1189–1202.
- Feulner, G. & Rahmstorf, S. (2010). On the effect of a new grand minimum of solar activity on the future climate on Earth. *Geophysical Research Letters*, 37, L05707.
- Galilei, G. (1613). *Istoria e dimostrazioni intorno alle macchie solari e loro accidenti*. Roma.
- Gao, C., Robock, A. & Ammann, C. (2008). Volcanic forcing of climate over the past 1500 years: An improved ice core-based index for climate models. *Journal of Geophysical Research*, 113, D23111.
- Gray, L. J. m.fl. (2010). Solar influences on climate. *Reviews of Geophysics*, 48, RG4001.
- Gray, L. J. m.fl. (2013). A lagged response to the 11 year solar cycle in observed winter Atlantic/European weather patterns. *Journal of Geophysical Research: Atmospheres*, 118, 13405–13420.
- Hale, G. E., Ellerman, F., Nicholson, S. B. & Joy, A. H. (1919). The magnetic polarity of sun-spots. *The Astrophysical Journal*, 49, 153–178.
- Hathaway, D. H. (2015). The solar cycle. *Living Reviews in Solar Physics*, 12, 4.
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics*, 6, 65–70.
- Hoyt, D. V. & Schatten, K. H. (1998). Group Sunspot Numbers: A new solar activity reconstruction. *Solar Physics*, 179, 189–219.
- IPCC (2021). *Climate Change 2021: The Physical Science Basis. Contribution of Working Group I to the Sixth Assessment Report of the Intergovernmental Panel on Climate Change*. Cambridge University Press. https://www.ipcc.ch/report/ar6/wg1/
- Ineson, S. m.fl. (2011). Solar forcing of winter climate variability in the Northern Hemisphere. *Nature Geoscience*, 4, 753–757.
- Kirkby, J. m.fl. (2011). Role of sulphuric acid, ammonia and galactic cosmic rays in atmospheric aerosol nucleation. *Nature*, 476, 429–433.
- Kopp, G. (2016). Magnitudes and timescales of total solar irradiance variability. *Journal of Space Weather and Space Climate*, 6, A30.
- Laken, B. A., Pallé, E., Čalogović, J. & Dunne, E. M. (2012). A cosmic ray-climate link and cloud observations. *Journal of Space Weather and Space Climate*, 2, A18.
- Lean, J. L. & Rind, D. H. (2008). How natural and anthropogenic influences alter global and regional surface temperatures: 1889 to 2006. *Geophysical Research Letters*, 35, L18701.
- Lenssen, N. J. L. m.fl. (2019). Improvements in the GISTEMP uncertainty model. *Journal of Geophysical Research: Atmospheres*, 124, 6307–6326.
- Lockwood, M. & Fröhlich, C. (2007). Recent oppositely directed trends in solar climate forcings and the global mean surface air temperature. *Proceedings of the Royal Society A*, 463, 2447–2460.
- Matzka, J., Stolle, C., Yamazaki, Y., Bronkalla, O. & Morschhauser, A. (2021). The geomagnetic Kp index and derived indices of geomagnetic activity. *Space Weather*, 19, e2020SW002641.
- Miller, G. H. m.fl. (2012). Abrupt onset of the Little Ice Age triggered by volcanism and sustained by sea-ice/ocean feedbacks. *Geophysical Research Letters*, 39, L02708.
- Morice, C. P. m.fl. (2021). An updated assessment of near-surface temperature change from 1850: The HadCRUT5 data set. *Journal of Geophysical Research: Atmospheres*, 126, e2019JD032361.
- Owens, M. J. m.fl. (2017). The Maunder minimum and the Little Ice Age: an update from recent reconstructions and climate simulations. *Journal of Space Weather and Space Climate*, 7, A33.
- Pierce, J. R. & Adams, P. J. (2009). Can cosmic rays affect cloud condensation nuclei by altering new particle formation rates? *Geophysical Research Letters*, 36, L09820.
- Robock, A. (2000). Volcanic eruptions and climate. *Reviews of Geophysics*, 38, 191–219.
- Russell, C. T. & McPherron, R. L. (1973). Semiannual variation of geomagnetic activity. *Journal of Geophysical Research*, 78, 92–108.
- Schreiber, T. & Schmitz, A. (2000). Surrogate time series. *Physica D*, 142, 346–382.
- Schwabe, H. (1844). Sonnen-Beobachtungen im Jahre 1843. *Astronomische Nachrichten*, 21, 233–236.
- Sloan, T. & Wolfendale, A. W. (2008). Testing the proposed causal link between cosmic rays and cloud cover. *Environmental Research Letters*, 3, 024001.
- Stothers, R. B. (1989). Volcanic eruptions and solar activity. *Journal of Geophysical Research*, 94, 17371–17381.
- Svalgaard, L. & Schatten, K. H. (2016). Reconstruction of the sunspot group number: The backbone method. *Solar Physics*, 291, 2653–2684.
- Svensmark, H. & Friis-Christensen, E. (1997). Variation of cosmic ray flux and global cloud coverage – a missing link in solar-climate relationships. *Journal of Atmospheric and Solar-Terrestrial Physics*, 59, 1225–1232.
- Theiler, J., Eubank, S., Longtin, A., Galdrikian, B. & Farmer, J. D. (1992). Testing for nonlinearity in time series: the method of surrogate data. *Physica D*, 58, 77–94.
- Usoskin, I. G. (2017). A history of solar activity over millennia. *Living Reviews in Solar Physics*, 14, 3.
- Usoskin, I. G., Bazilevskaya, G. A. & Kovaltsov, G. A. (2011). Solar modulation parameter for cosmic rays since 1936 reconstructed from ground-based neutron monitors and ionization chambers. *Journal of Geophysical Research*, 116, A02104.
- Wittmann, A. D. & Xu, Z. T. (1987). A catalogue of sunspot observations from 165 BC to AD 1684. *Astronomy and Astrophysics Supplement Series*, 70, 83–94.
- Yau, K. K. C. & Stephenson, F. R. (1988). A revised catalogue of Far Eastern observations of sunspots (165 BC to AD 1918). *Quarterly Journal of the Royal Astronomical Society*, 29, 175–197.

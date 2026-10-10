# Wissenschaftliche Begutachtung der glazial-seismischen Sensitivitätsanalyse

## Gesamturteil

Die wissenschaftliche Logik von v0.2 ist insgesamt **vertretbar als explorative bzw. prospektiv-operationalisierte Sensitivitätsanalyse**, aber an mehreren Stellen ist die Sprache derzeit stärker als das, was die Modelle identifizieren können. Der wichtigste begriffliche Punkt betrifft ETAS: Das geschätzte \(\mu(t)\) ist ein **ETAS-Hintergrund bzw. eine Residualintensität nach Abzug des im Modell repräsentierten Triggerings**, nicht eindeutig eine „forcing-driven background rate“. Gerade Kumazawa & Ogata weisen darauf hin, dass ein nichtstationärer ETAS-Hintergrund verschiedene externe oder vom Katalog bzw. Modell nicht erklärte Beiträge aufnehmen kann; er ist deshalb kein eindeutiger physikalischer Forcing-Parameter. citeturn23search0

Mein Urteil zu den sechs Kernfragen ist:

| Thema | Urteil |
|---|---|
| ETAS-Zerlegung | **Ja, statistisch defensibel**, insbesondere gegenüber einem gemeinsamen freien Fit; aber nicht kausal identifiziert. \(t_{\max}=1\) Jahr und \(p\) am Rand machen insbesondere \(\mu\)-Niveaus und Langzeitzerlegung stark modellabhängig. fileciteturn3file0L2-L2 |
| Alaska-Hintergrundtrend | Die im Repository vertretene **Netz-/Katalogartefakt-Deutung ist die plausibelste**. Der formale präregistrierte Test bleibt mathematisch positiv, ist aber keine belastbare Evidenz für glaziales Forcing. fileciteturn6file0L2-L2 |
| „Masked background rise“ | Als **deskriptive, konservative Regel sinnvoll**, als statistischer Test weniger sauber. Der Nullbefund schließt große Effekte in gut beobachteten Regionen eher aus, moderate Effekte – vor allem Island/Grönland – kaum. fileciteturn6file0L2-L2 |
| Körpergezeiten | Der Body-tide-Test ist technisch brauchbar, aber **kein Test der vollen Gezeitenbelastung**. Das Fehlen von Ocean Tide Loading schränkt gerade die vier genannten Küsten-/Inselregionen stark ein. fileciteturn2file0L2-L2 |
| Lag-Modell | Die Sasgen-Werte als Sensitivitätsparameter zu übernehmen ist legitim; die Übersetzung **LT \(\rightarrow T_e\)** und **Asthenosphärenviskosität \(\rightarrow\) Halbraumviskosität** ist jedoch nur eine grobe Modellabbildung. Das Ergebnis zur „elastischen Fraktion“ ist teilweise physikalisch nachvollziehbar, teilweise durch die Modellarchitektur vorgegeben. fileciteturn14file0L2-L2 |
| Prospektiver Test | C2 ist konzeptionell gut angelegt. Vor Beginn des Fensters sollte aber die **exakte Zielgröße und Varianzformel eindeutig eingefroren** werden. Ich sehe eine reale Inkonsistenz beim Faktor \(1.25\), eine kleine systematische Baseline/Future-Asymmetrie und eine problematische i.i.d.-Annahme für die Jahresstreuung. fileciteturn1file0L2-L2 fileciteturn11file0L2-L2 |

Der zentrale positive Punkt ist, dass das Repository selbst die meisten dieser Grenzen bereits ungewöhnlich offen dokumentiert: \(p\) am Rand, Netzgeschichte, fehlendes Ocean Loading und die vereinfachte GIA-Übertragung werden ausdrücklich genannt. fileciteturn7file0L2-L2 fileciteturn8file0L2-L2 Die Hauptkorrektur, die ich empfehlen würde, ist daher weniger ein kompletter Methodenwechsel als eine **strengere Interpretation der Estimanden und eine Schließung einiger statistischer Schlupflöcher vor dem prospektiven Fenster**.

## ETAS-Zerlegung: sinnvoller Schätzer, aber keine eindeutige Trennung von Forcing und Nachbeben

Das Modell

\[
\lambda(t)=\mu_y(t)+
\sum_{t_j<t,\;t-t_j\le 1\,{\rm yr}}
K\,e^{\alpha(m_j-M_c)}
(t-t_j+c)^{-p}
\]

mit jährlich konstantem \(\mu_y\) ist eine vernünftige Minimalform eines nichtstationären zeitlichen ETAS. Die Literatur unterstützt grundsätzlich die Idee, einen zeitvariablen Hintergrund von selbstangeregtem Triggering zu trennen. Kumazawa & Ogata verwenden nichtstationäre ETAS-Komponenten gerade dafür, Änderungen der Hintergrundintensität bzw. Produktivität von normaler Nachbebenaktivität zu unterscheiden; gleichzeitig interpretieren sie den Hintergrund ausdrücklich breiter als nur einen bestimmten äußeren physikalischen Antrieb. citeturn23search0 Das Repository setzt diese Idee wesentlich einfacher um, mit Jahresbins und stationären Triggerparametern. fileciteturn1file0L2-L2

### Der zweistufige Fit ist hier vernünftiger als der gemeinsame Fit

Die Entscheidung, zunächst ein stationäres ETAS für \(K,\alpha,c,p\) zu fitten und anschließend bei festgehaltenen Triggerparametern die jährlichen \(\mu_y\) zu bestimmen, halte ich angesichts der eigenen Recovery-Studie für **gut begründet**. Im synthetischen linearen Szenario liefert der gemeinsame Fit beispielsweise \(p=1.69\) statt \(1.15\), eine Verzweigungsrate von ungefähr \(0.33\) statt \(0.5\) und einen um rund \(29\%\) zu hohen \(\mu\)-Level; im zweistufigen Fit werden die Trends besser wiedergewonnen, wenn auch die absoluten \(\mu\)-Niveaus weiterhin verzerrt sein können. Beim künstlichen „masked rise“ wird der wahre Trend \(0.130\) pro Jahrzehnt als \(0.119\) geschätzt. fileciteturn3file0L2-L2

Das ist statistisch plausibel: Werden gleichzeitig Dutzende \(\mu_y\) und ein sehr langer Omori-Schwanz geschätzt, konkurrieren zwei flexible Komponenten darum, dieselben längerfristigen Ereignishäufungen zu erklären. Das Fixieren der Triggerparameter reduziert diese Nichtidentifizierbarkeit. Genau eine solche Stabilisierung durch Fixieren anderer ETAS-Parameter wird auch in der nichtstationären ETAS-Literatur verwendet. citeturn23search0

Allerdings bezahlt der zweistufige Fit dafür mit einer anderen Annahme: **Jegliche echte Zeitvariation von Produktivität oder Nachbebenphysik wird nun bevorzugt \(\mu_y\) zugeschrieben.** Ändern sich etwa \(K\), \(\alpha\), \(p\), Katalogvollständigkeit, Magnitudenskala oder die räumliche Mischung der aktiven Störungen, kann der zweite Schritt das als Hintergrundänderung darstellen. Das Repository hält \(K,\alpha,c,p\) über 1995–2025 konstant und arbeitet rein zeitlich, ohne räumlichen ETAS-Kern. fileciteturn2file0L2-L2

Deshalb würde ich in Manuskript und Ergebnistext konsequent von

> **„ETAS-residual background intensity“ bzw. „ETAS-Hintergrundrate“**

sprechen und **„forcing-driven background“ nur als mögliche physikalische Interpretation**, nicht als identifizierte Größe. Das ist keine semantische Spitzfindigkeit: Die entscheidende wissenschaftliche Frage ist gerade, ob \(\mu_y\) Gletscherforcing oder etwas Nichtmodelliertes auffängt.

### \(p=1.0001\) in sieben von acht Regionen ist ein ernstes Diagnosezeichen

Dass \(p\) in sieben Regionen exakt an der unteren Schranke \(1.0001\) liegt, ist meines Erachtens die wichtigste technische Warnung des M2-Modells. Die Baselines bestätigen dies für alle Regionen außer Island. fileciteturn18file0L2-L2 Ein Optimum auf der Schranke bedeutet nicht, dass der wahre Omori-Exponent tatsächlich \(p\simeq1\) ist. Es bedeutet zunächst nur, dass die Likelihood innerhalb des zugelassenen Modells einen noch langsameren Zerfall bevorzugen würde oder dass andere Fehlanpassungen – etwa räumliche Heterogenität, Schwärme oder Katalogeffekte – durch einen langen zeitlichen Schwanz kompensiert werden.

Bei \(p\rightarrow1\) wird die integrierte Omori-Masse besonders empfindlich gegen die gewählte maximale Nachbebenzeit. Für exakt \(p=1\),

\[
I(T)=\int_0^T\frac{dt}{t+c}
=\log\frac{T+c}{c}.
\]

Nimmt man beispielsweise das synthetische Benchmark-\(c=0.002\) Jahre, dann enthält das erste Jahr nur

\[
\frac{\log[(1+c)/c]}{\log[(5+c)/c]}
\simeq 0.79
\]

der Omori-Masse der ersten fünf Jahre. Rund ein Fünftel der fünfjährigen Triggerkomponente liegt also jenseits des verwendeten \(t_{\max}\). Gegenüber einem dreißigjährigen Fenster sind es nur etwa \(65\%\). Diese Zahlen sind lediglich eine Illustration – \(K\) und \(c\) werden im realen Fit neu angepasst –, zeigen aber, warum ein harter Cutoff gerade nahe \(p=1\) nicht harmlos ist. Die eigenen Alaska-Sensitivitätsläufe bestätigen praktisch, dass die Wahl relevant ist: bei \(t_{\max}=3\) Jahren sinkt der vollständige H2.1-Kontrast von ungefähr \(+0.41\) auf \(+0.23\pm0.21\) pro Jahrzehnt und ist nicht mehr signifikant. fileciteturn6file0L2-L2

Die Richtung des Bias ist dabei nicht immer einfach „\(\mu\) zu hoch“. Ereignisse, die mehr als ein Jahr nach einem großen Vorläufer auftreten, **können definitionsgemäß nicht mehr diesem Vorläufer zugerechnet werden** und landen tendenziell im Hintergrund oder bei jüngeren Triggern. Wann die großen Sequenzen auftreten, bestimmt dann, ob daraus ein positiver oder negativer \(\mu\)-Trend entsteht. Das macht Niveau und Trend teilweise vom historischen Sequenzmuster abhängig.

Noch problematischer ist die Interpretation der angegebenen Verzweigungsverhältnisse. Bei SE Alaska werden \(0.84\), bei Grönland \(0.89\) und bei Island \(0.90\) berichtet. fileciteturn6file0L2-L2 Wenn \(p\) praktisch eins ist, sind solche Werte stark **cutoff-abhängige Verzweigungsmaße innerhalb des einjährigen Kerns** und sollten nicht als physikalische, vollständige Reproduktionszahl eines unbegrenzten ETAS-Prozesses gelesen werden.

### Die Recovery-Studie reicht nicht aus, um den Randfall vollständig zu validieren

Die synthetische Prüfung ist sinnvoll, aber sie simuliert mit einem wahren \(p=1.15\), einer Verzweigungsrate um \(0.5\) und nur acht Realisationen pro nichtstationärem Szenario. Die reale Anwendung liegt dagegen in sieben von acht Fällen direkt an \(p=1.0001\), teilweise mit geschätzten Verzweigungsanteilen nahe \(0.9\). fileciteturn3file0L2-L2 Damit ist die Recovery-Studie eine gute **Unit-/sanity calibration**, aber keine starke Demonstration, dass die tatsächliche Randregime-Inferenz korrekt kalibriert ist.

Das gilt auch für den Faktor \(1.25\). Die 40 zusätzlichen stationären Nullsimulationen plus acht Recovery-Kataloge ergeben \(sd(z)\approx1.11\) für Trends und \(1.18\) für Fensterverhältnisse; daraus wird konservativ \(1.25\) gewählt. fileciteturn3file0L2-L2 Das ist eine vernünftige empirische Sicherheitsmarge, aber kein Ersatz für eine Simulation unter den tatsächlich beobachteten schwierigen Eigenschaften – \(p\) am Rand, hohe Branching Ratio, Netzsprünge, Schwärme und räumliche Heterogenität.

**Mein Urteil zur ersten Frage:** Der zweistufige Schätzer ist für dieses Projekt defensibel und wahrscheinlich klar besser als der gemeinsame Fit. Was er trennt, ist aber **„vom stationären temporal-ETAS erklärte Clusterung“ versus „Restintensität“**, nicht eindeutig **„Nachbeben“ versus „glaziales Forcing“**. Der einjährige Cutoff zusammen mit einem randständigen \(p\) ist eine substantielle Modellgrenze, nicht nur ein technisches Detail.

## Der Alaska-Befund: Netzgeschichte ist die plausibelste Erklärung

Formal gibt es am präregistrierten Test nichts wegzuinterpretieren: Für 1995–2025 beträgt der geschätzte Unterschied zwischen SE Alaska und Interior Alaska \(+0.405\pm0.138\) in \(\log\mu\) pro Jahrzehnt, \(z=2.93\), einseitig \(p=0.0017\), mit BH-adjustiertem Wert ungefähr \(0.005\). Nach der vorab festgelegten Entscheidungsregel ist H2.1 damit positiv. fileciteturn6file0L2-L2

Aber „der präregistrierte statistische Test ist positiv“ und „es gibt Evidenz für glazial verursachtes Hintergrundwachstum“ sind zwei verschiedene Aussagen.

### Warum die Artefaktdeutung stark ist

Vier Befunde zusammen machen die Netz-/Katalogerklärung aus meiner Sicht zur klar plausibelsten:

Erstens liegt die Hebelwirkung fast vollständig in der frühen Phase. In SE Alaska treten 1997–2002 je nach Jahr nur 62–196 Ereignisse auf, gegenüber 438–2059 pro Jahr in 2003–2024. Interior Alaska zeigt ebenfalls wesentlich kleinere frühe Zahlen, etwa 257–546 in 1998–2001 gegenüber 654–1930 ab 2004. Gleichzeitig liegt das jährliche EMR-\(M_c\) um das Jahr 2000 in beiden Regionen bei etwa \(2.3{-}2.4\), also oberhalb des fest verwendeten \(M_{c,\rm ref}=2.1\). fileciteturn6file0L2-L2 Ein ETAS-Hintergrund kann eine solche Änderung der Erfassungswahrscheinlichkeit unmittelbar als Änderung der zugrunde liegenden Ereignisrate darstellen.

Zweitens verschwindet der Kontrast mit dem sachlich naheliegenden, wenn auch nicht präregistrierten Start 2003: \(+0.11\pm0.16\) pro Jahrzehnt, \(z=0.71\). Auch mit gemeinsamem Schätzer bleibt ab 2003 nur \(+0.16\pm0.14\), \(z=1.11\); mit dem dreijährigen Triggerfenster wird der post-2003-Kontrast sogar negativ. fileciteturn6file0L2-L2 Ein echter über Jahrzehnte zunehmender glazialer Antrieb müsste nicht zwingend ab 2003 einen monotonen \(\mu\)-Trend erzeugen, aber die vollständige Abhängigkeit des Signals von genau der katalogisch problematischen Frühphase ist für eine physikalische Interpretation ungünstig.

Drittens ist die Kontrolldifferenz kein vollständiger Schutz gegen diesen Fehler. Sie eliminiert nur Netzänderungen, die die beiden Regionen hinsichtlich effektiver Vollständigkeit, Magnitudenskala und Lokalisierungsleistung hinreichend ähnlich betreffen. Das Repository sagt dies ausdrücklich. fileciteturn1file0L2-L2 Unterschiedliche Stationsgeometrie, unterschiedliche Entfernung zum Netz und unterschiedliche Magnitudenverteilungen können aus einer gemeinsamen Netzmodernisierung einen differentiellen Trend erzeugen.

Viertens hat der ETAS-Fit selbst genau in Alaska den problematischen Randfall: \(p=1.0001\), Branching Ratio \(0.84\) in SE Alaska und \(0.64\) in Interior Alaska. fileciteturn6file0L2-L2 Das bedeutet, dass ein beträchtlicher Teil der Differenz zwischen Regionen davon abhängt, wie das zeitliche Modell Triggering und Hintergrund aufteilt.

Kumazawa & Ogata betonen grundsätzlich, dass der ETAS-Hintergrund auch Einflüsse aufnehmen kann, die nicht in der beobachteten Ereignishistorie und Modellstruktur enthalten sind. citeturn23search0 Genau deshalb ist die Kombination aus Vollständigkeitswechsel und zeitlichem Modell hier eine hinreichende Alternativerklärung.

### Welche anderen Erklärungen noch realistisch sind

Neben einem reinen Stations-/Detektionsartefakt kommen mehrere Alternativen in Betracht, ohne dass eine davon durch H2.1 getrennt identifizierbar wäre.

**Magnituden- und Prozessierungsänderungen** sind praktisch dieselbe Fehlerfamilie wie Netzgeschichte, müssen aber nicht durch neue Stationen entstehen. Eine Änderung der Magnitudenbestimmung, des Detektionsalgorithmus, der Ereignisassoziation oder der Katalogrevision kann oberhalb eines scheinbar konstanten \(M_c\) dennoch regional unterschiedliche Effekte hinterlassen. Dass das jährliche EMR-\(M_c\) den verwendeten Schwellenwert in der Frühphase überschreitet, ist dafür direkte interne Evidenz. fileciteturn6file0L2-L2

**Nichtstationäre Triggerproduktivität** kann ebenfalls als \(\mu\)-Änderung erscheinen. Der zweistufige Fit zwingt \(K,\alpha,c,p\) über drei Jahrzehnte konstant. Wenn sich beispielsweise die räumlich aktive Störungspopulation ändert oder einzelne große Sequenzen eine andere Produktivität besitzen, kann der Jahres-Hintergrund diese Abweichung absorbieren. fileciteturn13file0L2-L2

**Langfristige Nachbeben- und Clusteranteile jenseits eines Jahres** sind besonders wegen \(p\simeq1\) relevant. Der \(t_{\max}=3\)-Jahre-Test ist hier sehr aufschlussreich: Dass bereits diese begrenzte Erweiterung den Alaska-Kontrast stark abschwächt, zeigt, dass die Trennung nicht invariant gegenüber einer plausiblen Wahl des Triggerhorizonts ist. fileciteturn6file0L2-L2

**Reale nichtglaziale äußere Forcings oder tektonische Transienten** würden von diesem Modell ebenfalls als Hintergrund aufgefasst. Nichtstationäres ETAS kann konzeptionell äußere Stresseinflüsse erfassen, identifiziert deren Ursache aber nicht allein aus \(\mu(t)\). citeturn23search0

Schließlich ist ein **echter glazialer Beitrag** nicht logisch ausgeschlossen. Aber H2.1 liefert dafür gerade keinen spezifischen Fingerabdruck: Das Signal fällt mit der katalogisch schwächsten Epoche zusammen und besteht im moderneren Teil des Katalogs nicht fort. Ohne unabhängige Übereinstimmung mit einer Last- oder Stressgeschichte wäre die physikalische Attribution deshalb Überinterpretation.

Ich würde die Schlussfolgerung daher so formulieren:

> Der präregistrierte H2.1-Test ist formal positiv. Der Effekt ist jedoch nicht robust gegen die Beschränkung auf die katalogisch homogenere Zeit ab 2003 und gegen einen längeren ETAS-Triggerhorizont. Zusammen mit der zeitvariablen Vollständigkeit spricht dies stärker für einen Katalog-/Modellartefakt als für einen glazial verursachten Hintergrundtrend.

Das ist etwas präziser als „H2.1 war falsch“: Die **Entscheidungsregel** wurde korrekt ausgelöst; die **physikalische Interpretation** scheitert an einer nicht vorab abgesicherten Störvariable.

## „Masked background rise“: gute Heuristik, aber ein schwacher Nullbefund

Die Klassifikationsidee ist konzeptionell attraktiv. Ein „masked rise“ verlangt gleichzeitig

\[
\mathrm{CI}_{95,\rm lower}
\left[
\frac{\mu_{2020-25}}{\mu_{2008-19}}
\right]>1
\]

und

\[
\frac{N_{2020-25}/T_2}
     {N_{2008-19}/T_1}<1.
\]

Damit soll genau das gesuchte Muster operationalisiert werden: Der ETAS-Hintergrund steigt überzeugend, während die rohe Gesamtseismizität zurückgeht. Die anderen Kategorien – unmaskierter Anstieg, echte Hintergrundabnahme, keine auflösbare Änderung – sind logisch konsistent. fileciteturn1file0L2-L2

Als **deskriptive Klassifikation** ist das sinnvoll. Ich würde es aber nicht wie einen kalibrierten Hypothesentest interpretieren.

### Die harte Grenze bei der Gesamtzahl ist zu grob

Für die \(\mu\)-Komponente wird Unsicherheit verlangt, für die Gesamtzahl dagegen nur ein Punktschätzer \(<1\). Ein Verhältnis von \(0.99\) wäre damit formal „quiet“, ein Verhältnis von \(1.01\) nicht, unabhängig von der Zählunsicherheit. fileciteturn13file0L2-L2 Das ist als einfaches Flag akzeptabel, aber nicht als statistisch symmetrische Definition.

Außerdem stammen \(\mu\)-Verhältnis und Gesamtverhältnis aus **denselben Ereignissen**. Sie sind nicht unabhängige Evidenzquellen. Eine höhere Zahl von Ereignissen beeinflusst sowohl die Gesamtzahl als auch die ETAS-Zerlegung. Die Konjunktion „95%-Untergrenze für \(\mu\) über eins und Gesamtverhältnis unter eins“ besitzt deshalb nicht automatisch eine bekannte gemeinsame Fehlerwahrscheinlichkeit.

Ein saubererer inferentieller Ansatz wäre ein zweidimensionaler Kontrast aus

\[
\Delta_\mu=
\Delta\log\mu_{\rm glacier}
-
\Delta\log\mu_{\rm control}
\]

und

\[
\Delta_N=
\Delta\log R_{\rm total,glacier}
-
\Delta\log R_{\rm total,control},
\]

mit gemeinsamer Simulation unter dem Nullmodell. Für die aktuelle v0.2-Klassifikation ist die einfachere Regel dennoch vertretbar, solange sie ausdrücklich **deskriptiv** bleibt – was die Präregistrierung bereits tut. fileciteturn1file0L2-L2

### Der Nullbefund ist nur regional und effektgrößenabhängig informativ

Die beobachteten Resultate sind:

| Region | \(\mu\)-Verhältnis | Gesamtverhältnis | Lesart |
|---|---:|---:|---|
| SE Alaska | 1.41, KI 1.07–1.85 | 2.33 | Hintergrundanstieg, aber nicht maskiert |
| Interior Alaska | 0.87, KI 0.71–1.07 | 0.91 | nicht auflösbar |
| NZ Südalpen | 0.62, KI 0.45–0.86 | 0.32 | Hintergrundabnahme |
| NZ Wellington | 0.99, KI 0.67–1.47 | 0.71 | nicht auflösbar |
| Alpen | 1.22, KI 0.96–1.56 | 1.30 | nicht auflösbar |
| Nordschweiz | 1.94, KI 1.29–2.91 | 2.04 | nicht maskierter Anstieg |
| Island | 1.56, KI 0.85–2.86 | 0.19 | Richtung passt, Unsicherheit zu groß |
| Grönland | 1.12, KI 0.75–1.67 | 1.68 | nicht auflösbar |

fileciteturn6file0L2-L2

Island ist dabei besonders lehrreich. Die rohe Rate sinkt um ungefähr \(81\%\), während der Punktschätzer des ETAS-Hintergrunds um \(56\%\) steigt – also genau in Richtung des postulierten Musters. Die Unsicherheit ist aber riesig, und zusätzlich ist \(\alpha\approx0.02\), was darauf hindeutet, dass das Standard-ETAS die dortigen Schwärme schlecht beschreibt. fileciteturn6file0L2-L2 Daher ist „kein masked rise in Island“ wesentlich schwächer als „gute Evidenz gegen einen masked rise“.

Aus den publizierten Konfidenzintervallen lässt sich grob die Power abschätzen. Unter approximativ normalem \(\log\)-Verhältnis braucht ein Test mit Kriterium „untere 95%-Grenze \(>1\)“ für etwa 80% Power einen wahren Effekt von ungefähr

\[
\exp[(1.96+0.84)SE_{\log R}].
\]

Damit ergeben sich aus den vorhandenen Intervallen ungefähr folgende Schwellen:

| Region | grobe wahre \(\mu\)-Ratio für 80% Power |
|---|---:|
| SE Alaska | etwa 1.5 |
| Interior Alaska | etwa 1.3 |
| NZ Südalpen | etwa 1.6 |
| NZ Wellington | etwa 1.8 |
| Alpen | etwa 1.4 |
| Nordschweiz | etwa 1.8 |
| Island | etwa 2.4 |
| Grönland | etwa 1.8 |

Diese Rechnung ist eine Näherung aus den berichteten Intervallen und berücksichtigt weder die Unsicherheit des Gesamtverhältnisses noch die Abhängigkeit zwischen ETAS- und Rohzählstatistik. Die Ausgangsdaten dafür stehen in den H2.2-Ergebnissen. fileciteturn6file0L2-L2

Damit ist der Nullbefund **durchaus informativ gegen große maskierte Hintergrundanstiege in den gut beobachteten Regionen**, insbesondere SE Alaska. Er ist hingegen keine starke Evidenz gegen moderate Effekte und in Island beziehungsweise Grönland klar schwach.

Die synthetische „masked-rise“-Simulation zeigt, dass der zweistufige Schätzer einen vorgegebenen starken Trend prinzipiell wiederfinden kann; sie ist aber mit acht Katalogen kein eigener Power-Nachweis für die konkrete binäre H2.2-Klassifikation. fileciteturn3file0L2-L2

Daher würde ich die Ergebnisformulierung von

> „kein masked background rise“

zu

> **„keine Region erfüllt das vorab definierte masked-background-rise-Kriterium; moderate Effekte sind insbesondere in Island und Grönland nicht ausgeschlossen“**

erweitern.

## Gezeiten: die skalare Körperdehnung ist korrekt, die physikalische Aussage aber eng

### Die Formel für die Flächendehnung ist als Grad-zwei-Proxy in Ordnung

Für ein Grad-\(n\)-Gezeitenpotential ergibt sich an einer kugelförmigen elastischen Oberfläche aus radialer Love-Zahl \(h_n\) und horizontaler Shida-Zahl \(l_n\) für die horizontale Flächendehnung eine Kombination der Form

\[
\varepsilon_A
=
\frac{\left[2h_n-n(n+1)l_n\right]W_n}{ga}.
\]

Für \(n=2\) folgt damit genau

\[
\varepsilon_A
=
(2h-6l)\frac{W_2}{ga}.
\]

Die verwendete Struktur ist daher physikalisch konsistent als **Grad-zwei-Oberflächen-Flächendehnung einer sphärisch symmetrischen elastischen Erde**. Die IERS Conventions geben als nominale Grad-zwei-Werte \(h=0.6078\) und \(l=0.0847\) an. citeturn14view0 Das Repository verwendet \(h=0.6114\), \(l=0.0832\); die resultierende Skalierung \(2h-6l\) ist nur rund \(2.3\%\) größer als mit den nominalen IERS-Werten, sodass die Amplitude geringfügig verändert wird, nicht aber die Phase eines rein positiv skalierten Signals. Das Repository dokumentiert dieselbe Größenordnung. fileciteturn2file0L2-L2

Für einen **Schuster-Test gegen die Phase eines skalaren Körpergezeiten-Proxys** ist das ausreichend.

Nicht ausreichend ist die Größe dagegen als vollständiger physikalischer Triggerstress. Ein Erdbeben reagiert nicht auf Flächendehnung als solche, sondern auf die auf der konkreten Störungsfläche aufgelösten Änderungen von Schubspannung und effektiver Normalspannung – beziehungsweise auf Änderungen des Coulomb-Stresses, gegebenenfalls unter Beteiligung des Porendrucks. Frühe systematische Tidal-triggering-Studien berechneten deshalb einen vollständigen theoretischen Spannungstensor einschließlich Körper- und Ozeanauflast und fanden, dass die relevante Phase von der Störungsgeometrie abhängen kann. citeturn23search1

Daher würde ich H3 exakt so benennen:

> **Test auf Korrelation mit der Phase der Grad-zwei-Körpergezeiten-Flächendehnung**

und nicht allgemein als Test auf „tidal triggering“.

### Das fehlende Ocean Tide Loading ist für die vier genannten Regionen eine starke Einschränkung

Tsuruoka, Ohtake & Sato berechneten für ihren Gezeiten-Triggering-Test explizit **sowohl Solid Earth Tide als auch Ocean Tide Loading** am Hypozentrum. citeturn23search1 Das ist wichtig, weil die Ozeanmasse eine zusätzliche zeitvariable Oberflächenlast erzeugt, deren lokale Amplitude und Phase durch Küstengeometrie, Bathymetrie und die Dynamik der jeweiligen Gezeitenkonstituenten bestimmt werden. Sie ist daher weder notwendigerweise klein noch einfach phasengleich mit der astronomisch berechneten Körpergezeit. citeturn23search1

Genau deshalb sind **SE Alaska, Neuseeland, Island und Grönland** die ungünstigsten Orte, um aus einem Body-tide-only-Nullresultat eine allgemeine Aussage über Gezeitentriggering abzuleiten. Das Repository erkennt das selbst ausdrücklich an und nennt Ocean Tide Loading als wesentliche fehlende Komponente. fileciteturn2file0L2-L2

Wie groß der Fehler in jeder Region tatsächlich ist, kann man ohne eine regionale Ozeanlastberechnung nicht seriös quantifizieren. Insbesondere sollte man nicht behaupten, die Ozeanlast dominiere zwingend an jedem Bebenort. Aber es ist durchaus möglich, dass

\[
\varepsilon_{\rm full}(t)
=
\varepsilon_{\rm body}(t)
+
\varepsilon_{\rm ocean}(t)
\]

eine deutlich andere Amplitude und Phase besitzt als \(\varepsilon_{\rm body}(t)\) allein. In einem Phasentest ist ein Phasenfehler besonders schädlich: Selbst ein realer Zusammenhang mit der Gesamtlast kann im Body-only-Schuster-Test abgeschwächt oder ausgelöscht werden.

Entsprechend ist der SE-Alaska-MDE von \(a=0.068\) zwar eine brauchbare Aussage über **Modulation relativ zur verwendeten Körpergezeitenphase** – bei 4517 declusterten Ereignissen wären große body-phase-synchrone Modulationen gefunden worden –, aber er ist **keine MDE für die volle gezeiteninduzierte Coulombspannung**. Dasselbe gilt noch stärker für Island mit MDE \(\sim0.126\) und Grönland mit \(\sim0.194\). fileciteturn6file0L2-L2

Das Nullresultat H3 sollte deshalb physikalisch eng interpretiert werden:

> Es gibt keine nachweisbare Seismizitätsmodulation mit der modellierten Körpergezeiten-Flächendehnungsphase. Eine Modulation durch die volle lokale Gezeitenspannung einschließlich Ozeanauflast wurde nicht getestet.

Das ist eine solide Nullhypothese. Die weitergehende Aussage „keine tidal triggering evidence“ wäre zu breit.

## Lagmodell: sinnvolle Sensitivitätsstudie, aber die Sasgen-Parameter sind nicht direkt dieselben Modellparameter

Das M4-Modell verwendet für Alaska nach Sasgen et al. eine Asthenosphärenviskosität von \(3\times10^{18}\,\mathrm{Pa\,s}\) und eine Lithosphärendicke von etwa \(30\) km, für Island \(10^{18}\,\mathrm{Pa\,s}\) und etwa \(30\) km; ein Island-GNSS-Fall mit ungefähr \(40\) km wird ebenfalls betrachtet. Diese Werte entsprechen den im Sasgen-Modell untersuchten bzw. bevorzugten regionalen Rheologien. citeturn16view0 Das Repository übernimmt sie korrekt als Sensitivitätswerte. fileciteturn14file0L2-L2

Die Frage ist aber, ob die **Abbildung** dieser Werte auf die Parameter des einfachen Lagmodells physikalisch konsistent ist.

### Lithosphärendicke ist nicht identisch mit effektiver elastischer Dicke

Im Repository wird aus der Lithosphärendicke \(T_e\) eine dünnplattige Flexionssteifigkeit

\[
D=\frac{E T_e^3}{12(1-\nu^2)}
\]

gebildet und daraus

\[
C(k)=
\frac{1}
{1+Dk^4/(\rho_m g)}
\]

als wellenlängenabhängiger Kompensationsfaktor. fileciteturn15file0L2-L2

Sasgen et al. verwenden dagegen ein geschichtetes, selbstgravitierendes Maxwell-viskoelastisches Erdmodell, in dem die Lithosphärendicke die Grenze einer elastischen Schicht gegenüber viskoelastischen Schichten charakterisiert; die Asthenosphäre besitzt endliche Mächtigkeit und darunter liegen weitere Mantelschichten. citeturn16view2 Das ist nicht mathematisch dasselbe wie eine unendlich ausgedehnte dünne elastische Platte auf einem viskosen Halbraum.

Eine reale lithosphärische Schichtdicke und eine aus Oberflächenlasten abgeleitete effektive elastische Dicke \(T_e\) können verwandt sein, müssen aber numerisch nicht gleich sein. Das effektive \(T_e\) hängt unter anderem von Temperaturstruktur, rheologischer Kopplung, Lastwellenlänge und Belastungszeit ab. Daher ist

\[
T_{\rm lith,Sasgen}=T_{e,\rm plate}
\]

eine **Modellannahme**, keine Parametertransformation.

Für eine Größenordnungs-Sensitivitätsstudie halte ich sie dennoch für akzeptabel, wenn dies – wie bereits in LIMITATIONS – klar ausgesprochen wird. fileciteturn8file0L2-L2 Ich würde die Resultate aber nicht als „Lag mit der Sasgen-Rheologie“ bezeichnen, sondern als **„thin-plate/half-space sensitivity informed by Sasgen et al.“**

### Noch gröber ist Asthenosphärenviskosität gleich Halbraumviskosität

Im einfachen Modell gilt

\[
\tau
=
\frac{4\pi\eta}
{\rho_m g\lambda}
\,C.
\]

fileciteturn15file0L2-L2

Damit wird die veröffentlichte Asthenosphärenviskosität als Viskosität eines homogenen Halbraums verwendet. Im Sasgen-Modell ist sie dagegen eine regionale Viskosität innerhalb einer endlichen asthenosphärischen Schicht; darunter wirken andere Mantelviskositäten und die gesamte Antwort wird in sphärischer, selbstgravitierender Geometrie berechnet. citeturn16view2 Deshalb kann die resultierende einzelne \(\tau\) nicht als Sasgens Relaxationszeit gelesen werden.

Auch hier: als Szenario-Parameterisierung vertretbar, als quantitative Übertragung nicht.

### Warum im Modell die „elastische Fraktion“ die Nachweiszeit dominiert

Der entscheidende Punkt steht im Code von `tipping.py`. Die Stressratenantwort wird explizit als

\[
\dot S_{\rm GIA}(t)
=
\kappa\left[
(1-C)\dot L(t)
+
C\int
\dot L(s)
\frac{e^{-(t-s)/\tau}}{\tau}\,ds
\right]
\]

konstruiert. fileciteturn17file0L2-L2

Damit besitzt das Modell per Konstruktion zwei Kanäle:

\[
1-C
\quad\text{sofort},
\]

und

\[
C
\quad\text{verzögert mit }\tau.
\]

Das erklärt unmittelbar die Alaska-Ergebnisse. In v0.1 liegt \(C\approx0.11\); rund \(89\%\) der modellierten Antwort werden also dem sofortigen Zweig zugewiesen. Wenn nur \(\eta\) geändert wird, fällt \(\tau\) von ungefähr 64 auf 14 Jahre, aber die zeitverzögerte Komponente macht weiterhin nur rund \(11\%\) der gesamten Modellantwort aus. Entsprechend bleibt das früheste Nachweisjahr praktisch bei 2045.8. Beim Sasgen-informierten \(T_e=30\) km steigt dagegen \(C\) auf etwa \(0.50\), wodurch die Hälfte der Antwort in den verzögerten Kanal verschoben wird; das Nachweisjahr verschiebt sich auf ungefähr 2047.3. fileciteturn7file0L2-L2

**Innerhalb dieses Modells ist das Resultat daher vollkommen logisch und nicht numerisch verdächtig.**

Es ist sogar physikalisch qualitativ plausibel, dass eine große sofortige elastische Komponente die frühe Beobachtbarkeit stärker bestimmt als die genaue Relaxationszeit eines kleinen viskosen Restanteils.

Problematisch wird erst die weitergehende Interpretation. Der Faktor

\[
C=\frac{1}{1+Dk^4/(\rho g)}
\]

ist ursprünglich ein **flexuraler Kompensationsfaktor** für die Oberflächen-/Mantelantwort einer bestimmten Wellenlänge. Er ist nicht automatisch identisch mit dem Anteil des **Coulomb-Stresses auf seismogenen Störungen**, der viskos statt elastisch übertragen wird. Dass im Code exakt \(1-C\) in einen sofortigen seismischen Stresskanal und \(C\) in einen verzögerten Kanal eingeht, ist eine zusätzliche Modellannahme. fileciteturn17file0L2-L2

Hinzu kommt, dass \(T_e\) im einfachen Modell **nicht nur die Amplitudenaufteilung ändert**, sondern über \(C\) zugleich die Relaxationszeit verändert:

\[
\tau=\tau_{\rm halfspace}\,C.
\]

fileciteturn15file0L2-L2 Deshalb kann man aus dem Sensitivitätslauf streng genommen nicht sagen, die Nachweiszeit „hänge vom elastischen Anteil und nicht von der Viskosität“ als unabhängige physikalische Feststellung. \(T_e\) beeinflusst in dieser Parametrisierung gleichzeitig Amplitudenpartition und Relaxation.

Island zeigt auch die Gegenrichtung: Mit der niedrigeren Viskosität verkürzt sich die modellierte Einzelzeitkonstante von etwa 300 auf etwa zehn Jahre und das früheste Nachweisjahr verschiebt sich von ungefähr 2070 auf 2062. fileciteturn7file0L2-L2 Viskosität kann also sehr wohl entscheidend werden, sobald der verzögerte Anteil und die Relation zwischen \(\tau\) und Beobachtungsfenster anders liegen.

Mein Urteil lautet daher:

> **Das Ergebnis ist physikalisch nachvollziehbar innerhalb des reduzierten Modells, aber seine Stärke ist wesentlich modellarchitekturbedingt.** Es sollte nicht als empirische Erkenntnis gelesen werden, dass die reale seismische Reaktion Alaskas „von \(T_e\), nicht von \(\eta\)“ kontrolliert wird.

Die bereits verwendete Bezeichnung „Szenarien, keine Vorhersagen“ ist hier genau richtig. fileciteturn8file0L2-L2

## Der prospektive Test: gute Grundidee mit einigen schließbaren statistischen Öffnungen

C2 ist konzeptionell wahrscheinlich der stärkste Bestandteil von v0.2. Er beginnt erst am **1. Januar 2027**, verwendet vorher eingefrorene Triggerparameter und Baselines und definiert den primären Kontrast

\[
D =
[\log\mu_{\rm neu}-\log\mu_{\rm ref}]_G
-
[\log\mu_{\rm neu}-\log\mu_{\rm ref}]_C.
\]

Der erste Look verwendet Daten bis Ende 2029 mit \(\alpha=0.01\), der zweite Daten bis Ende 2036 mit \(\alpha=0.04\). Die Aufteilung \(0.01+0.04=0.05\) garantiert bereits per Bonferroni-/Union-Bound eine Gesamtfehlerwahrscheinlichkeit von höchstens \(0.05\), ohne Unabhängigkeit der beiden kumulativen Looks vorauszusetzen. fileciteturn1file0L2-L2

Das Einfrieren von \(K,\alpha,c,p\) ist für einen prospektiven Test sinnvoll: Sonst könnte ein zukünftiger Ratenanstieg post hoc entweder durch \(\mu\) oder veränderte Triggerparameter erklärt werden. Die Implementierung `mu_window_mle` konditioniert korrekt auf die Triggerhistorie und schätzt nur ein konstantes \(\mu\) im neuen Fenster; Ereignisse des Vorjahres können wegen \(t_{\max}=1\) als Trigger eingehen. fileciteturn13file0L2-L2

Trotzdem sehe ich mehrere Punkte, die vor dem Fenster wissenschaftlich geklärt sein sollten.

### Es gibt eine Inkonsistenz beim Faktor für die Standardfehler

`v02_benchmarks.md` sagt nach der Nullkalibrierung ausdrücklich, dass der Faktor \(1.25\) für die H2-/C2-Standardfehler vorab festgelegt werde. fileciteturn3file0L2-L2

Die Präregistrierung gibt für C2 dagegen

\[
SE^2
=
\sum_{\rm Regionen}
\left(
se_{\rm neu}^2
+
\frac{\sigma_y^2}{T}
+
\frac{\sigma_y^2}{n_{\rm ref}}
\right)
\]

an. fileciteturn1file0L2-L2

Und die aktuelle Implementierung berechnet exakt diese Summe, ohne Multiplikation mit \(1.25\):

```text
var =
    log_mu_se²
  + sigma_year² / T
  + sigma_year² / n_ref_years
```

gefolgt von der quadratischen Addition beider Regionen. fileciteturn11file0L2-L2

Damit ist derzeit unklar, ob

\[
SE_{\rm C2}
\]

oder

\[
1.25\,SE_{\rm C2}
\]

die tatsächlich eingefrorene Entscheidungsregel ist.

Das ist kein bloßes Dokumentationsdetail, weil es die Ablehnungsgrenze direkt verändert. Außerdem wurde der Faktor \(1.25\) aus Trend- und Fensterverhältnisstatistiken der H2-Simulationen gewonnen, nicht speziell aus der endgültigen C2-Statistik. fileciteturn3file0L2-L2 Die statistisch sauberste Lösung wäre daher nicht, mechanisch \(1.25\) irgendwo hinzuzufügen, sondern die **exakte C2-Prozedur als Ganzes** unter einem stationären/prospektiven Nullmodell zu simulieren und die endgültige Kalibrierung noch vor 2027 eindeutig zu hashen.

### Baseline und Zukunft schätzen nicht exakt dieselbe funktionale Größe

Das ist die subtilste Öffnung.

Die Referenz ist

\[
\log\mu_{\rm ref}
=
\frac{1}{10}
\sum_{y=2016}^{2025}
\log\mu_y,
\]

also der Mittelwert jährlicher **Log-Raten**. fileciteturn1file0L2-L2

Im Zukunftsfenster wird dagegen ein **einziges konstantes \(\mu_{\rm neu}\)** über drei bzw. zehn Jahre per Likelihood geschätzt und anschließend logarithmiert. fileciteturn13file0L2-L2

Bei realer Jahr-zu-Jahr-Heterogenität sind diese Größen nicht identisch:

\[
E[\log\mu_y]
\neq
\log E[\mu_y].
\]

Ist \(\log\mu_y\) näherungsweise normal mit Varianz \(\sigma^2\), gilt

\[
\log E[\mu_y]
=
E[\log\mu_y]+\frac{\sigma^2}{2}.
\]

Das erzeugt selbst bei unveränderter zugrunde liegender Verteilung einen positiven Offset, wenn der Zukunftsschätzer eher die gepoolte arithmetische Rate und die Baseline eher den geometrischen Mittelwert repräsentiert.

Für die eingefrorenen Baselines ist

\[
\sigma_{\rm SE\,Alaska}=0.3584,\qquad
\sigma_{\rm Interior}=0.1550.
\]

fileciteturn18file0L2-L2

Unter der vereinfachenden Lognormal-Näherung wäre der differentielle Offset

\[
\frac{1}{2}
(0.3584^2-0.1550^2)
\approx 0.052,
\]

also etwa **5% zugunsten eines positiven SE-Alaska-Kontrasts**, obwohl sich die Verteilung nicht geändert hätte.

Das ist angesichts des erwarteten ersten-Look-\(SE(D)\) von ungefähr \(0.3\) kein großer Effekt – etwa \(0.17\) Standardabweichungen –, aber er ist **gerichtet und vollständig vermeidbar**. Die Results selbst schätzen die erste C2-Schwelle grob auf einen Faktor zwei, für 80% Power etwa 2.5. fileciteturn6file0L2-L2

Methodisch sauberer wäre, Baseline und Zukunft mit demselben Funktional zu vergleichen: entweder einen konstanten Zehnjahres-\(\mu\)-MLE für 2016–2025 als Referenz verwenden oder auch künftig jährliche \(\log\mu_y\) erzeugen und deren Mittel mit dem historischen Mittel vergleichen. Entscheidend ist **Symmetrie des Estimands**.

### \(\sigma_y^2/T\) setzt praktisch unabhängige Jahre voraus

Die Formel

\[
\operatorname{Var}(\bar X_T)
=
\frac{\sigma_y^2}{T}
\]

ist für unabhängige Jahresabweichungen plausibel. Bei positiver serieller Korrelation gilt dagegen allgemein

\[
\operatorname{Var}(\bar X_T)
\simeq
\frac{\sigma^2}{T}
\left[
1+2\sum_k
\left(1-\frac{k}{T}\right)\rho_k
\right],
\]

sodass das einfache \(\sigma^2/T\) zu klein sein kann. Netzphasen und mehrjährige geophysikalische Episoden sind gerade Beispiele für Prozesse, die nicht wie unabhängiges Jahresrauschen aussehen. Die Alaska-Ergebnisse selbst demonstrieren mehrjährige Katalogphasen. fileciteturn6file0L2-L2

Umgekehrt enthält die empirische \(\sigma_y\) nicht nur wahre Prozessschwankung, sondern auch Schätzrauschen der jährlichen \(\mu_y\). Wird dann zusätzlich `log_mu_se²` addiert, kann ein Teil des Mess-/Schätzrauschens doppelt gezählt werden. fileciteturn11file0L2-L2 Das ist eher konservativ; positive Autokorrelation wirkt in die andere Richtung. Dadurch ist die aktuelle Formel weniger „falsch“ als vielmehr **ad hoc zusammengesetzt**.

Eine vollständige Nullsimulation der exakt eingefrorenen C2-Prozedur würde beide Fragen deutlich eleganter lösen.

### Die beiden Regionen sind nicht zwingend statistisch unabhängig

Der Code setzt

\[
SE(D)
=
\sqrt{SE_G^2+SE_C^2}.
\]

fileciteturn11file0L2-L2

Das entspricht \(\operatorname{Cov}(G,C)=0\). Bei gemeinsamen Netzwerk- und Katalogeffekten dürfte eine positive Korrelation plausibel sein. Für einen echten gemeinsamen zufälligen Effekt wäre das Ignorieren positiver Kovarianz sogar konservativ, denn

\[
\operatorname{Var}(G-C)
=
V_G+V_C-2\,\operatorname{Cov}(G,C).
\]

Das eigentliche Risiko sind jedoch **differentielle Netzänderungen**, die keine bloße Kovarianz erzeugen, sondern einen Bias im Mittelwert. Genau dieser Fall hat H2.1 wahrscheinlich getroffen. fileciteturn8file0L2-L2

C2 wird daher nur dann wirklich stark sein, wenn zusätzlich zur statistischen Formel operational feststeht, was bei einer zukünftigen Änderung von Katalogvollständigkeit, Magnitudenskala, Stationsnetz oder Datenpipeline geschieht. Ein eingefrorenes \(M_c\) schützt nur dann, wenn der Katalog während des gesamten Testfensters oberhalb dieses Wertes tatsächlich vollständig und vergleichbar bleibt.

### Das Fixieren der Triggerparameter ist legitim, aber die Unsicherheit wird konditioniert

Da \(K,\alpha,c,p\) als feste, vor 2027 bestimmte Nuisance-Parameter behandelt werden, enthält der C2-Fisher-Fehler ihre Schätzunsicherheit nicht. fileciteturn13file0L2-L2 Das kann man methodisch vertreten: Dann ist C2 ausdrücklich ein **bedingter prospektiver Test unter dem eingefrorenen ETAS-Modell**.

Wegen des \(p=1.0001\)-Randproblems sollte man ihn aber nicht als modellunabhängigen Test bezeichnen. Für SE Alaska und Interior Alaska sind genau die eingefrorenen \(p\)-Werte beide \(1.0001\). fileciteturn18file0L2-L2 Ein zukünftiger ungewöhnlich langer Sequenzschwanz kann daher weiterhin als \(\mu\)-Änderung erscheinen.

Mein Gesamturteil zu C2 ist dennoch positiv: **Die prospektive Differenz-von-Differenzen-Idee ist gut und wesentlich überzeugender als H2.1.** Die stärkste Fassung wäre ein exakt symmetrischer Baseline/Future-Estimand, eine explizite Regel für Kataloghomogenität und eine Monte-Carlo-Kalibrierung der vollständigen C2-Statistik. Dann wäre der Test sauber genug, um eine positive Beobachtung deutlich ernster zu nehmen als die retrospektive H2.1-Signifikanz.

## Schlussbewertung

Die v0.2-Arbeit macht wissenschaftlich etwas Richtiges: Sie versucht nicht, rohe Seismizitätsraten unmittelbar als Klimaantwort zu lesen, sondern trennt Clusterung, katalogische Robustheit, periodische Belastung und viskoelastische Verzögerungen in expliziten Modellen. Die Präregistrierung trennt retrospektive H2/H3-Analysen zudem korrekt vom wirklich prospektiven C2-Fenster. fileciteturn1file0L2-L2

Die stärksten Aussagen, die die gegenwärtigen Resultate tragen, sind meines Erachtens:

**Zum ETAS-Hintergrund:** Der zweistufige Ansatz ist eine sinnvolle regularisierte Zerlegung und in den eigenen synthetischen Tests dem gemeinsamen Fit überlegen. Wegen \(p\simeq1\), \(t_{\max}=1\) Jahr und des fehlenden Raumkerns ist \(\mu\) aber als **modellabhängiger Residualhintergrund**, nicht als isolierter glazialer Antrieb zu lesen. fileciteturn3file0L2-L2

**Zu H2.1:** Das Ergebnis \(+0.41\pm0.14\) pro Jahrzehnt ist formal echt im Sinne der präregistrierten Statistik, aber seine physikalische Interpretation ist nicht robust. Dass es nach 2003 verschwindet, mit einer Epoche schlechter Vollständigkeit zusammenfällt und bei längerem ETAS-Fenster stark schrumpft, macht die Netz-/Katalogerklärung derzeit klar plausibler als ein glaziales Signal. fileciteturn6file0L2-L2

**Zur „trügerischen Ruhe“:** Keine Region erfüllt die vorab definierte Regel. Das ist in SE Alaska und einigen besser beobachteten Regionen mäßig informativ gegen große Effekte; in Island und Grönland lässt die Power moderate bis selbst relativ große Effekte zu. Der Befund sollte deshalb als **„criterion not met“**, nicht als generelle Widerlegung des Mechanismus formuliert werden. fileciteturn6file0L2-L2

**Zu den Gezeiten:** Der Ausdruck \((2h-6l)W_2/(ga)\) ist als Grad-zwei-Körpergezeiten-Flächendehnung physikalisch korrekt; die Abweichung der verwendeten Love-/Shida-Zahlen von IERS-Nominalwerten ist klein. citeturn14view0 Was fehlt, ist jedoch gerade in den Küsten-/Inselregionen eine potentiell entscheidende Ozeanauflast und die auf Störungsflächen aufgelöste Spannung. Das H3-Nullresultat gilt deshalb nur für den verwendeten Body-tide-Proxy. citeturn23search1

**Zum Lagmodell:** Die Sasgen-Werte sind als Sensitivitätsanker sinnvoll, aber die Überführung in einen dünnplattigen viskosen Halbraum ist keine Reproduktion der Sasgen-Rheologie. citeturn16view2 Dass frühe Nachweiszeiten im Modell stärker auf \(C\) beziehungsweise \(1-C\) als auf \(\eta\) reagieren, folgt nachvollziehbar aus der expliziten Aufteilung in sofortigen und verzögerten Kanal; es sollte deshalb als **Eigenschaft des Szenariomodells**, nicht als neue geophysikalische Feststellung über Alaska formuliert werden. fileciteturn17file0L2-L2

**Zu C2:** Das Grunddesign ist überzeugend. Vor dem 1. Januar 2027 sollte aber eindeutig feststehen, ob der Faktor \(1.25\) gilt, und Baseline und Zukunft sollten idealerweise dieselbe statistische Zielgröße verwenden. Die derzeitige Mischung aus mittlerem jährlichem \(\log\mu\) und gepooltem Zukunfts-\(\log\mu\) erzeugt bei unterschiedlicher Jahresvarianz einen kleinen gerichteten Offset; die \(\sigma_y^2/T\)-Formel setzt außerdem eine stärkere zeitliche Unabhängigkeit voraus, als H2.1 empirisch nahelegt. fileciteturn1file0L2-L2 fileciteturn11file0L2-L2

Unterm Strich sehe ich **keinen fundamentalen physikalischen Fehler, der v0.2 als Ganzes entwertet**. Die problematischen Stellen liegen vielmehr dort, wo eine bewusst vereinfachte statistische oder rheologische Zerlegung beinahe physikalisch wörtlich genommen wird. In nüchterner Fassung ist die Evidenzlage daher: **kein belastbarer Nachweis eines glazial getriebenen säkularen ETAS-Hintergrundanstiegs; kein nachgewiesenes masked-rise-Muster; kein nachweisbarer Zusammenhang mit der modellierten Körpergezeitenphase; und Lag-Zeiten, die als Größenordnungs-Sensitivitäten, nicht als Prognosen, zu behandeln sind.** Der wirklich entscheidende Erkenntnisgewinn kann ab 2027 aus C2 kommen – vorausgesetzt, seine jetzt noch sichtbaren statistischen Mehrdeutigkeiten werden vor Öffnung des Datenfensters vollständig eingefroren. fileciteturn8file0L2-L2
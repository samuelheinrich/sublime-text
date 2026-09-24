# FortiOS für Sublime Text

Eine erste funktionsfähige Erweiterung für **Sublime Text 4**:
Syntaxfarben, semantische Blockfaltung und Navigation für FortiGate-/FortiOS-Konfigurationen.
Entwickelt und direkt in Sublime Text Build 4213 mit der lokalen Beispielkonfiguration geprüft.

## Verwendung

Nach der Installation eine Beispielkonfiguration öffnen oder **View → Syntax → FortiOS** wählen.
Bei einer Installation als Entwicklungs-Symlink lädt Sublime Änderungen an den Quelldateien automatisch.

Mit **⌘⇧P** auf macOS bzw. **Ctrl+Shift+P** auf Windows/Linux die Command Palette öffnen
und `FortiOS` eingeben. Dieselben Aktionen stehen im Rechtsklickmenü.

| Befehl | Wirkung |
| --- | --- |
| **Toggle Current Block** | Innersten Block am Cursor auf-/zuklappen; Kopfzeile und `next`/`end` bleiben sichtbar. |
| **Fold Sections (Overview)** | Fachabschnitte einklappen; `config global`, `config vdom` und VDOM-Namen bleiben sichtbar. |
| **Fold Long Sections** | `config`-Abschnitte ab 200 Zeilen einklappen; Global-/VDOM-Rahmen bleiben offen. |
| **Fold Entries in Current Section** | Direkte `edit`-Einträge des aktuellen `config`-Abschnitts einklappen, etwa alle Adressobjekte oder Policies. |
| **Fold Certificates and Long Text** | Lange Zertifikate, Schlüssel, verschlüsselte Werte und mehrzeilige Texte einklappen. |
| **Unfold Everything** | Alle Faltungen im Dokument aufheben. |
| **Go to Section** | Abschnitte durchsuchen, einschließlich VDOM-/Elternpfad, Zeilennummer und Länge. |

Zusätzlich **Ctrl+Alt+[** für den aktuellen Block und **Ctrl+Alt+]** für alles aufklappen.
Auf Tastaturlayouts ohne direkt erreichbare eckige Klammern empfiehlt sich die Command Palette.
Sublimes Symbolnavigation (**⌘R / Ctrl+R**) zeigt Abschnitte und Objekte.

Die normalen Faltpfeile links funktionieren weiterhin über Sublimes Einrückungserkennung.
Für nicht eingerückte Global-/VDOM-Blöcke und andere Fälle, in denen der Pfeil fehlt oder
die falsche Grenze erkennt, die **FortiOS-Befehle** verwenden: Diese ermitteln die Grenzen aus
`config`, `edit`, `next` und `end`. Es werden keine Einrückungen oder Inhalte verändert.

## Visuelle Darstellung

Das mitgelieferte dunkle Farbschema wird standardmäßig nur für die FortiOS-Syntax eingestellt.

| Element | Darstellung |
| --- | --- |
| Abschnitt, z. B. `firewall policy` | Blau, fett |
| Objektname / Policy-ID nach `edit` | Gold, fett |
| Wichtige Parameter wie `srcintf`, `dstaddr`, `action`, `ip`, `gateway` | Hell, fett |
| IP-Adressen, Netze, Zahlen, Portbereiche | Türkis |
| `accept`, `enable` | Grün, fett |
| `deny`, `disable`, Änderungsbefehle wie `delete` | Rot, fett |
| `all`, `any` | Gold, fett |
| Zertifikate, Schlüssel, HTML-Nutzdaten, UUIDs und Verwaltungsmetadaten | Gedämpftes Grau |

### FortiOS FMG Style

Ein zweites, helles Schema bildet die schlichte Konfigurationsansicht des FortiManagers nach
(Farben aus einem FortiManager-Screenshot gemessen). Es kommt mit vier Textfarben aus:

| Element | Farbe |
| --- | --- |
| Befehle `config`, `edit`, `set`, `next`, `end`, `unset` … | Lila `#620075` |
| Abschnitts- und Parameternamen | Schwarz `#000000` |
| Werte: Strings, Zahlen, IPs, `enable`/`disable`, Objektnamen nach `edit` | Grün `#0F7743` |
| Kommentare und Backup-Header `#…` | Braun `#984203` |

Hintergrund Weiß, Zeilennummern Grau auf `#F5F5F5`, aktive Zeile hellblau `#E3EFFF`.
Das Schema ist als eigene Syntax eingebunden: **View → Syntax → FortiOS → FortiOS FMG Style**.
Grammatik, Faltung und Befehle sind identisch mit **FortiOS**; nur die Farben unterscheiden sich.
Dateien öffnen standardmäßig mit **FortiOS** (dunkel). Wer immer den FMG-Stil möchte, stellt über
**View → Syntax → Open all with current extension as… → FortiOS → FortiOS FMG Style** um.

Die Farben beschreiben Werte, keine Sicherheitsbewertung: `disable` kann beispielsweise
auch eine Schutzfunktion deaktivieren. IP-Muster dienen der Darstellung, nicht der Adressvalidierung.
Falten und Abdunkeln sind ausschließlich Anzeigeoperationen; der vollständige Text bleibt in der Datei.

Eine kleine Konfiguration mit fiktiven Werten liegt unter [examples/overview.fgt](FortiOS/examples/overview.fgt).
Für große Faltungen gibt es außerdem eine [bereinigte Testdatei mit 19.231 Zeilen](examples/fortigate-sanitized.fgt).
Alle ursprünglichen Werte und Objektnamen wurden durch künstliche Daten ersetzt;
die Datei ist nicht als Gerätekonfiguration verwendbar. [Details zur Bereinigung](examples/README.md).

## Automatik und Einstellungen

Dateien mit `.fgt` und `.fortios` werden automatisch zugeordnet. Ein FortiGate-Backup-Header
`#config-version=FG…-…` aktiviert die Syntax auch bei `.txt`, `.cfg` oder `.conf`.
Dadurch funktioniert die Erkennung zusammen mit dem Cisco-Paket, das `.txt` und `.cfg` beansprucht.
Dateien ohne eindeutigen Header und ohne spezifische Endung bitte manuell zuordnen.

Lange Nutzdaten werden beim ersten Aktivieren eines Dokuments automatisch gefaltet.
Nach manuellem Aufklappen bleiben sie während dieser Sitzung offen; beim Tabwechsel werden
sie nicht erneut zugeklappt. Lange Konfigurationsabschnitte werden auf Wunsch per Befehl gefaltet.

**Preferences: FortiOS Settings** in der Command Palette öffnet die Benutzereinstellungen:

```json
{
    "fortios_auto_fold_payloads": true,
    "fortios_payload_min_lines": 4,
    "fortios_payload_min_chars": 100,
    "fortios_long_block_lines": 200,
    "fortios_detect_backup_header": true
}
```

Eine der beiden Nutzdaten-Schwellen genügt. Mehrzeilige Skripte und Beschreibungen können
damit ebenfalls gefaltet werden. Kurze normale Strings und lange Objektlisten werden nicht automatisch versteckt.
Für ein anderes Farbschema hier zusätzlich `color_scheme` auf dessen Sublime-Ressourcenpfad setzen.

## Installation auf einem weiteren Rechner

1. `python3 FortiGate/tools/build_package.py` vom Projektordner aus ausführen.
2. In Sublime **Preferences → Browse Packages…** öffnen.
3. Eine Ebene höher in `Installed Packages` wechseln und
   `FortiGate/dist/FortiOS.sublime-package` hineinkopieren.
4. Die Konfiguration öffnen und bei Bedarf **View → Syntax → FortiOS** wählen.

Alternativ den Quellordner `FortiGate/FortiOS` als `FortiOS` nach `Packages` kopieren.
Für lokale Entwicklung einen Symlink auf diesen Ordner verwenden. Nur eine Installationsform
gleichzeitig einsetzen. Zum Entfernen den Symlink, Paketordner oder das installierte Archiv löschen.
Das Archiv enthält ausschließlich die Erweiterung, Syntaxprüfungen und die fiktive Demo.

## Analyse und Aufbau

Die ausführliche Begründung und Messwerte stehen in [ANALYSE.md](ANALYSE.md).

| Datei | Aufgabe |
| --- | --- |
| `FortiOS/FortiOS.sublime-syntax` | Verschachtelte Syntaxkontexte, Werte und mehrzeilige Strings |
| `FortiOS/FortiOS Dark.sublime-color-scheme` | Visuelle Gewichtung |
| `FortiOS/FortiOS FMG Style.sublime-syntax` | Erbt die FortiOS-Grammatik; eigene Syntax für das FMG-Schema |
| `FortiOS/FortiOS FMG Style.sublime-color-scheme` | Helles Vier-Farben-Schema im FortiManager-Stil |
| `FortiOS/fortios_parser.py` | Block-/Textgrenzen ohne Abhängigkeit von Sublime oder Einrückung |
| `FortiOS/fortios.py` | Faltung, Abschnittsnavigation, Headererkennung und Cache |
| `FortiOS/Symbols.tmPreferences` | Abschnitts- und Objektsymbole für die Navigation |

Es gibt keine externe Laufzeitabhängigkeit. Der Parser liest den Text linear und wird pro
Dokumentversion zwischengespeichert. Er läuft bei Bedarf für Falt- und Navigationsbefehle,
nicht bei jedem Tastendruck. Mehrzeilige Strings respektieren einfache/doppelte Anführungszeichen
und Backslash-Escapes. Unvollständige Blöcke werden nicht bis ans Dateiende zugefaltet.

Die Erweiterung ist kein FortiOS-Konfigurationsvalidator. Unbekannte FortiOS-Parameter bleiben
lesbar und erhalten die allgemeine Parameterfarbe. Gerätespezifische oder künftige Syntaxvarianten
können anhand weiterer Beispiele ergänzt werden.

## Tests

```sh
python3 -m unittest discover -s FortiGate/tests -v
python3 FortiGate/tools/build_package.py
```

Für Sublimes native Syntaxprüfungen `FortiOS/tests/syntax_test_fortios.fgt` im installierten
Paket öffnen und **Tools → Build** ausführen. Die große öffentliche Testdatei wird immer geprüft.
Zusätzliche Tests der privaten Beispieldatei werden übersprungen, wenn sie lokal nicht vorhanden ist.

Bei der Erstprüfung: 13 Python-Tests und 28 native Syntaxprüfungen erfolgreich. Hinzu kommen
Tests für die Bereinigung und die öffentliche Testdatei. Zusätzlich wurden
Faltbefehle, automatische Erkennung trotz Cisco-Zuordnung, Farben und Syntaxleistung an der gesamten
Beispieldatei direkt in Sublime geprüft. Details in [ANALYSE.md](ANALYSE.md).

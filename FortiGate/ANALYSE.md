# Analyse und Entwurf

## Lokale Beispielkonfiguration

FortiOS-Backup aus Version 7.2.8; 580.386 Bytes und 19.231 Zeilen.
Es werden hier ausschließlich Strukturmerkmale dokumentiert.

| Merkmal | Ergebnis |
| --- | ---: |
| `config`-Blöcke | 937 |
| `edit`-Einträge | 3.956 |
| Alle erkannten Blöcke | 4.893 |
| Maximale strukturelle Tiefe | 7 |
| Mehrzeilige Werte | 49 |
| PEM-Werte | 43 |
| Fehlerhafte/offene Strukturen im Beispiel | 0 |

Die 49 mehrzeiligen Werte verteilen sich auf 5 CA-Zertifikate, 15 Zertifikate,
23 private Schlüssel, 4 HTML-Puffer, ein Skript und eine Beschreibung.
Sie belegen insgesamt 1.533 Zeilen einschließlich der Anfangs-/Endzeilen.

Besonders große Abschnitte:

| Abschnitt | Zeilen |
| --- | ---: |
| `config global` als äußerer Rahmen | 10.275 |
| `config firewall internet-service-name` | 5.090 |
| `config system admin` | 1.404 |
| Ein verschachteltes `config gui-dashboard` | 1.072 |
| `config system interface` | 932 |
| `config certificate local` | 772 |

Die Einrückung bildet die Struktur nicht vollständig ab: Vor allem globale Abschnitte
und VDOM-Rahmen enthalten weitere Blöcke auf derselben Einrückungsebene. Deshalb reicht
Sublimes gewöhnliche Einrückungsfaltung für diese Datei nicht aus.

Drei VDOM-Einträge werden durch `end` ohne vorangehendes `next` abgeschlossen. Das ist
gültige FortiOS-Syntax: `end` kann einen bearbeiteten Eintrag und dessen Tabelle gemeinsam
verlassen. Ein starrer Parser mit ausschließlich `edit`/`next`-Paaren würde hier falsche
Restblöcke erzeugen. Siehe [Fortinet: Command syntax](https://docs.fortinet.com/document/fortigate/7.6.0/administration-guide/508024/command-syntax).

## Cisco-Paket

Das untersuchte [tunnelsup/sublime-cisco-syntax](https://github.com/tunnelsup/sublime-cisco-syntax)
enthält eine ältere TextMate-Grammatik (`.tmLanguage` und deren JSON-Quelle), Kommentarpräferenzen
und eine README. Die Grammatik nutzt eine flache Liste von Regex-Regeln für unter anderem
Zugriffslisten, `permit`/`deny`, Kommentare, IPv4 und IPv6. Sie deklariert `.cfg` und `.txt`.
Die ebenfalls lokal installierte Fassung wurde als Integrationspartner verwendet.

Es gibt darin keine verschachtelten Sprachkontexte oder eigene Blockfaltungslogik. Manche
Wortmuster sind nicht an Befehlspositionen gebunden. Eine Übertragung dieser Architektur
würde FortiOS-Schlüsselwörter auch innerhalb von Textwerten erkennen und könnte VDOM-Strukturen
nicht zuverlässig abbilden. Der Quelltext wurde untersucht; die neue Implementierung ist eigenständig.
Quelle: [Cisco-Grammatik](https://github.com/tunnelsup/sublime-cisco-syntax/blob/master/Cisco%20Definitions.json-tmLanguage).

## Lösung

Die Darstellung hat drei Ebenen:

1. **Struktur:** Blaue Abschnittsnamen, goldene Objektnamen und sichtbare Blockabschlüsse.
2. **Konfiguration:** Helle wichtige Parameter, unterscheidbare Adressen sowie hervorgehobene Aktionen und Statuswerte.
3. **Nutzdaten und Metadaten:** Gedämpfte Zertifikate, Schlüssel, HTML und UUIDs; lange Werte automatisch faltbar.

Eine `.sublime-syntax` mit getrennten Kontexten für `config`, `edit`, Parameterwerte und Strings
verhindert, dass `end` in einem Skript oder HTML-Text einen äußeren Block beendet. Standard-Scopes
halten die Grammatik auch mit anderen Farbschemata nutzbar; die genaue Gewichtung liefert
das eigene Farbschema. Grundlage: [Sublime Syntax Definitions](https://www.sublimetext.com/docs/syntax.html)
und [Color Schemes](https://www.sublimetext.com/docs/color_schemes.html).

Ein eigener Parser liefert semantische Bereiche für Sublimes `fold`-/`unfold`-API. Er berücksichtigt
Verschachtelung, das gemeinsame Schließen von Eintrag/Tabelle, Quotes und Escape-Zeichen.
Das ermöglicht präzise Faltung auch ohne Einrückung. Die normalen Faltpfeile bleiben Sublimes
Einrückungsfunktion; semantische Aktionen sind über Palette, Kontextmenü und Tastenkürzel erreichbar.
Siehe [Sublime API Reference](https://www.sublimetext.com/docs/api_reference.html).

Die Übersicht erhält VDOM-/Global-Rahmen und reduziert stattdessen Fachabschnitte. Damit bleibt
erkennbar, zu welchem VDOM ein Bereich gehört. Die Abschnittssuche zeigt zusätzlich den Elternpfad.
Große Kataloge können insgesamt oder Eintrag für Eintrag gefaltet werden.

## Verifikation am 23. September 2026

Direkt in Sublime Text Build 4213 auf diesem Mac:

| Prüfung | Ergebnis |
| --- | --- |
| Parser-Tests, inklusive kompletter Beispieldatei | 13 bestanden |
| Native Syntaxprüfungen | 28 bestanden |
| Regex-Kompatibilität mit Sublimes schneller Engine | Keine inkompatiblen Muster |
| Ungültige Syntax-Scopes in der Beispieldatei | 0 |
| Erkannte Abschnitts-/Objektnamen in der Syntax | 937 / 3.956 |
| Automatisch gefaltete Nutzdaten | 85 Bereiche |
| Lange Fachabschnitte ab 200 Zeilen | 17 Faltungen |
| Übersicht | 255 nichtleere Fachabschnitte gefaltet |
| Internet-Service-Katalog, direkte Einträge | 1.696 Faltungen |
| Aktuellen Block zu-/aufklappen | 1 / 0 verbleibende Faltungen |
| FortiGate-Header bei vorher aktivierter Cisco-Syntax | FortiOS erkannt, 85 Nutzdaten gefaltet |
| Farbschema | Wichtige Parameter hell/fett, Nutzdaten gedämpft bestätigt |

399 äußere Fachabschnitte werden erkannt; 144 davon haben keinen faltbaren Inhalt.
Die 85 Nutzdatenfaltungen umfassen neben mehrzeiligen Texten auch lange einzeilige Schlüsselwerte.
Die Schwellenwerte sind bewusst konfigurierbar.

Eine lokale Einzelmessung benötigte rund **44 ms** für den Python-Parser und **99 ms** für
Sublimes Syntaxverarbeitung der gesamten Datei. Diese Werte sind Orientierung für das konkrete
Beispiel und keine Leistungszusage für beliebig große Backups.

Die Syntaxprüfungen testen unter anderem geschachtelte Blöcke, VDOM-Abschlüsse, IPv4/IPv6,
Aktionen, Metadaten und FortiOS-Befehle innerhalb von PEM-, HTML- und Skriptwerten. Die Parser-Tests
ergänzen CRLF, Unicode, einfache Quotes, Escapes, fehlende Einrückung und abgeschnittene Eingaben.

## Öffentliche Testdatei

Für die Veröffentlichung wurde eine separate synthetische Fassung erzeugt. Alle Werte,
Objektnamen, IDs, Kommentare und Nutzdaten wurden ersetzt; Blockgrenzen und Zeilenzahl
entsprechen weiterhin dem lokalen Ausgangsbeispiel. Die Originaldatei bleibt außerhalb der Git-Historie.

Die Tests prüfen zusätzlich die Ersetzung von Benutzer-/Serverdaten, Secrets und mehrzeiligen
Inhalten sowie den Abbruch bei unbekannten Befehlen oder ungeprüften Abschnittspfaden.
Eine separate Prüfung der öffentlichen Datei erlaubt ausschließlich definierte synthetische
Wertformate; alle **12.657 Werte und Objektnamen** bestehen diese Prüfung.
Mit diesen Ergänzungen bestehen **22 Python-Tests**. Ohne das lokale Original werden zwei
Vergleichstests übersprungen; die öffentliche Testdatei wird weiterhin vollständig geprüft.

[Testdatei und Bereinigungsdetails](examples/README.md)

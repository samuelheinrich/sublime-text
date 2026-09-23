# Große synthetische Testkonfiguration

`fortigate-sanitized.fgt` wurde aus einem lokalen FortiOS-Backup erzeugt. Sie erhält
dessen Struktur mit **19.231 Zeilen, 937 config-Blöcken, 3.956 edit-Einträgen und
49 mehrzeiligen Werten**, damit große und verschachtelte Faltungen reproduzierbar sind.

Übernommen wurden ausschließlich geprüfte CLI-Abschnittspfade, Parameternamen,
Strukturbefehle und Einrückungen. Ersetzt wurden **alle Werte**, darunter:

- Benutzer-, Gruppen-, VDOM-, Geräte- und Objektnamen sowie numerische Objekt-IDs;
- Passwörter, verschlüsselte Werte, private/öffentliche Schlüssel und Zertifikatsinhalte;
- RADIUS-/LDAP-/TACACS-Serverwerte und Secrets, sofern im Eingabebackup vorhanden;
- IP-/MAC-Adressen, Netze, Domains, URLs, UUIDs, Seriennummern und sonstige Kennungen;
- Kommentare, Backup-Metadaten, HTML, Skripte und mehrzeilige Beschreibungen.

Die Ersatzwerte sind laufende Demo-Bezeichner, Dokumentationsadressen und fest erzeugte
Platzhalter. Es wird keine Zuordnungstabelle zu Originalwerten veröffentlicht.
PEM-Markierungen bleiben als Syntaxbeispiel sichtbar, ihre Inhalte sind unbrauchbare Testtexte.
Auch Zahlen und Status-/Aktionswerte wurden neu erzeugt; die Datei bildet keine realen Regeln ab.
Referenzen zwischen Objekten sind nicht für einen Geräteimport rekonstruiert.

**Diese Datei ausschließlich zum Testen von Syntaxfarben, Navigation und Faltung verwenden.**

## Lokal neu erzeugen

```sh
python3 FortiGate/tools/sanitize_config.py \
  FortiGate/fortigate-sample-config.txt \
  FortiGate/examples/new-sanitized.fgt
```

Das Original wird nicht verändert. Der Zielpfad muss neu sein. Unbekannte Befehle,
ungeprüfte Abschnittspfade und unvollständige Strings führen zum Abbruch, bevor eine
Ausgabedatei geschrieben wird. Die freigegebenen Abschnittspfade stehen in
`tools/sanitizer_config_paths.json`; neue Pfade müssen vor einer Erweiterung geprüft werden.

Der Generator ist für vollständige FortiOS-Konfigurationen mit dieser CLI-Struktur ausgelegt,
nicht für beliebige Logdateien oder andere Dateiformate. Neue Ausgaben vor Veröffentlichung prüfen.

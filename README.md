# Sublime Text Extensions

Syntax-Highlighting und Erweiterungen für Sublime Text. Jedes Paket erhält einen
eigenen Projektordner mit Quellcode, Dokumentation, Beispielen und Tests.

| Paket | Beschreibung |
| --- | --- |
| [FortiGate / FortiOS](FortiGate/README.md) | Syntaxfarben, semantische Blockfaltung und Navigation für FortiOS-Konfigurationen |

## FortiOS installieren

Den Ordner [`FortiGate/FortiOS`](FortiGate/FortiOS) als `FortiOS` in Sublimes
Paketverzeichnis kopieren (**Preferences → Browse Packages…**).
Danach **View → Syntax → FortiOS** auswählen oder eine `.fgt`-/`.fortios`-Datei öffnen.

Alternativ ein installierbares Archiv bauen:

```sh
python3 FortiGate/tools/build_package.py
```

Die erzeugte Datei `FortiGate/dist/FortiOS.sublime-package` nach `Installed Packages`
kopieren. [Vollständige Anleitung und Faltbefehle](FortiGate/README.md).

## Beispiele und Tests

- [Kleine fiktive Demo](FortiGate/FortiOS/examples/overview.fgt)
- [Große bereinigte Testkonfiguration](FortiGate/examples/fortigate-sanitized.fgt):
  19.231 Zeilen und 4.893 Blöcke; sämtliche ursprünglichen Werte und Objektnamen ersetzt.
- [Bereinigung und Grenzen der Testdaten](FortiGate/examples/README.md)

```sh
python3 -m unittest discover -s FortiGate/tests -v
```

Originale Gerätebackups gehören nicht ins Repository. Die veröffentlichte große
Testdatei enthält künstliche Werte sowie absichtlich ungültige Zertifikats- und
Schlüsselplatzhalter. Sie dient ausschließlich zum Testen der Darstellung und Faltung.

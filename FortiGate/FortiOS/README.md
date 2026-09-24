# FortiOS for Sublime Text 4

Select **View → Syntax → FortiOS → FortiOS** (dark) or **FortiOS FMG Style**
(light, FortiManager look). Files ending in `.fgt` or `.fortios`, and
backups with a FortiGate `#config-version=FG…` header, are detected automatically.

Open the Command Palette and search for **FortiOS**:

- **Toggle Current Block** folds/unfolds the innermost config/edit block.
- **Fold Sections (Overview)** keeps global/VDOM wrappers visible.
- **Fold Long Sections** collapses sections with at least 200 lines.
- **Fold Entries in Current Section** collapses direct edit entries.
- **Fold Certificates and Long Text** hides long payload values.
- **Unfold Everything** expands the document.
- **Go to Section** searches section names and their parent paths.

These commands are also in the context menu. **Ctrl+Alt+[** toggles the current
block; **Ctrl+Alt+]** unfolds everything. Semantic commands work without
indentation. Sublime's normal gutter arrows remain indentation based.

Certificates, keys, HTML payloads and metadata use muted colors. Long payloads
are folded on first activation. Important fields and action/status values stand
out in the included dark color scheme; the FMG Style syntax uses a light
four-color scheme instead. Display operations never rewrite text.

Use **Preferences: FortiOS Settings** to change thresholds, automatic folding,
header detection or the color scheme. Open `tests/syntax_test_fortios.fgt` and run **Tools → Build** to
execute the native syntax tests.

Tested with Sublime Text Build 4213. No external runtime dependencies.

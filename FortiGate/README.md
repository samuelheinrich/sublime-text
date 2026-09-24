# FortiOS for Sublime Text

A working extension for **Sublime Text 4**: syntax highlighting, semantic block folding
and navigation for FortiGate / FortiOS configurations.
Developed and tested directly in Sublime Text Build 4213.

| FortiOS (dark) | FortiOS FMG Style (light) |
| --- | --- |
| <img src="docs/screenshot-dark.png" alt="Dark FortiOS color scheme" width="420"> | <img src="docs/screenshot-fmg.png" alt="Light FortiOS FMG Style color scheme" width="420"> |

## Usage

After installing, open a configuration or choose **View → Syntax → FortiOS**.
The submenu offers **FortiOS** (dark) and **FortiOS FMG Style** (light); both share the
same grammar, folding and commands. With a development symlink, Sublime reloads changes
to the source files automatically.

Press **⌘⇧P** on macOS or **Ctrl+Shift+P** on Windows/Linux to open the Command Palette
and type `FortiOS`. The same actions are available in the context menu.

| Command | Effect |
| --- | --- |
| **Toggle Current Block** | Fold/unfold the innermost block at the cursor; the header line and `next`/`end` stay visible. |
| **Fold Sections (Overview)** | Fold topic sections; `config global`, `config vdom` and VDOM names stay visible. |
| **Fold Long Sections** | Fold `config` sections with 200 or more lines; global/VDOM wrappers stay open. |
| **Fold Entries in Current Section** | Fold the direct `edit` entries of the current `config` section, e.g. all address objects or policies. |
| **Fold Certificates and Long Text** | Fold long certificates, keys, encrypted values and multi-line text. |
| **Unfold Everything** | Remove all folds in the document. |
| **Go to Section** | Search sections, including VDOM/parent path, line number and length. |

**Ctrl+Alt+[** toggles the current block and **Ctrl+Alt+]** unfolds everything.
On keyboard layouts without direct access to square brackets, use the Command Palette.
Sublime's symbol navigation (**⌘R / Ctrl+R**) lists sections and objects.

The regular fold arrows in the gutter keep working through Sublime's indentation detection.
For unindented global/VDOM blocks and other cases where the arrow is missing or picks the
wrong boundary, use the **FortiOS commands**: they derive boundaries from `config`, `edit`,
`next` and `end`. Indentation and content are never modified.

## Color schemes

### FortiOS (dark)

The default scheme for the **FortiOS** syntax. It is only applied to FortiOS files.

| Element | Appearance |
| --- | --- |
| Section, e.g. `firewall policy` | Blue, bold |
| Object name / policy ID after `edit` | Gold, bold |
| Important parameters such as `srcintf`, `dstaddr`, `action`, `ip`, `gateway` | Bright, bold |
| IP addresses, networks, numbers, port ranges | Cyan |
| `accept`, `enable` | Green, bold |
| `deny`, `disable`, mutation commands such as `delete` | Red, bold |
| `all`, `any` | Gold, bold |
| Certificates, keys, HTML payloads, UUIDs and management metadata | Muted gray |

### FortiOS FMG Style (light)

A second, light scheme that recreates the plain configuration view of FortiManager
(colors measured from a FortiManager screenshot). It uses only four text colors:

| Element | Color |
| --- | --- |
| Commands `config`, `edit`, `set`, `next`, `end`, `unset` … | Purple `#620075` |
| Section and parameter names | Black `#000000` |
| Values: strings, numbers, IPs, `enable`/`disable`, object names after `edit` | Green `#0F7743` |
| Comments and the `#…` backup header | Brown `#984203` |

White background, gray line numbers on `#F5F5F5`, light blue current line `#E3EFFF`.

The scheme is shipped as its own syntax: **View → Syntax → FortiOS → FortiOS FMG Style**.
Files open with **FortiOS** (dark) by default. To always use the FMG style, open a file and choose
**View → Syntax → Open all with current extension as… → FortiOS → FortiOS FMG Style**.

Colors describe values, not a security rating: `disable` may just as well turn off a
protection feature. IP patterns are for display only, not address validation.
Folding and muting are display operations only; the full text always stays in the file.

## Detection and settings

Files ending in `.fgt` and `.fortios` are assigned automatically. A FortiGate backup header
`#config-version=FG…-…` also activates the syntax for `.txt`, `.cfg` or `.conf`.
This keeps detection working alongside the Cisco package, which claims `.txt` and `.cfg`.
Assign files without a clear header or specific extension manually.

Long payloads are folded automatically the first time a document is activated.
After unfolding them manually they stay open for the session; switching tabs does not
fold them again. Long configuration sections are folded on demand via command.

**Preferences: FortiOS Settings** in the Command Palette opens the user settings:

```json
{
    "fortios_auto_fold_payloads": true,
    "fortios_payload_min_lines": 4,
    "fortios_payload_min_chars": 100,
    "fortios_long_block_lines": 200,
    "fortios_detect_backup_header": true
}
```

Either payload threshold is sufficient. Multi-line scripts and descriptions can be folded
this way too. Short regular strings and long object lists are never hidden automatically.
To use a different color scheme, also set `color_scheme` to its Sublime resource path.

## Installing on another machine

1. Run `python3 FortiGate/tools/build_package.py` from the project folder.
2. In Sublime, open **Preferences → Browse Packages…**.
3. Go one level up into `Installed Packages` and copy
   `FortiGate/dist/FortiOS.sublime-package` into it.
4. Open a configuration and, if needed, choose **View → Syntax → FortiOS**.

Alternatively, copy the source folder `FortiGate/FortiOS` as `FortiOS` into `Packages`.
For local development, use a symlink to that folder. Use only one installation method
at a time. To uninstall, delete the symlink, package folder or installed archive.
The archive contains only the extension and its syntax tests.

## Analysis and structure

The detailed reasoning and measurements are in [ANALYSIS.md](ANALYSIS.md).

| File | Purpose |
| --- | --- |
| `FortiOS/FortiOS.sublime-syntax` | Nested syntax contexts, values and multi-line strings |
| `FortiOS/FortiOS Dark.sublime-color-scheme` | Visual weighting for the dark scheme |
| `FortiOS/FortiOS FMG Style.sublime-syntax` | Inherits the FortiOS grammar; separate syntax for the FMG scheme |
| `FortiOS/FortiOS FMG Style.sublime-color-scheme` | Light four-color scheme in FortiManager style |
| `FortiOS/fortios_parser.py` | Block/text boundaries independent of Sublime or indentation |
| `FortiOS/fortios.py` | Folding, section navigation, header detection and cache |
| `FortiOS/Symbols.tmPreferences` | Section and object symbols for navigation |

There are no external runtime dependencies. The parser reads the text linearly and is
cached per document version. It runs on demand for folding and navigation commands,
not on every keystroke. Multi-line strings respect single/double quotes and backslash
escapes. Incomplete blocks are never folded to the end of the file.

The extension is not a FortiOS configuration validator. Unknown FortiOS parameters stay
readable and get the generic parameter color. Device-specific or future syntax variants
can be added based on further examples.

## Tests

```sh
python3 -m unittest discover -s FortiGate/tests -v
python3 FortiGate/tools/build_package.py
```

For Sublime's native syntax tests, open `FortiOS/tests/syntax_test_fortios.fgt` in the
installed package and run **Tools → Build**. An additional comparison test against a private
local backup is skipped when that file is not present.

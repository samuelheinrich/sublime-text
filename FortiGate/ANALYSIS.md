# Analysis and Design

## Local sample configuration

FortiOS backup from version 7.2.8; 580,386 bytes and 19,231 lines.
Only structural characteristics are documented here.

| Characteristic | Result |
| --- | ---: |
| `config` blocks | 937 |
| `edit` entries | 3,956 |
| All detected blocks | 4,893 |
| Maximum structural depth | 7 |
| Multi-line values | 49 |
| PEM values | 43 |
| Malformed/unclosed structures in the sample | 0 |

The 49 multi-line values consist of 5 CA certificates, 15 certificates,
23 private keys, 4 HTML buffers, one script and one description.
Together they span 1,533 lines including their opening and closing lines.

Particularly large sections:

| Section | Lines |
| --- | ---: |
| `config global` as the outer wrapper | 10,275 |
| `config firewall internet-service-name` | 5,090 |
| `config system admin` | 1,404 |
| A nested `config gui-dashboard` | 1,072 |
| `config system interface` | 932 |
| `config certificate local` | 772 |

Indentation does not fully reflect the structure: global sections and VDOM wrappers in
particular contain further blocks at the same indentation level. Sublime's regular
indentation-based folding is therefore not sufficient for this file.

Three VDOM entries are closed by `end` without a preceding `next`. This is valid FortiOS
syntax: `end` can leave an edited entry and its table together. A rigid parser that only
knows `edit`/`next` pairs would produce bogus leftover blocks here. See
[Fortinet: Command syntax](https://docs.fortinet.com/document/fortigate/7.6.0/administration-guide/508024/command-syntax).

## Cisco package

The examined [tunnelsup/sublime-cisco-syntax](https://github.com/tunnelsup/sublime-cisco-syntax)
contains an older TextMate grammar (`.tmLanguage` and its JSON source), comment preferences
and a README. The grammar uses a flat list of regex rules for access lists, `permit`/`deny`,
comments, IPv4 and IPv6, among others. It claims `.cfg` and `.txt`.
The locally installed copy was used as an integration partner.

It has no nested language contexts and no block folding logic of its own. Some word
patterns are not bound to command positions. Carrying this architecture over would match
FortiOS keywords inside text values and could not reliably represent VDOM structures.
The source was examined; the new implementation is independent.
Source: [Cisco grammar](https://github.com/tunnelsup/sublime-cisco-syntax/blob/master/Cisco%20Definitions.json-tmLanguage).

## Solution

The presentation has three layers:

1. **Structure:** blue section names, gold object names and visible block closers.
2. **Configuration:** bright important parameters, distinguishable addresses and highlighted actions and status values.
3. **Payloads and metadata:** muted certificates, keys, HTML and UUIDs; long values can be folded automatically.

A `.sublime-syntax` with separate contexts for `config`, `edit`, parameter values and strings
prevents an `end` inside a script or HTML text from closing an outer block. Standard scopes
keep the grammar usable with other color schemes; the bundled schemes provide the exact
weighting. References: [Sublime Syntax Definitions](https://www.sublimetext.com/docs/syntax.html)
and [Color Schemes](https://www.sublimetext.com/docs/color_schemes.html).

The **FortiOS FMG Style** syntax extends the base grammar (`extends`) without changes and only
exists so it can carry its own color scheme. Its scope `source.fortios.fmg` still matches the
`source.fortios` selector, so all commands, symbols and comment settings apply unchanged.

A dedicated parser supplies semantic regions to Sublime's `fold`/`unfold` API. It handles
nesting, closing an entry and its table together, quotes and escape characters.
This allows precise folding even without indentation. The regular fold arrows remain
Sublime's indentation feature; semantic actions are available via palette, context menu
and key bindings. See [Sublime API Reference](https://www.sublimetext.com/docs/api_reference.html).

The overview keeps VDOM/global wrappers and collapses topic sections instead. This keeps
it clear which VDOM a section belongs to. Section search also shows the parent path.
Large catalogs can be folded as a whole or entry by entry.

## Verification on 23 September 2026

Directly in Sublime Text Build 4213 on macOS:

| Check | Result |
| --- | --- |
| Parser tests, including the complete sample file | 13 passed |
| Native syntax tests | 28 passed |
| Regex compatibility with Sublime's fast engine | No incompatible patterns |
| Invalid syntax scopes in the sample file | 0 |
| Detected section/object names in the syntax | 937 / 3,956 |
| Automatically folded payloads | 85 regions |
| Long topic sections of 200+ lines | 17 folds |
| Overview | 255 non-empty topic sections folded |
| Internet service catalog, direct entries | 1,696 folds |
| Toggle current block | 1 / 0 remaining folds |
| FortiGate header with Cisco syntax active beforehand | FortiOS detected, 85 payloads folded |
| Color scheme | Important parameters bright/bold, payloads muted — confirmed |

399 outer topic sections are detected; 144 of them have no foldable content.
Besides multi-line texts, the 85 payload folds include long single-line key values.
The thresholds are deliberately configurable.

A single local measurement took about **44 ms** for the Python parser and **99 ms** for
Sublime's syntax processing of the whole file. These figures are indicative for this
particular sample, not a performance guarantee for arbitrarily large backups.

The syntax tests cover nested blocks, VDOM closers, IPv4/IPv6, actions, metadata and
FortiOS commands inside PEM, HTML and script values, among others. The parser tests add
CRLF, Unicode, single quotes, escapes, missing indentation and truncated input.

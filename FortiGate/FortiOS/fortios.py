"""Sublime Text commands for semantic FortiOS folding and navigation."""
import re

import sublime
import sublime_plugin

from .fortios_parser import parse, outermost, section_blocks, is_wrapper


SYNTAX = 'Packages/FortiOS/FortiOS.sublime-syntax'
_cache = {}


def enabled(view):
    return view.match_selector(0, 'source.fortios')


def setting(view, key, default):
    return view.settings().get(key, sublime.load_settings('FortiOS.sublime-settings').get(key, default))


def document(view):
    key = (view.buffer_id(), view.change_count())
    cached = _cache.get(view.id())
    if cached is None or cached[0] != key:
        cached = (key, parse(view.substr(sublime.Region(0, view.size()))))
        _cache[view.id()] = cached
    return cached[1]


def block_region(block):
    # Keep the complete header and closing next/end visible.
    return sublime.Region(block.header_end, max(block.header_end, block.close_start - 1))


def fold_blocks(view, blocks):
    regions = [block_region(b) for b in blocks]
    view.fold([r for r in regions if not r.empty()])


def payload_regions(view, doc):
    min_lines = setting(view, 'fortios_payload_min_lines', 4)
    min_chars = setting(view, 'fortios_payload_min_chars', 100)
    return [sublime.Region(p.start, p.end) for p in doc.payloads
            if p.end > p.start and (p.end_row - p.row + 1 >= min_lines
                                   or p.end - p.start >= min_chars)]


class FortiosCommand(sublime_plugin.TextCommand):
    def is_enabled(self, **kwargs):
        return enabled(self.view)

    def is_visible(self, **kwargs):
        return enabled(self.view)


class FortiosToggleBlockCommand(FortiosCommand):
    def run(self, edit):
        doc = document(self.view)
        targets = []
        folded = self.view.folded_regions()
        for selection in self.view.sel():
            point = selection.begin()
            candidates = [b for b in doc.blocks if b.start <= point <= b.end]
            if not candidates:
                continue
            block = max(candidates, key=lambda b: b.depth)
            region = block_region(block)
            if region in folded:
                self.view.unfold(region)
            elif not region.empty():
                targets.append(region)
        self.view.fold(targets)


class FortiosFoldCommand(FortiosCommand):
    def run(self, edit, mode='overview'):
        doc = document(self.view)
        if mode == 'payloads':
            self.view.fold(payload_regions(self.view, doc))
        elif mode == 'overview':
            fold_blocks(self.view, section_blocks(doc))
        elif mode == 'long':
            threshold = setting(self.view, 'fortios_long_block_lines', 200)
            fold_blocks(self.view, outermost(b for b in doc.blocks
                        if b.kind == 'config' and not is_wrapper(b)
                        and b.end_row - b.row + 1 >= threshold))
        elif mode == 'entries':
            points = [s.begin() for s in self.view.sel()]
            configs = [b for b in doc.blocks if b.kind == 'config'
                       and any(b.start <= p <= b.end for p in points)]
            if configs:
                parent = max(configs, key=lambda b: b.depth)
                fold_blocks(self.view, [b for b in doc.blocks if b.kind == 'edit'
                                        and b.parent == parent.start])
        if doc.issues:
            sublime.status_message('FortiOS: {0} incomplete/unmatched structures; only complete blocks folded'.format(len(doc.issues)))


class FortiosUnfoldAllCommand(FortiosCommand):
    def run(self, edit):
        self.view.unfold(sublime.Region(0, self.view.size()))


class FortiosSectionsCommand(FortiosCommand):
    def run(self, edit):
        doc = document(self.view)
        blocks = [b for b in doc.blocks if b.kind == 'config']
        by_start = dict((b.start, b) for b in doc.blocks)
        entries = []
        for block in blocks:
            trail, parent = [], block.parent
            while parent in by_start:
                ancestor = by_start[parent]
                trail.append(ancestor.label)
                parent = ancestor.parent
            entries.append(['config ' + block.label,
                            '{0} | line {1} | {2} lines'.format(
                                ' > '.join(reversed(trail)) or 'root', block.row + 1,
                                block.end_row - block.row + 1)])
        revision = self.view.change_count()

        def select(index):
            if index < 0 or not self.view.is_valid():
                return
            if self.view.change_count() != revision:
                sublime.status_message('FortiOS: configuration changed; reopen section list')
                return
            point = blocks[index].start
            self.view.unfold(sublime.Region(max(0, point - 1), point + 1))
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(point))
            self.view.show_at_center(point)

        self.view.window().show_quick_panel(entries, select)


def prepare(view):
    if not view.is_valid() or view.is_loading():
        return
    # Cisco claims .txt/.cfg. A FortiGate backup header is more specific.
    # The setting allows users to opt out of this automatic detection.
    if setting(view, 'fortios_detect_backup_header', True):
        header = view.substr(view.line(0))
        if re.match(r'^\ufeff?#config-version=FG[A-Z0-9]+-', header) and not enabled(view):
            view.assign_syntax(SYNTAX)
    if not enabled(view) or view.settings().get('_fortios_prepared'):
        return
    view.settings().set('_fortios_prepared', True)
    if setting(view, 'fortios_auto_fold_payloads', True):
        view.fold(payload_regions(view, document(view)))


class FortiosColorSchemeCommand(sublime_plugin.ApplicationCommand):
    """Store the chosen bundled scheme in the user's FortiOS syntax settings."""
    def run(self, name):
        settings = sublime.load_settings('FortiOS.sublime-settings')
        settings.set('color_scheme', 'Packages/FortiOS/%s.sublime-color-scheme' % name)
        sublime.save_settings('FortiOS.sublime-settings')


class FortiosListener(sublime_plugin.EventListener):
    def on_post_text_command(self, view, command_name, args):
        if command_name == 'set_file_type':
            sublime.set_timeout(lambda: prepare(view), 100)

    def on_load(self, view):
        sublime.set_timeout(lambda: prepare(view), 100)

    def on_activated(self, view):
        sublime.set_timeout(lambda: prepare(view), 100)

    def on_close(self, view):
        _cache.pop(view.id(), None)


def plugin_loaded():
    for window in sublime.windows():
        for view in window.views():
            prepare(view)


def plugin_unloaded():
    _cache.clear()
    for window in sublime.windows():
        for view in window.views():
            view.settings().erase('_fortios_prepared')

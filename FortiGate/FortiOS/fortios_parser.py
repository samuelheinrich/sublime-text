"""FortiOS structure reader, independent of Sublime and indentation.

Offsets are Unicode character offsets, as used by Sublime's Region API.
Only complete blocks/strings are foldable. No configuration is rewritten.
"""
import re
from collections import namedtuple


Block = namedtuple('Block', 'kind label start header_end close_start end row end_row depth parent')
Payload = namedtuple('Payload', 'field start end row end_row')
Document = namedtuple('Document', 'blocks payloads issues')
COMMAND = re.compile(r'^[ \t]*(config|edit|next|end)\b(?:[ \t]+(.*?))?[ \t]*$')
FIELD = re.compile(r'^[ \t]*(?:set|append|select)\s+(\S+)\s+')
SECRET = re.compile(r'^(?:.*password|.*passwd|.*secret|passphrase|private-key|'
                    r'certificate|ca|public-key|hostkey-.*|api-key|token)$')


def parse(text):
    blocks, payloads, issues, stack = [], [], [], []
    quote = None
    quote_start = quote_row = 0
    field = ''
    offset = 0

    def close_block(close_start, end, row):
        item = stack.pop()
        blocks.append(Block(*(item[:4] + [close_start, end, item[4], row,
                                         item[5], item[6]])))

    for row, raw in enumerate(text.splitlines(True)):
        line = raw.rstrip('\r\n')
        end = offset + len(line)
        if quote is None:
            if line.lstrip().startswith('#'):
                offset += len(raw)
                continue
            field_match = FIELD.match(line)
            field = field_match.group(1) if field_match else ''
            match = COMMAND.match(line)
            if match:
                command, label = match.groups()
                if command in ('config', 'edit') and label:
                    stack.append([command, label, offset, end, row, len(stack),
                                  stack[-1][2] if stack else None])
                elif command == 'next':
                    if stack and stack[-1][0] == 'edit':
                        close_block(offset, end, row)
                    else:
                        issues.append((row, 'next without edit'))
                elif command == 'end':
                    # FortiOS end can save an entry AND leave its table.
                    if stack and stack[-1][0] == 'edit':
                        close_block(offset, end, row)
                    if stack and stack[-1][0] == 'config':
                        close_block(offset, end, row)
                    else:
                        issues.append((row, 'end without config'))
            if field_match:
                value_start = field_match.end()
                value = line[value_start:]
                if value.startswith('ENC ') or (SECRET.match(field) and not value.startswith(('"', "'"))):
                    payloads.append(Payload(field, offset + value_start, end, row, row))

        escaped = False
        for col, char in enumerate(line):
            if escaped:
                escaped = False
                continue
            if char == '\\':
                escaped = True
                continue
            if quote:
                if char == quote:
                    if field and (row > quote_row or SECRET.match(field)):
                        payloads.append(Payload(field, quote_start + 1, offset + col,
                                                quote_row, row))
                    quote = None
            elif char in ('"', "'"):
                quote, quote_start, quote_row = char, offset + col, row
        offset += len(raw)

    issues.extend((item[4], 'unclosed ' + item[0]) for item in stack)
    if quote:
        issues.append((quote_row, 'unclosed string'))
    blocks.sort(key=lambda b: b.start)
    return Document(blocks, payloads, issues)


def outermost(blocks):
    """Choose non-overlapping outer blocks in document order in O(n log n)."""
    result = []
    until = -1
    for block in sorted(blocks, key=lambda b: (b.start, -b.end)):
        if block.start >= until:
            result.append(block)
            until = block.end
    return result


def is_wrapper(block):
    return block.kind == 'config' and block.label in ('global', 'vdom')


def section_blocks(document):
    """Expose useful sections inside global/VDOM envelopes."""
    return outermost(b for b in document.blocks
                     if b.kind == 'config' and not is_wrapper(b))

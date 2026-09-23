"""Create a non-deployable folding fixture without copying configuration values.

Only reviewed config paths, parameter names, commands and whitespace survive.
All values (including numbers), object names, comments and payloads are generated.
Unknown commands/paths and malformed quotes cause failure before any output write.
"""
import argparse
import ipaddress
import json
import re
from pathlib import Path


TOKEN = re.compile(r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|(?:\\.|[^\s"'\\])+''', re.S)
PATHS = set(json.loads(Path(__file__).with_name('sanitizer_config_paths.json').read_text()))
MARKER = 'REDACTED-NOT-A-REAL-SECRET-'


def tokenize(value):
    end = 0
    result = []
    for match in TOKEN.finditer(value):
        if value[end:match.start()].strip():
            raise ValueError('Unsupported token syntax')
        result.append(match.group())
        end = match.end()
    if value[end:].strip():
        raise ValueError('Unterminated or unsupported value')
    return result


def path_shape(tokens):
    return ' '.join('<value>' if t.startswith(('"', "'")) or t.isdigit() else t
                    for t in tokens)


def statements(text):
    quote = None
    pending = []
    for line in text.splitlines(True):
        if not pending and line.lstrip().startswith('#'):
            yield line
            continue
        pending.append(line)
        escaped = False
        for char in line.rstrip('\r\n'):
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif quote:
                if char == quote:
                    quote = None
            elif char in ('"', "'"):
                quote = char
        if quote is None:
            yield ''.join(pending)
            pending = []
    if pending:
        raise ValueError('Unterminated quoted value; refusing to write a fixture')


class Sanitizer:
    def __init__(self):
        self.counter = 0

    def value(self, token, field='', object_name=False):
        self.counter += 1
        index = self.counter
        quoted = token.startswith(('"', "'"))
        value = token[1:-1] if quoted else token
        quote = token[0] if quoted else ''
        line_count = value.count('\n') + 1

        if line_count > 1:
            lines = ['REDACTED-LINE-{0:04d}'.format(i + 1) for i in range(line_count)]
            pem = re.match(r'^-----BEGIN (CERTIFICATE|ENCRYPTED PRIVATE KEY|OPENSSH PRIVATE KEY|PRIVATE KEY|PUBLIC KEY)-----', value)
            if pem:
                kind = pem.group(1)
                lines[0] = '-----BEGIN ' + kind + '-----'
                lines[-1] = '-----END ' + kind + '-----'
            elif field in ('buffer', 'content', 'http-body'):
                lines[0], lines[-1] = '<html><!-- SYNTHETIC TEST TEXT -->', '</html>'
            return quote + '\n'.join(lines) + quote

        if object_name:
            new = 'demo-object-{0:05d}'.format(index) if quoted else str(index)
        elif re.search(r'password|passwd|secret|key|token|certificate|^ca$|passphrase|community', field):
            new = MARKER * 5
        elif field in ('hostname', 'fqdn', 'wildcard-fqdn', 'server-hostname', 'domain'):
            new = 'host-{0}.example.invalid'.format(index)
        elif field in ('url', 'uri'):
            new = 'https://example.invalid/test-{0}'.format(index)
        elif field in ('uuid', 'guid', 'ibeacon-uuid'):
            new = '00000000-0000-4000-8000-{0:012d}'.format(index)
        elif field in ('status', 'nat', 'utm-status'):
            new = 'enable' if index % 2 else 'disable'
        elif field == 'action':
            new = 'accept' if index % 2 else 'deny'
        elif field == 'allowaccess':
            new = 'ping'
        elif field == 'protocol':
            new = 'tcp'
        else:
            try:
                address = ipaddress.ip_interface(value)
            except ValueError:
                address = None
            if address:
                new = ('192.0.2.' + str(index % 254 + 1) if address.version == 4
                       else '2001:db8::{0:x}'.format(index))
                if '/' in value:
                    new += '/24' if address.version == 4 else '/64'
            elif re.fullmatch(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', value):
                new = '02:00:00:{0:02x}:{1:02x}:{2:02x}'.format(
                    (index >> 16) & 255, (index >> 8) & 255, index & 255)
            elif re.fullmatch(r'-?\d+(?:[-:]\d+)*', value):
                new = str(index % 100 + 1)
            else:
                new = 'demo-value-{0:05d}'.format(index)
        return quote + new + quote

    def statement(self, raw):
        ending = '\n' if raw.endswith('\n') else ''
        line = raw.rstrip('\r\n')
        if not line.strip():
            return ending
        if line.lstrip().startswith('#'):
            return '# SYNTHETIC TEST FIXTURE - ALL ORIGINAL VALUES REMOVED' + ending
        match = re.match(r'^([ \t]*)([a-z]+)(?:[ \t]+(.*))?$', line, re.S)
        if not match:
            raise ValueError('Unsupported statement; refusing to write a fixture')
        indent, command, rest = match.groups()
        tokens = tokenize(rest or '')
        if command in ('next', 'end') and not tokens:
            result = command
        elif command == 'config':
            if path_shape(tokens) not in PATHS:
                raise ValueError('Unreviewed config path; refusing to copy it')
            result = 'config ' + ' '.join(
                self.value(t, object_name=True) if t.startswith(('"', "'")) or t.isdigit() else t
                for t in tokens)
        elif command == 'edit' and len(tokens) == 1:
            result = 'edit ' + self.value(tokens[0], object_name=True)
        elif command in ('set', 'append', 'select', 'unselect', 'unset') and tokens:
            field = tokens[0]
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', field):
                raise ValueError('Unsupported parameter name')
            values = tokens[1:]
            if values and values[0] == 'ENC':
                # Generate the entire encrypted value, retaining only its syntax.
                values = ['ENC', MARKER * 5]
            else:
                values = [self.value(t, field) for t in values]
            result = ' '.join([command, field] + values)
        else:
            raise ValueError('Unsupported command; refusing to copy it')
        return indent + result + ending


def sanitize(text):
    sanitizer = Sanitizer()
    return ''.join(sanitizer.statement(s) for s in statements(text))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        parser.error('Output must differ from the original file')
    result = sanitize(args.source.read_text(encoding='utf-8-sig'))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Never overwrite an existing original, fixture, or symlink target.
    with args.output.open('x', encoding='utf-8', newline='\n') as target:
        target.write(result)
    print('Synthetic fixture written: {0} lines'.format(len(result.splitlines())))


if __name__ == '__main__':
    main()

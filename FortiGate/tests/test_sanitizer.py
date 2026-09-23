import sys
import re
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'FortiOS'))
from sanitize_config import sanitize, statements, tokenize, MARKER
from fortios_parser import parse


class SanitizerTests(unittest.TestCase):
    def test_public_fixture_contains_only_generated_values(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / 'examples' / 'fortigate-sanitized.fgt').read_text()
        allowed = re.compile(
            r'(?:demo-(?:value|object)-\d+|host-\d+\.example\.invalid|'
            r'https://example\.invalid/test-\d+|00000000-0000-4000-8000-\d{12}|'
            r'192\.0\.2\.\d+|2001:db8::[0-9a-f]+|02:00:00(?::[0-9a-f]{2}){3}|'
            r'\d+|enable|disable|accept|deny|ping|tcp|ENC|'
            r'(?:REDACTED-NOT-A-REAL-SECRET-)+)(?:/(?:24|64))?')
        multiline = re.compile(
            r'REDACTED-LINE-\d+|-----(?:BEGIN|END) '
            r'(?:CERTIFICATE|ENCRYPTED PRIVATE KEY|OPENSSH PRIVATE KEY|PRIVATE KEY|PUBLIC KEY)-----|'
            r'<html><!-- SYNTHETIC TEST TEXT -->|</html>')
        count = 0
        for statement in statements(text):
            line = statement.strip()
            if not line or line.startswith('#'):
                continue
            tokens = tokenize(line)
            if tokens[0] == 'edit':
                values = tokens[1:]
            elif tokens[0] in ('set', 'append', 'select', 'unselect', 'unset'):
                values = tokens[2:]
            elif tokens[0] == 'config':
                values = [t for t in tokens[1:] if t.startswith(('"', "'")) or t.isdigit()]
            else:
                values = []
            for token in values:
                value = token[1:-1] if token.startswith(('"', "'")) else token
                if '\n' in value:
                    self.assertTrue(all(multiline.fullmatch(row) for row in value.splitlines()))
                else:
                    self.assertIsNotNone(allowed.fullmatch(value))
                count += 1
        self.assertEqual(count, 12657)

    def test_users_radius_addresses_and_unknown_fields(self):
        source = ('# hardware-and-user-metadata\nconfig user radius\n'
                  'edit "private-server-name"\nset server "10.99.88.77"\n'
                  'set secret "private-shared-value"\n'
                  'set unexpected-field "private-extra-value"\n'
                  'set username "private-account"\nnext\nend\n')
        output = sanitize(source)
        for value in ('hardware-and-user-metadata', 'private-server-name', '10.99.88.77',
                      'private-shared-value', 'private-extra-value', 'private-account'):
            self.assertNotIn(value, output)
        self.assertIn('config user radius', output)
        self.assertIn(MARKER, output)
        self.assertFalse(parse(output).issues)

    def test_multiline_payloads_and_embedded_commands_are_removed(self):
        source = ('config system automation-action\nedit "private-task"\n'
                  'set script "show private-data\nconfig private-path\nend"\nnext\nend\n')
        output = sanitize(source)
        self.assertNotIn('private-', output)
        self.assertEqual(len(source.splitlines()), len(output.splitlines()))
        self.assertEqual(len(parse(output).blocks), 2)

    def test_pem_body_and_encrypted_values_are_replaced(self):
        source = ('config certificate local\nedit "private-cert"\n'
                  'set private-key "-----BEGIN PRIVATE KEY-----\n'
                  'original-private-payload\n-----END PRIVATE KEY-----"\n'
                  'set password ENC original-encrypted-value\nnext\nend\n')
        output = sanitize(source)
        self.assertNotIn('original-', output)
        self.assertNotIn('private-cert', output)
        self.assertIn('-----BEGIN PRIVATE KEY-----', output)
        self.assertIn('set password ENC ' + MARKER, output)

    def test_quotes_escapes_numbers_and_single_quoted_strings(self):
        source = ('config system global\nset hostname \'private-host\'\n'
                  'set admin-sport 65432\nset alias "private-\\"label"\nend\n')
        output = sanitize(source)
        self.assertNotIn('private-', output)
        self.assertNotIn('65432', output)
        self.assertFalse(parse(output).issues)

    def test_quoted_config_argument_is_removed(self):
        output = sanitize('config system replacemsg http "private-template"\nend\n')
        self.assertNotIn('private-template', output)
        self.assertIn('config system replacemsg http "demo-object-', output)

    def test_unknown_paths_and_commands_fail_closed(self):
        for source in ('config unknown-private-path\nend\n', 'execute private-command\n',
                       'set hostname "unclosed\n', 'next trailing-private-data\n'):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    sanitize(source)

    def test_local_fixture_generation_and_structure(self):
        root = Path(__file__).resolve().parents[1]
        original = root / 'fortigate-sample-config.txt'
        if not original.exists():
            self.skipTest('Private local sample not distributed')
        source = original.read_text()
        fixture = (root / 'examples' / 'fortigate-sanitized.fgt').read_text()
        self.assertEqual(sanitize(source), fixture)
        shape = lambda text: [(b.kind, b.row, b.end_row, b.depth) for b in parse(text).blocks]
        self.assertEqual(shape(source), shape(fixture))


if __name__ == '__main__':
    unittest.main()

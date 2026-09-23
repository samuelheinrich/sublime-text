import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'FortiOS'))
from fortios_parser import parse, section_blocks, outermost


class ParserTests(unittest.TestCase):
    def test_nested_unindented_blocks(self):
        text = 'config firewall policy\nedit 1\nconfig nested\nedit 2\nset action accept\nnext\nend\nnext\nend\n'
        doc = parse(text)
        self.assertFalse(doc.issues)
        self.assertEqual([b.depth for b in doc.blocks], [0, 1, 2, 3])
        self.assertEqual([b.end_row for b in doc.blocks], [8, 7, 6, 5])
        self.assertEqual(doc.blocks[2].parent, doc.blocks[1].start)

    def test_end_closes_entry_and_config(self):
        doc = parse('config vdom\nedit "lab"\nconfig system settings\nset gui-ips enable\nend\nend\n')
        self.assertFalse(doc.issues)
        self.assertEqual(len(doc.blocks), 3)
        self.assertEqual(doc.blocks[0].end, doc.blocks[1].end)
        self.assertEqual([b.label for b in section_blocks(doc)], ['system settings'])

    def test_commands_and_hashes_inside_payload_are_not_structure(self):
        text = 'config system automation-action\nedit "demo"\nset script "show\nconfig fake\nedit bogus\n# quote \\"\nnext\nend\n"\nnext\nend\n'
        doc = parse(text)
        self.assertFalse(doc.issues)
        self.assertEqual(len(doc.blocks), 2)
        self.assertEqual(len(doc.payloads), 1)
        self.assertIn('config fake', text[doc.payloads[0].start:doc.payloads[0].end])

    def test_quotes_backslashes_unicode_and_crlf_offsets(self):
        text = 'config test\r\nedit "Büro"\r\nset buffer "a \\" quote\r\nend\r\nz"\r\nnext\r\nend'
        doc = parse(text)
        self.assertFalse(doc.issues)
        self.assertEqual(len(doc.blocks), 2)
        self.assertEqual(text[doc.blocks[0].close_start:], 'end')
        self.assertEqual(text[doc.payloads[0].start:doc.payloads[0].end], 'a \\" quote\r\nend\r\nz')

    def test_single_quotes(self):
        doc = parse("config demo\nedit 'one'\nset buffer 'line\nnext\nend'\nnext\nend\n")
        self.assertFalse(doc.issues)
        self.assertEqual(len(doc.blocks), 2)
        self.assertEqual(len(doc.payloads), 1)

    def test_escaped_unquoted_quote_does_not_open_string(self):
        doc = parse('config demo\nset comment a\\"b\nend\n')
        self.assertFalse(doc.issues)
        self.assertEqual(len(doc.blocks), 1)

    def test_comments_cannot_open_strings_or_blocks(self):
        doc = parse('# "broken\nconfig demo\n  # edit fake\nend\n')
        self.assertFalse(doc.issues)
        self.assertEqual(len(doc.blocks), 1)

    def test_truncated_input_is_not_folded_to_eof(self):
        doc = parse('config demo\nedit 1\nset buffer "never closed\nend\n')
        self.assertFalse(doc.blocks)
        self.assertFalse(doc.payloads)
        self.assertEqual(len(doc.issues), 3)

    def test_unmatched_closers(self):
        doc = parse('next\nend\nconfig valid\nend\n')
        self.assertEqual(len(doc.issues), 2)
        self.assertEqual(len(doc.blocks), 1)

    def test_encrypted_single_line_and_multiple_strings(self):
        text = 'set password ENC abcdef\nset member "one" "two"\nset private-key "secret"\n'
        doc = parse(text)
        self.assertEqual([text[p.start:p.end] for p in doc.payloads], ['ENC abcdef', 'secret'])

    def test_overview_keeps_global_and_vdom_open(self):
        text = 'config global\nconfig system global\nend\nend\nconfig vdom\nedit "lab"\nconfig firewall policy\nedit 1\nconfig nested\nend\nnext\nend\nend\n'
        doc = parse(text)
        self.assertFalse(doc.issues)
        self.assertEqual([b.label for b in section_blocks(doc)], ['system global', 'firewall policy'])
        self.assertEqual(len(outermost(doc.blocks)), 2)

    def test_empty_config(self):
        doc = parse('config empty\nend\n')
        self.assertFalse(doc.issues)
        self.assertEqual(doc.blocks[0].close_start - 1, doc.blocks[0].header_end)

    def test_local_sample_if_present(self):
        path = Path(__file__).resolve().parents[1] / 'fortigate-sample-config.txt'
        if not path.exists():
            self.skipTest('Private local sample not distributed')
        doc = parse(path.read_text())
        self.assertFalse(doc.issues)
        self.assertEqual(len(doc.blocks), 4893)
        self.assertEqual(sum(b.kind == 'config' for b in doc.blocks), 937)
        self.assertEqual(max(b.end_row - b.row + 1 for b in doc.blocks if b.label == 'firewall internet-service-name'), 5090)

    def test_public_large_fixture(self):
        path = Path(__file__).resolve().parents[1] / 'examples' / 'fortigate-sanitized.fgt'
        text = path.read_text()
        doc = parse(text)
        self.assertFalse(doc.issues)
        self.assertEqual(len(text.splitlines()), 19231)
        self.assertEqual(len(doc.blocks), 4893)
        self.assertEqual(sum(b.kind == 'config' for b in doc.blocks), 937)
        self.assertEqual(sum(p.end_row > p.row for p in doc.payloads), 49)


if __name__ == '__main__':
    unittest.main()

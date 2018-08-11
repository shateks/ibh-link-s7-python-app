import unittest
from ddt import ddt, data, idata, unpack

import utils

parser_set_of_data = [
    (('m200.1'),     ('M', None, 200, 1, 'BOOL')),
    (('m200.1 bool'),('M', None, 200, 1, 'BOOL')),
    (('mb200'),      ('M', None, 200, None, 'BYTE')),
    (('mb200 byte'), ('M', None, 200, None, 'BYTE')),
    (('mb200 sint'), ('M', None, 200, None, 'SINT')),
    (('mW200'),      ('M', None, 200, None, 'WORD')),
    (('mW200 word'), ('M', None, 200, None, 'WORD')),
    (('mW200 int'),  ('M', None, 200, None, 'INT')),
    (('md200 '),     ('M', None, 200, None, 'DWORD')),
    (('md200 dword'),('M', None, 200, None, 'DWORD')),
    (('md200 dint'), ('M', None, 200, None, 'DINT')),
    (('md200 real'), ('M', None, 200, None, 'REAL')),

    (('i123.1'),        ('I', None, 123, 1, 'BOOL')),
    (('E123.1'),        ('I', None, 123, 1, 'BOOL')),
    (('i123.1 bool'),   ('I', None, 123, 1, 'BOOL')),
    (('E123.1 bool'),   ('I', None, 123, 1, 'BOOL')),
    (('iW123'),         ('I', None, 123, None, 'WORD')),
    (('EW123'),         ('I', None, 123, None, 'WORD')),
    (('iW123 word'),    ('I', None, 123, None, 'WORD')),
    (('EW123 word'),    ('I', None, 123, None, 'WORD')),
    (('iW123 int'),     ('I', None, 123, None, 'INT')),
    (('EW123 int'),     ('I', None, 123, None, 'INT')),

    (('q123.1'),        ('Q', None, 123, 1, 'BOOL')),
    (('A123.1'),        ('Q', None, 123, 1, 'BOOL')),
    (('q123.1 bool'),   ('Q', None, 123, 1, 'BOOL')),
    (('A123.1 bool'),   ('Q', None, 123, 1, 'BOOL')),
    (('qW123'),         ('Q', None, 123, None, 'WORD')),
    (('AW123'),         ('Q', None, 123, None, 'WORD')),
    (('qW123 word'),    ('Q', None, 123, None, 'WORD')),
    (('AW123 word'),    ('Q', None, 123, None, 'WORD')),
    (('aW123 qnt'),     ('Q', None, 123, None, 'INT')),

    (('db300.dbx10.2'),         ('D', 300, 10, 2, 'BOOL')),
    (('db300.dbx10.2 bool'),    ('D', 300, 10, 2, 'BOOL')),
    (('db300.dbb10'),           ('D', 300, 10, None, 'BYTE')),
    (('db300.dbb10 byte'),      ('D', 300, 10, None, 'BYTE')),
    (('db300.dbb10 sint'),      ('D', 300, 10, None, 'SINT')),
    (('db300.dbw10'),           ('D', 300, 10, None, 'WORD')),
    (('db300.dbw10 word'),      ('D', 300, 10, None, 'WORD')),
    (('db300.dbw10 int'),       ('D', 300, 10, None, 'INT')),
    (('db300.dbd10'),           ('D', 300, 10, None, 'DWORD')),
    (('db300.dbd10 dword'),     ('D', 300, 10, None, 'DWORD')),
    (('db300.dbd10 dint'),      ('D', 300, 10, None, 'DINT')),
    (('db300.dbd10 real'),      ('D', 300, 10, None, 'REAL')),
    ]

@ddt
class TestPaserVariablePlc(unittest.TestCase):

    def setUp(self):
        self.t_parser = utils.PlcVariableParser()

    @idata(parser_set_of_data)
    def testParse_simple(self, tuptup):
        _text = tuptup[0]
        self.assertEqual(tuptup[1], self.t_parser.parse_simple(_text))

import unittest
from ddt import ddt, data, idata, unpack

import utils

parser_set_of_data = [
    (('m200.1'),     ('M', 200, None, 1, 'BOOL')),
    (('m200.1 bool'),('M', 200, None, 1, 'BOOL')),
    (('mb200'),      ('M', 200, None, None, 'BYTE')),
    (('mb200 byte'), ('M', 200, None, None, 'BYTE')),
    (('mb200 sint'), ('M', 200, None, None, 'SINT')),
    (('mW200'),      ('M', 200, None, None, 'WORD')),
    (('mW200 word'), ('M', 200, None, None, 'WORD')),
    (('mW200 int'),  ('M', 200, None, None, 'INT')),
    (('md200 '),     ('M', 200, None, None, 'DWORD')),
    (('md200 dword'),('M', 200, None, None, 'DWORD')),
    (('md200 dint'), ('M', 200, None, None, 'DINT')),
    (('md200 real'), ('M', 200, None, None, 'REAL')),

    (('i123.1'),        ('I', 123, None, 1, 'BOOL')),
    (('E123.1'),        ('I', 123, None, 1, 'BOOL')),
    (('i123.1 bool'),   ('I', 123, None, 1, 'BOOL')),
    (('E123.1 bool'),   ('I', 123, None, 1, 'BOOL')),
    (('iW123'),         ('I', 123, None, None, 'WORD')),
    (('EW123'),         ('I', 123, None, None, 'WORD')),
    (('iW123 word'),    ('I', 123, None, None, 'WORD')),
    (('EW123 word'),    ('I', 123, None, None, 'WORD')),
    (('iW123 int'),     ('I', 123, None, None, 'INT')),
    (('EW123 int'),     ('I', 123, None, None, 'INT')),

    (('q123.1'),        ('Q', 123, None, 1, 'BOOL')),
    (('A123.1'),        ('Q', 123, None, 1, 'BOOL')),
    (('q123.1 bool'),   ('Q', 123, None, 1, 'BOOL')),
    (('A123.1 bool'),   ('Q', 123, None, 1, 'BOOL')),
    (('qW123'),         ('Q', 123, None, None, 'WORD')),
    (('AW123'),         ('Q', 123, None, None, 'WORD')),
    (('qW123 word'),    ('Q', 123, None, None, 'WORD')),
    (('AW123 word'),    ('Q', 123, None, None, 'WORD')),
    (('aW123 int'),     ('Q', 123, None, None, 'INT')),

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

parser_set_of_data_should_fail = [
    'm200', 'MD30.2', 'i22', 'q3',
    'db20dbx12.2', 'd2.dbx3.2', 'db3,dbx40.2', 'db2.dbx3,2',
    'm23.8', 'db2.dbx23.8',
    'mw30real', 'db1.dbb3 dword', 'db1.dbb3 int'
    ]

@ddt
class TestPaserVariablePlc(unittest.TestCase):

    def setUp(self):
        self.t_parser = utils.PlcVariableParser()

    @idata(parser_set_of_data)
    def testParse(self, tuptup):
        _text = tuptup[0]
        self.assertEqual(tuptup[1], self.t_parser.parse(_text))

    @idata(parser_set_of_data_should_fail)
    def testParseFail(self,val):
        self.assertRaises(ValueError, self.t_parser.parse, val)
        # with self.assertRaises(ValueError):
        #     self.t_parser.parse(val)

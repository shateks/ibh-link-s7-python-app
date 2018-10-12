import unittest
from ddt import ddt, data, idata, unpack

import utils
from data_plc import DataType, Action, DEFAULT_RANGE

parser_set_of_data = [
    (('m200.1'),     ('M', 200, None, 1, DataType.BOOL, None, None)),
    (('m200.1 bool'),('M', 200, None, 1, DataType.BOOL, None, None)),
    (('mb200'),      ('M', 200, None, None, DataType.BYTE, None, DEFAULT_RANGE[DataType.BYTE])),
    (('mb200 byte'), ('M', 200, None, None, DataType.BYTE, None, DEFAULT_RANGE[DataType.BYTE])),
    (('mb200 sint'), ('M', 200, None, None, DataType.SINT, None, DEFAULT_RANGE[DataType.SINT])),
    (('mb200 sint, write'), ('M', 200, None, None, DataType.SINT, Action.WRITE, DEFAULT_RANGE[DataType.SINT])),
    (('mW200'),      ('M', 200, None, None, DataType.WORD, None, DEFAULT_RANGE[DataType.WORD])),
    (('mW200 word'), ('M', 200, None, None, DataType.WORD, None, DEFAULT_RANGE[DataType.WORD])),
    (('mW200 word range(99,400)'), ('M', 200, None, None, DataType.WORD, None, (99, 400))),
    (('mW200 int'),  ('M', 200, None, None, DataType.INT, None, DEFAULT_RANGE[DataType.INT])),
    (('mW200 int range(-3,+50)'),  ('M', 200, None, None, DataType.INT, None, (-3, 50))),
    (('md200 '),     ('M', 200, None, None, DataType.DWORD, None, DEFAULT_RANGE[DataType.DWORD])),
    (('md200 dword'),('M', 200, None, None, DataType.DWORD, None, DEFAULT_RANGE[DataType.DWORD])),
    (('md200 dint, write'), ('M', 200, None, None, DataType.DINT, Action.WRITE, DEFAULT_RANGE[DataType.DINT])),
    (('md200 real'), ('M', 200, None, None, DataType.REAL, None, DEFAULT_RANGE[DataType.REAL])),

    (('i123.1'),        ('I', 123, None, 1, DataType.BOOL, None, None)),
    (('E123.1'),        ('I', 123, None, 1, DataType.BOOL, None, None)),
    (('i123.1 bool'),   ('I', 123, None, 1, DataType.BOOL, None, None)),
    (('E123.1 bool'),   ('I', 123, None, 1, DataType.BOOL, None, None)),
    (('iW123'),         ('I', 123, None, None, DataType.WORD, None, DEFAULT_RANGE[DataType.WORD])),
    (('EW123'),         ('I', 123, None, None, DataType.WORD, None, DEFAULT_RANGE[DataType.WORD])),
    (('iW123 word'),    ('I', 123, None, None, DataType.WORD, None, DEFAULT_RANGE[DataType.WORD])),
    (('EW123 word'),    ('I', 123, None, None, DataType.WORD, None, DEFAULT_RANGE[DataType.WORD])),
    (('iW123 int'),     ('I', 123, None, None, DataType.INT, None, DEFAULT_RANGE[DataType.INT])),
    (('EW123 int'),     ('I', 123, None, None, DataType.INT, None, DEFAULT_RANGE[DataType.INT])),

    (('q123.1 s'),        ('Q', 123, None, 1, DataType.BOOL, Action.SET, None)),
    (('q123.1,set'),        ('Q', 123, None, 1, DataType.BOOL, Action.SET, None)),
    (('A123.1,r'),        ('Q', 123, None, 1, DataType.BOOL, Action.RESET, None)),
    (('A123.1 r'),        ('Q', 123, None, 1, DataType.BOOL, Action.RESET, None)),
    (('q123.1 bool'),     ('Q', 123, None, 1, DataType.BOOL, None, None)),
    (('A123.1 bool'),     ('Q', 123, None, 1, DataType.BOOL, None, None)),
    (('A123.1 bool set'), ('Q', 123, None, 1, DataType.BOOL, Action.SET, None)),
    (('qW123'),       ('Q', 123, None, None, DataType.WORD, None, DEFAULT_RANGE[DataType.WORD])),
    (('qW123 range(0,100)'),       ('Q', 123, None, None, DataType.WORD, None, (0,100))),
    (('qW123,write'),       ('Q', 123, None, None, DataType.WORD, Action.WRITE, DEFAULT_RANGE[DataType.WORD])),
    (('qW123'),           ('Q', 123, None, None, DataType.WORD, None, DEFAULT_RANGE[DataType.WORD])),
    (('QB123 write'),           ('Q', 123, None, None, DataType.BYTE, Action.WRITE, DEFAULT_RANGE[DataType.BYTE])),
    (('AW123'),         ('Q', 123, None, None, DataType.WORD, None, DEFAULT_RANGE[DataType.WORD])),
    (('qW123 word'),    ('Q', 123, None, None, DataType.WORD, None, DEFAULT_RANGE[DataType.WORD])),
    (('AW123 word'),    ('Q', 123, None, None, DataType.WORD, None, DEFAULT_RANGE[DataType.WORD])),
    (('aW123 int'),     ('Q', 123, None, None, DataType.INT, None, DEFAULT_RANGE[DataType.INT])),

    (('db300.dbx10.2'),         ('D', 300, 10, 2, DataType.BOOL, None, None)),
    (('db300.dbx10.2 bool'),    ('D', 300, 10, 2, DataType.BOOL, None, None)),
    (('db300.dbx10.2,set'),     ('D', 300, 10, 2, DataType.BOOL, Action.SET, None)),
    (('db300.dbx10.2 bool Reset'), ('D', 300, 10, 2, DataType.BOOL, Action.RESET, None)),
    (('db300.dbx10.2 bool toggle'),('D', 300, 10, 2, DataType.BOOL, Action.TOGGLE, None)),
    (('db300.dbb10'),           ('D', 300, 10, None, DataType.BYTE, None, DEFAULT_RANGE[DataType.BYTE])),
    (('db300.dbb10 byte write'),('D', 300, 10, None, DataType.BYTE, Action.WRITE, DEFAULT_RANGE[DataType.BYTE])),
    (('db300.dbb10 sint'),      ('D', 300, 10, None, DataType.SINT, None, DEFAULT_RANGE[DataType.SINT])),
    (('db300.dbw10'),           ('D', 300, 10, None, DataType.WORD, None, DEFAULT_RANGE[DataType.WORD])),
    (('db300.dbw10 word'),      ('D', 300, 10, None, DataType.WORD, None, DEFAULT_RANGE[DataType.WORD])),
    (('db300.dbw10 int'),       ('D', 300, 10, None, DataType.INT, None, DEFAULT_RANGE[DataType.INT])),
    (('db300.dbd10'),           ('D', 300, 10, None, DataType.DWORD, None, DEFAULT_RANGE[DataType.DWORD])),
    (('db300.dbd10 dword'),     ('D', 300, 10, None, DataType.DWORD, None, DEFAULT_RANGE[DataType.DWORD])),
    (('db300.dbd10 dint'),      ('D', 300, 10, None, DataType.DINT, None, DEFAULT_RANGE[DataType.DINT])),
    (('db300.dbd10 real'),      ('D', 300, 10, None, DataType.REAL, None, DEFAULT_RANGE[DataType.REAL])),
    ]

parser_set_of_data_should_fail = [
    'm200', 'MD30.2', 'i22', 'q3',
    'db20dbx12.2', 'd2.dbx3.2', 'db3,dbx40.2', 'db2.dbx3,2',
    'm23.8', 'db2.dbx23.8',
    'mw30real', 'db1.dbb3 dword', 'db1.dbb3 int','', 'qb123 range(0,300)', 'mW123 range(-2,300)',
    'db103.dbd10 int range(-2,300)', 'db103.dbd10 dint range(-2147483649,300)', 'db103.dbd10 byte range(-2,300)',
    'db200.dbx3.0 set range(3,100)', 'db200.dbx3.0 range(3,100) toggle', 'm300.2 reset range(2,100)',
    'db200.dbx3.0 write set', 'm300.2 range(2,100) reset', 'm300.2 write', 'm300.2 write set'
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

class TestRecursive_dict_fromkeys(unittest.TestCase):

    def testRun(self):
        input_dict = {'M': {0: 1, 1: 2, 2: 3}, 'I': {}, 'Q': {}, 'D': {100: {0: 1, 1: 2, 4: 5}, 101: {0:None, 1:0xff}}}
        output_dict = {'M': {0: None, 1: None, 2: None}, 'I': {}, 'Q': {},
                       'D': {100: {0: None, 1: None, 4: None}, 101: {0:None, 1:None}}}
        result = utils.recursive_dict_fromkeys(input_dict)
        self.assertEqual(result, output_dict)

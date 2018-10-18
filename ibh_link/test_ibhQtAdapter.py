import unittest

from ibh_link import ibh_qt_adapter


class TestDivideListsOfAddress(unittest.TestCase):

    def setUp(self):
        self.input = [0,69,2,3,4,5,6,21,70,10,100,101]
        self.out_expected = [[x for x in range(0,70)], [x for x in range(70,102)]]

    def test_divide_lists_of_address(self):
        self.assertEqual(ibh_qt_adapter.Manager.divide_lists_of_address(self.input, 70), self.out_expected)

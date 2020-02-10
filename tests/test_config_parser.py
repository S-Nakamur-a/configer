import unittest
from src.configer.command import ConfigParser


class TestConfig(unittest.TestCase):
    def test_type_hint(self):
        config_parser = ConfigParser()
        val_type = config_parser.get_type_and_default(12)
        self.assertTupleEqual(('int', 12), val_type)
        val_type = config_parser.get_type_and_default("12")
        self.assertTupleEqual(('str', "'12'"), val_type)
        val_type = config_parser.get_type_and_default(False)
        self.assertTupleEqual(('bool', False), val_type)
        val_type = config_parser.get_type_and_default(12.4)
        self.assertTupleEqual(('float', 12.4), val_type)
        val_type = config_parser.get_type_and_default(None)
        self.assertTupleEqual(('None', 'None'), val_type)
        val_type = config_parser.get_type_and_default([12, 33, 21])
        self.assertTupleEqual(('typing.Tuple[int, int, int]', '(12, 33, 21)'), val_type)
        val_type = config_parser.get_type_and_default([12, 32, 10.3])
        self.assertTupleEqual(('typing.Tuple[int, int, float]', '(12, 32, 10.3)'), val_type)
        val_type = config_parser.get_type_and_default([12, 32, [20, 11.1]])
        self.assertEqual(('typing.Tuple[int, int, typing.Tuple[int, float]]', '(12, 32, (20, 11.1))'), val_type)

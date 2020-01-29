import unittest
from src.configer.command import ConfigParser


class TestConfig(unittest.TestCase):
    def test_type_hint(self):
        config_parser = ConfigParser()
        val_type = config_parser.get_type_and_default(12)
        self.assertEqual('int', val_type)
        val_type = config_parser.get_type_and_default("12")
        self.assertEqual('str', val_type)
        val_type = config_parser.get_type_and_default(False)
        self.assertEqual('bool', val_type)
        val_type = config_parser.get_type_and_default(12.4)
        self.assertEqual('float', val_type)
        val_type = config_parser.get_type_and_default(None)
        self.assertEqual('None', val_type)
        val_type = config_parser.get_type_and_default([12, 33, 21])
        self.assertEqual('Tuple[int, int, int]', val_type)
        val_type = config_parser.get_type_and_default([12, 32, 10.3])
        self.assertEqual('Tuple[int, int, float]', val_type)
        val_type = config_parser.get_type_and_default([12, 32, [20, 11.1]])
        self.assertEqual('Tuple[int, int, Tuple[int, float]]', val_type)

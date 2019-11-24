import unittest
from pathlib import Path
from src.configer.command import Configer


class TestConfig(unittest.TestCase):
    def setUp(self):
        project_dir = Path(__file__).parent.parent
        self.config_path = project_dir / 'tests' / 'setting' / 'setting.yaml'

        Configer.create_from_files(
            self.config_path,
            project_dir / 'tests' / 'config.py')

    def test_load(self):
        from tests.config import Config
        config = Config.load(self.config_path)
        config.pprint(wait_yes=False)
        self.assertEqual(config.training.batchsize, 64)
        self.assertEqual(config.models.BaseMLP.batch_norm, False)
        self.assertEqual(config.use_model, 'BaseMLP')

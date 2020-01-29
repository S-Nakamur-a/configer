import os
import unittest
from pathlib import Path
from src.configer.command import Configer


class TestConfig(unittest.TestCase):
    def setUp(self):
        project_dir = Path(__file__).parents[1]
        self.config_path: Path = project_dir / 'tests' / 'setting' / 'default.yml'
        self.config_models_path: Path = project_dir / 'tests' / 'setting' / 'models.yml'
        self.config_optimizer_path: Path = project_dir / 'tests' / 'setting' / 'optimizer.yml'
        self.out_path = project_dir / 'tests' / 'config.py'
        Configer.create_from_file(self.config_path, self.out_path)

    def test_load(self):
        from tests.config import ConfigGenerator

        config_generator = ConfigGenerator()
        config1 = config_generator\
            .update_by([self.config_models_path, self.config_optimizer_path])\
            .generate()
        del config_generator
        config_generator2 = ConfigGenerator()
        config2 = config_generator2.generate()
        self.assertEqual(config2.training.batchsize, 64)
        self.assertEqual(config2.models.BaseMLP.in_channels, 3)
        self.assertEqual(config2.models.BaseMLP.batch_norm, False)
        self.assertEqual(config2.use_model, 'BaseMLP')
        # os.remove(str(self.out_path))

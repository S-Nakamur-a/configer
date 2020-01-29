import os
import unittest
from pathlib import Path
from src.configer.command import Configer
import dataclasses


class TestConfig(unittest.TestCase):
    def setUp(self):
        project_dir = Path(__file__).parents[1]
        self.config_path: Path = project_dir / 'tests' / 'setting' / 'default.yml'
        self.config_models_path: Path = project_dir / 'tests' / 'setting' / 'models.yml'
        self.config_models_conflict_path: Path = project_dir / 'tests' / 'setting' / \
                                                 'models_conflict_with_optimizer.yml'
        self.config_optimizer_path: Path = project_dir / 'tests' / 'setting' / 'optimizer.yml'
        self.out_path = project_dir / 'tests' / 'config.py'
        Configer.create_from_file(self.config_path, self.out_path)

    def test_load(self):
        from tests.config import ConfigGenerator

        config = ConfigGenerator(default_from=self.config_path) \
            .update_by([self.config_models_path, self.config_optimizer_path]) \
            .generate()

        self.assertEqual(config.training.batchsize, 64)
        self.assertEqual(config.models.BaseMLP.in_channels, 3)
        self.assertEqual(config.models.BaseMLP.batch_norm, False)
        self.assertEqual(config.use_model, 'BaseMLP')

        config = ConfigGenerator(default_from=self.config_path).generate()
        self.assertEqual(config.models.BaseMLP.in_channels, 32)

        self.assertRaises(
            AssertionError,
            ConfigGenerator(default_from=self.config_path).update_by,
            [self.config_models_conflict_path, self.config_optimizer_path]
        )

        config = ConfigGenerator(default_from=self.config_path) \
            .update_by(self.config_optimizer_path) \
            .update_by(self.config_models_conflict_path) \
            .generate()

        self.assertEqual(config.optimizer.adam.alpha, 1.)

        # os.remove(str(self.out_path))
        config.pprint(wait=False)

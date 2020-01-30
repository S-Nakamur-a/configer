import os
import unittest
from pathlib import Path
from src.configer.command import Configer


class TestConfig(unittest.TestCase):
    def setUp(self):
        project_dir = Path(__file__).parents[1]
        self.config_path: Path = project_dir / 'tests' / 'setting' / 'default.yml'
        self.config_path_2: Path = project_dir / 'tests' / 'setting' / 'default_2.yml'
        self.config_models_path: Path = project_dir / 'tests' / 'setting' / 'models.yml'
        self.config_models_conflict_path: Path = project_dir / 'tests' / 'setting' / \
                                                 'models_conflict_with_optimizer.yml'
        self.config_optimizer_path: Path = project_dir / 'tests' / 'setting' / 'optimizer.yml'
        self.config_optimizer_type_error_path: Path = project_dir / 'tests' / 'setting' / 'optimizer_type_error.yml'
        self.out_path = project_dir / 'tests' / 'config.py'
        Configer.create_from_file(self.config_path, self.out_path)

    def test_load(self):
        from tests.config import ConfigGenerator, ConflictError, InvalidTypeError, ChangeDefaultError

        config = ConfigGenerator(assert_identical_to_default=True) \
            .update_by([self.config_models_path, self.config_optimizer_path]) \
            .generate()

        self.assertEqual(config.training.batchsize, 64)
        self.assertEqual(config.models.BaseMLP.in_channels, 3)
        self.assertEqual(config.models.BaseMLP.batch_norm, False)
        self.assertEqual(config.use_model, 'BaseMLP')

        config = ConfigGenerator().generate()
        self.assertEqual(config.models.BaseMLP.in_channels, 32)

        self.assertRaises(
            ConflictError,
            ConfigGenerator().update_by,
            [self.config_models_conflict_path, self.config_optimizer_path]
        )

        self.assertRaises(
            InvalidTypeError,
            ConfigGenerator().update_by(self.config_optimizer_type_error_path).generate,
        )

        self.assertRaises(
            ChangeDefaultError,
            ConfigGenerator(identical_to=self.config_path_2).generate,
        )

        config = ConfigGenerator() \
            .update_by(self.config_optimizer_path) \
            .update_by(self.config_models_conflict_path) \
            .generate()

        self.assertEqual(config.optimizer.adam.alpha, 1.)

        config.pprint(wait=False)
        out_file = self.config_path.parent / 'out.yml'
        config.save_as(out_file, 'yaml')

        config2 = ConfigGenerator().update_by(out_file).generate()
        self.assertEqual(config, config2)
        os.remove(str(self.out_path))
        os.remove(str(out_file))

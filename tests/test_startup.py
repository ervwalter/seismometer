import logging
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from seismometer import run_startup
from seismometer.configuration import ConfigProvider
from seismometer.seismogram import Seismogram


def fake_load(self, *args):
    mock_config = Mock(autospec=ConfigProvider)
    mock_config.output_dir.return_value
    self.config = mock_config
    self.dataframe = pd.DataFrame()

    self.template = "TestTemplate"


@pytest.fixture
def fake_seismo(tmp_path):
    with patch.object(Seismogram, "_load_from_config", fake_load):
        Seismogram(config_path=tmp_path / "config", output_path=tmp_path / "output")
    yield
    Seismogram.kill()


class TestStartup:
    def test_debug_logs_with_formatter(self, fake_seismo, tmp_path, capsys):
        expected_date_str = "[" + datetime.now().strftime("%Y-%m-%d")

        run_startup(config_path=tmp_path / "new_config", log_level=logging.DEBUG)

        sterr = capsys.readouterr().err
        assert sterr.startswith(expected_date_str)

    def test_seismo_killed_between_tests(self, fake_seismo, tmp_path):
        sg = Seismogram()
        assert sg.config_path == (tmp_path / "config")

    @pytest.mark.parametrize("log_level", [30, 40, 50])
    def test_logger_initialized(self, log_level, fake_seismo, tmp_path):
        run_startup(config_path=tmp_path / "new_config", log_level=log_level)

        logger = logging.getLogger("seismometer")
        assert logger.getEffectiveLevel() == log_level

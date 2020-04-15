from pathlib import Path

import pytest
import yaml


from bottica.bottica import _bottica_yaml_path, _uap_extras_yaml_path


@pytest.fixture(scope="session")
def bottica_yaml():
    """The parsed bottica yaml"""
    with open(_bottica_yaml_path, "r") as h:
        return yaml.load(h, Loader=yaml.SafeLoader)


@pytest.fixture(scope="session")
def uap_extras_yaml():
    """The parsed UAP extras"""
    with open(_uap_extras_yaml_path, "r") as h:
        return yaml.load(h, Loader=yaml.SafeLoader)

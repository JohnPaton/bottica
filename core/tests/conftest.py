from pathlib import Path

import pytest
import yaml


@pytest.fixture(scope="session")
def bottica_yaml():
    """The parsed bottica yaml"""
    bottica_path = Path(__file__).parent.parent / "bottica.yaml"
    with open(bottica_path, "r") as h:
        return yaml.load(h, Loader=yaml.SafeLoader)


@pytest.fixture(scope="session")
def schema_yaml():
    """The parsed bottica schema"""
    schema_path = Path(__file__).parent.parent / "schema.yaml"
    with open(schema_path, "r") as h:
        return yaml.load(h, Loader=yaml.SafeLoader)


@pytest.fixture(scope="session")
def uap_extras_yaml():
    """The parsed UAP extras"""
    extras_path = Path(__file__).parent.parent / "uap_extras.yaml"
    with open(extras_path, "r") as h:
        return yaml.load(h, Loader=yaml.SafeLoader)

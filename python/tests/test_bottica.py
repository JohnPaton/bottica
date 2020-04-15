import yaml
import pytest
from ua_parser import user_agent_parser

from bottica import bottica


def test_load_uap_extras(uap_extras_yaml, tmpdir, monkeypatch):
    monkeypatch.setattr(user_agent_parser, "USER_AGENT_PARSERS", [])

    with open(f"{tmpdir}/uap_extras.yaml", "w") as h:
        yaml.dump(uap_extras_yaml, h, Dumper=yaml.SafeDumper)

    bottica._load_uap_extras(f"{tmpdir}/uap_extras.yaml")

    assert len(user_agent_parser.USER_AGENT_PARSERS) == len(
        uap_extras_yaml["user_agent_parsers"]
    )


def test_paths():
    assert bottica._uap_extras_yaml_path.exists()
    assert bottica._bottica_yaml_path.exists()


class TestBottica:
    def test_init_loads_default_yaml(self, bottica_yaml):
        b = bottica.Bottica()
        assert len(b.verifiers) == len(bottica_yaml["bots"])

    def test_none_yaml_doesnt_load(self):
        b = bottica.Bottica(yaml_path=None)
        assert len(b.verifiers) == 0

    def test_init_max_tries_set(self):
        b = bottica.Bottica(max_tries=12345)
        assert b.max_tries == 12345

    @pytest.mark.parametrize(
        "ua, expected",
        [("DuckDuckGo/1.2.3", "DuckDuckBot"), ("YandexImages", "Yandexbot")],
    )
    def test_parse_uap_extras(self, ua, expected):
        b = bottica.Bottica(yaml_path=None)
        assert b.parse_ua(ua) == expected

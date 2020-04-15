from .schema import Bottica, UAPExtras


def test_bottica(bottica_yaml):
    # no assertion needed here as validators will raise exceptions if
    # there are validation errors
    Bottica(**bottica_yaml)


def test_schema(schema_yaml):
    """Test that the documented schema matches the actual tests"""
    expected = Bottica.schema()
    assert schema_yaml == expected


def test_uap_extras(uap_extras_yaml, bottica_yaml):
    uaps = UAPExtras(**uap_extras_yaml).user_agent_parsers
    bot_names = [b.name for b in Bottica(**bottica_yaml).bots]

    for uap in uaps:
        assert (
            uap.family_replacement in bot_names or uap.family_replacement is None
        ), f"{uap.family_replacement} not present in bottica bot names"

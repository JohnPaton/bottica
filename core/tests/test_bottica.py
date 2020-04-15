from .schema import Bottica, UAPExtras


def test_bottica(bottica_yaml):
    # no assertion needed here as validators will raise exceptions if
    # there are validation errors
    Bottica(**bottica_yaml)


def test_schema(schema_yaml):
    """Test that the documented schema matches the actual tests"""
    expected = Bottica.schema()
    assert schema_yaml == expected


def test_uap_extras(uap_extras_yaml):
    UAPExtras(**uap_extras_yaml)

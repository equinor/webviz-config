import pathlib
import pytest
import yaml
import jsonschema

from webviz_config._docs._create_schema import create_schema


@pytest.mark.parametrize(
    "config_file_path",
    [
        (pathlib.Path("examples") / "basic_example.yaml").read_text(),
        (pathlib.Path("examples") / "basic_example_advanced_menu.yaml").read_text(),
    ],
)
def test_schema(config_file_path: str):
    """Tests both that the generated schema is valid,
    and that the input configuration is valid according to the schema.
    """

    config = yaml.safe_load(config_file_path)
    jsonschema.validate(instance=config, schema=create_schema())

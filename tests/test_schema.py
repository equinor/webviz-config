import pathlib

import yaml
import jsonschema

from webviz_config._docs._create_schema import create_schema


def test_schema():
    """Tests both that the generated schema is valid,
    and that the input configuration is valid according to the schema.
    """

    config = yaml.safe_load(
        (pathlib.Path("examples") / "basic_example.yaml").read_text()
    )
    jsonschema.validate(instance=config, schema=create_schema())

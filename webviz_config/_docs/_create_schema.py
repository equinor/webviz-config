import copy
import pathlib
from typing import Any

from ._build_docs import get_plugin_documentation


JSON_SCHEMA = {
    "$id": "https://github.com/equinor/webviz-config",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Person",
    "type": "object",
    "properties": {
        "title": {"description": "Title of your Webviz application.", "type": "string"},
        "shared_settings": {"type": "object"},
        "pages": {
            "description": "Define the pages in your Webviz application.",
            "type": "array",
            "minLength": 1,
            "items": {
                "type": "object",
                "properties": {
                    "title": {"description": "Title of the page", "type": "string"},
                    "content": {
                        "description": "Content on the page",
                        "type": "array",
                        "items": {
                            "oneOf": [
                                {"type": "string"},
                            ]
                        },
                    },
                },
                "required": ["title", "content"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["title", "pages"],
    "additionalProperties": False,
}

CONTACT_PERSON = {
    "contact_person": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"},
            "phone": {"type": ["integer", "string"]},
        },
        "additionalProperties": False,
    }
}


def create_schema() -> dict:
    def json_type(typehint: Any) -> dict:
        # pylint: disable=too-many-return-statements
        if typehint == list:
            return {"type": "array", "items": {}}
        if typehint in (str, pathlib.Path):
            return {"type": "string"}
        if typehint == bool:
            return {"type": "boolean"}
        if typehint == int:
            return {"type": "integer"}
        if typehint == float:
            return {"type": "number"}
        if typehint == dict:
            return {"type": "object"}
        return {}

    json_schema = copy.deepcopy(JSON_SCHEMA)

    # fmt: off
    content_schemas = json_schema["properties"]["pages"][  # type: ignore
        "items"]["properties"]["content"]["items"]["oneOf"]
    # fmt: on

    for package_doc in get_plugin_documentation().values():
        for plugin_doc in package_doc["plugins"]:
            content_schemas.append(
                {
                    "type": "object",
                    "properties": {
                        plugin_doc["name"]: {
                            "description": plugin_doc["description"],
                            "type": "object",
                            "properties": {
                                **{
                                    arg_name: json_type(arg_info.get("typehint"))
                                    for arg_name, arg_info in plugin_doc[
                                        "arg_info"
                                    ].items()
                                },
                                **CONTACT_PERSON,
                            },
                            "required": [
                                arg_name
                                for arg_name, arg_info in plugin_doc["arg_info"].items()
                                if arg_info["required"]
                            ],
                            "additionalProperties": False,
                        }
                    },
                    "required": [plugin_doc["name"]],
                    "additionalProperties": False,
                    "minProperties": 1,
                    "maxProperties": 1,
                }
            )

    return json_schema

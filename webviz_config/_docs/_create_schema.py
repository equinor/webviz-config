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
        "menu_options": {
            "description": "Define the menu options.",
            "type": "object",
            "properties": {
                "show_logo": {
                    "description": "State if a logo shall be shown in the menu.",
                    "type": "boolean",
                },
                "bar_position": {
                    "description": "Define where the menu bar shall be positioned:"
                    " left, top, right, bottom.",
                    "type": "string",
                },
                "drawer_position": {
                    "description": "Define where the menu drawer shall be positioned:"
                    " left or right.",
                    "type": "string",
                },
                "initially_pinned": {
                    "description": "State if the menu shall be pinned when initially showing.",
                    "type": "boolean",
                },
            },
            "additionalProperties": False,
        },
        "pages": {
            "description": "Define the pages (and potential sections and groups)"
            " in your Webviz application.",
            "type": "array",
            "minLength": 1,
            "items": {
                "type": "object",
                "oneOf": [
                    {
                        "properties": {
                            "^type$": {
                                "description": "Defines if this is a section or group (valid values"
                                ": 'section' or 'group'). If not given, this is a normal page.",
                                "type": "string",
                            },
                            "title": {
                                "description": "Title of the section or group",
                                "type": "string",
                            },
                            "content": {
                                "description": "Define the pages (and potential subgroups)"
                                " of this group or section.",
                                "type": "array",
                                "minLength": 1,
                                "items": {"$ref": "#/properties/pages/items",},
                            },
                        },
                        "required": ["title", "content", "type"],
                        "additionalProperties": False,
                    },
                    {
                        "properties": {
                            "title": {
                                "description": "Title of the page",
                                "type": "string",
                            },
                            "content": {
                                "description": "Content on the page",
                                "type": "array",
                                "items": {"oneOf": [{"type": "string"},]},
                            },
                        },
                        "required": ["title", "content"],
                        "additionalProperties": False,
                    },
                ],
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
        "items"]["oneOf"][1]["properties"]["content"]["items"]["oneOf"]
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

import copy
import pathlib
from typing import Any

from ._build_docs import get_plugin_documentation


JSON_SCHEMA = {
    "$id": "https://github.com/equinor/webviz-config",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Webviz",
    "type": "object",
    "properties": {
        "title": {"description": "Title of your Webviz application.", "type": "string"},
        "shared_settings": {"type": "object"},
        "options": {
            "type": "object",
            "menu": {
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
                    "initially_collapsed": {
                        "description": "State if all groups in menu shall initially be collapsed",
                        "type": "boolean",
                    },
                },
                "additionalProperties": False,
            },
        },
        "layout": {
            "description": "Define the pages (and potential sections and groups)"
            " in your Webviz application.",
            "type": "array",
            "minLength": 1,
            "items": {
                "oneOf": [
                    {
                        "type": "object",
                        "properties": {
                            "section": {
                                "description": "Title of the section.",
                                "type": "string",
                            },
                            "icon": {
                                "description": "Optionally set an icon for the section.",
                                "type": "string",
                            },
                            "content": {
                                "description": "Define the pages (and potential subgroups)"
                                " of this section.",
                                "type": "array",
                                "minLength": 1,
                                "items": {
                                    "type": "object",
                                    "oneOf": [
                                        {"$ref": "#/properties/layout/items/oneOf/1"},
                                        {"$ref": "#/properties/layout/items/oneOf/2"},
                                    ],
                                },
                            },
                        },
                        "required": ["section", "content"],
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "properties": {
                            "group": {
                                "description": "Title of the group.",
                                "type": "string",
                            },
                            "icon": {
                                "description": "Optionally define an icon for the group.",
                                "type": "string",
                            },
                            "content": {
                                "description": "Content of the group.",
                                "type": "array",
                                "minLength": 1,
                                "items": {
                                    "oneOf": [
                                        {"$ref": "#/properties/layout/items/oneOf/1"},
                                        {"$ref": "#/properties/layout/items/oneOf/2"},
                                    ]
                                },
                            },
                        },
                        "required": ["group", "content"],
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "properties": {
                            "page": {
                                "description": "Title of the page.",
                                "type": "string",
                            },
                            "icon": {
                                "description": "Optionally define an icon for the page.",
                                "type": "string",
                            },
                            "content": {
                                "description": "Content of the page.",
                                "type": "array",
                                "minLength": 1,
                                "items": {"oneOf": [{"type": "string"}]},
                            },
                        },
                        "required": ["page", "content"],
                        "additionalProperties": False,
                    },
                ],
            },
        },
    },
    "required": ["title", "layout"],
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
    content_schemas = json_schema["properties"]["layout"][  # type: ignore
        "items"]["oneOf"][2]["properties"]["content"]["items"]["oneOf"]
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

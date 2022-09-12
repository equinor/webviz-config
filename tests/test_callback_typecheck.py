from typing import TypedDict
from typing import Dict, List, Optional, TypedDict, _TypedDictMeta, Union  # type: ignore[attr-defined]
from webviz_config.utils import callback_typecheck, ConversionError
from enum import Enum


def test_callback_typecheck() -> None:
    class MyEnum(str, Enum):
        VALUE_1 = "value-1"

    class MyTypedDict(TypedDict):
        name: str
        year: int

    class DeepTypedDict(TypedDict):
        value: MyTypedDict

    ############################################################

    def expect_none(arg: None) -> None:
        assert arg == None

    callback_typecheck(expect_none)(None)

    ############################################################

    def expect_enum(arg: MyEnum) -> None:
        assert isinstance(arg, MyEnum)

    callback_typecheck(expect_enum)("value-1")

    ############################################################

    def expect_typed_dict(arg: MyTypedDict) -> None:
        types = [type(value) for value in arg.values()]
        assert (
            type(arg) is dict
            and set(arg.keys()) == set(MyTypedDict.__annotations__.keys())
            and set(types) == set(MyTypedDict.__annotations__.values())
        )

    callback_typecheck(expect_typed_dict)({"name": "Name", "year": 1990})

    # If any invalid key is given to a `TypedDict`, assert that a `ConversionError` is raised
    try:
        callback_typecheck(expect_typed_dict)({"name": "Name", "year2": 1990})
        assert False
    except ConversionError:
        pass
    except Exception as e:
        assert False

    ############################################################

    def expect_deep_typed_dict(arg: DeepTypedDict) -> None:
        types = [type(value) for value in arg.values()]
        assert (
            type(arg) is dict
            and set(arg.keys()) == set(DeepTypedDict.__annotations__.keys())
            # NOTE: A `TypedDict` is a `dict` at runtime
            and set(types) == set([dict])
            and set(arg["value"].keys()) == set(MyTypedDict.__annotations__.keys())
        )

    callback_typecheck(expect_deep_typed_dict)(
        {"value": {"name": "Name", "year": 1990}}
    )

    ############################################################

    def expect_int(arg: int) -> None:
        assert isinstance(arg, int)

    callback_typecheck(expect_int)("1")

    ############################################################

    def expect_float(arg: float) -> None:
        assert isinstance(arg, float)

    callback_typecheck(expect_float)("1.5")

    ############################################################

    def expect_str(arg: str) -> None:
        assert isinstance(arg, str)

    callback_typecheck(expect_str)(1)

    ############################################################

    def expect_list(arg: List[str]) -> None:
        assert isinstance(arg, list)

    callback_typecheck(expect_list)([1, 2, 3])

    ############################################################

    def expect_dict(arg: Dict[str, int]) -> None:
        assert isinstance(arg, dict)
        assert isinstance(list(arg.values())[0], int)
        assert isinstance(list(arg.keys())[0], str)

    callback_typecheck(expect_dict)({"1": 1})

    ############################################################

    def expect_optional(arg: Optional[str]) -> None:
        assert arg == None or type(arg) == str

    callback_typecheck(expect_optional)(None)
    callback_typecheck(expect_optional)("string")

    ############################################################

    def expect_union(arg: Union[str, int]) -> Union[str, int]:
        return arg

    assert type(callback_typecheck(expect_union)("1")) == str
    assert type(callback_typecheck(expect_union)(1)) == int
    assert type(callback_typecheck(expect_union)(1.5)) == str

    ############################################################

from typing import Any, Dict, List, Optional, TypedDict, Union
from enum import Enum
from webviz_config.utils import callback_typecheck, ConversionError


def test_callback_typecheck() -> None:

    # pylint: disable=too-many-locals, too-many-statements
    class MyEnum(str, Enum):
        VALUE_1 = "value-1"

    class MyTypedDict(TypedDict):
        name: str
        year: int

    class DeepTypedDict(TypedDict):
        value: MyTypedDict

    ############################################################

    def expect_none(arg: None) -> None:
        assert arg is None

    callback_typecheck(expect_none)(None)

    ############################################################

    def expect_enum(arg: MyEnum) -> None:
        assert isinstance(arg, MyEnum)

    callback_typecheck(expect_enum)("value-1")

    ############################################################

    def expect_typed_dict(arg: MyTypedDict) -> None:
        types = [type(value) for value in arg.values()]
        assert (
            isinstance(arg, dict)
            and set(arg.keys())
            == set(MyTypedDict.__annotations__.keys())  # pylint: disable=no-member
            and set(types)
            == set(MyTypedDict.__annotations__.values())  # pylint: disable=no-member
        )

    callback_typecheck(expect_typed_dict)({"name": "Name", "year": 1990})

    # If any invalid key is given to a `TypedDict`, assert that a `ConversionError` is raised
    try:
        callback_typecheck(expect_typed_dict)({"name": "Name", "year2": 1990})
        assert False
    except ConversionError:
        pass
    except Exception:  # pylint: disable=broad-except
        assert False

    ############################################################

    def expect_deep_typed_dict(arg: DeepTypedDict) -> None:
        types = [type(value) for value in arg.values()]
        assert (
            isinstance(arg, dict)
            and set(arg.keys())
            == set(DeepTypedDict.__annotations__.keys())  # pylint: disable=no-member
            # NOTE: A `TypedDict` is a `dict` at runtime
            and set(types) == set([dict])
            and set(arg["value"].keys())
            == set(MyTypedDict.__annotations__.keys())  # pylint: disable=no-member
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
        assert isinstance(arg[0], str)

    callback_typecheck(expect_list)([1, 2, 3])

    ############################################################

    def expect_dict(arg: Dict[str, int]) -> None:
        assert isinstance(arg, dict)
        assert isinstance(list(arg.values())[0], int)
        assert isinstance(list(arg.keys())[0], str)

    callback_typecheck(expect_dict)({"1": 1})

    ############################################################

    def expect_optional(arg: Optional[str]) -> Optional[str]:
        return arg

    assert callback_typecheck(expect_optional)(None) is None
    assert isinstance(callback_typecheck(expect_optional)("string"), str)

    ############################################################

    def expect_union(arg: Union[str, int]) -> Union[str, int]:
        return arg

    assert isinstance(callback_typecheck(expect_union)("1"), str)
    assert isinstance(callback_typecheck(expect_union)(1), int)
    assert isinstance(callback_typecheck(expect_union)(1.5), str)

    ############################################################

    def expect_union_list(arg: Union[List[str], str]) -> Union[List[str], str]:
        return arg

    assert isinstance(callback_typecheck(expect_union_list)(["1", "2"]), list)
    assert isinstance(callback_typecheck(expect_union_list)(["1", "2"])[0], str)
    assert isinstance(callback_typecheck(expect_union_list)("1"), str)

    ############################################################

    def expect_optional_enum(arg: Optional[MyEnum]) -> Optional[MyEnum]:
        return arg

    assert callback_typecheck(expect_optional_enum)(None) is None
    assert isinstance(callback_typecheck(expect_optional_enum)("value-1"), MyEnum)

    ############################################################

    def expect_optional_string(arg: str) -> str:
        return arg

    try:
        callback_typecheck(expect_optional_string)(None)
        assert False
    except ConversionError:
        pass
    except Exception:  # pylint: disable=broad-except
        assert False

    ############################################################

    def expect_union_string_list(
        arg: Union[str, List[str], Dict[str, str], Optional[int]]
    ) -> Union[str, List[str], Dict[str, str], Optional[int]]:
        return arg

    assert callback_typecheck(expect_union_string_list)(["1", "2"]) == ["1", "2"]
    assert callback_typecheck(expect_union_string_list)("1") == "1"
    assert callback_typecheck(expect_union_string_list)({"1": "1"}) == {"1": "1"}
    assert callback_typecheck(expect_union_string_list)(None) is None
    assert callback_typecheck(expect_union_string_list)(1) == 1

    ############################################################

    def expect_optional_dict(arg: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        return arg

    assert callback_typecheck(expect_optional_dict)({"1": "1"}) == {"1": "1"}
    assert callback_typecheck(expect_optional_dict)(None) is None

    ############################################################

    def expect_optional_dict_without_types(arg: Optional[Dict]) -> Optional[Dict]:
        return arg

    assert callback_typecheck(expect_optional_dict_without_types)({"1": "1"}) == {
        "1": "1"
    }
    assert callback_typecheck(expect_optional_dict_without_types)(None) is None

    ############################################################

    def expect_optional_dict_with_any(arg: Optional[Dict[Any, Any]]) -> Optional[dict]:
        return arg

    assert callback_typecheck(expect_optional_dict_with_any)({"1": "1"}) == {"1": "1"}
    assert callback_typecheck(expect_optional_dict_with_any)(None) is None

from typing import Optional

import pytest

from webviz_config.webviz_factory import WebvizFactory
from webviz_config.webviz_factory_registry import WebvizFactoryRegistry


# pylint: disable=no-self-use
class FactoryA(WebvizFactory):
    def create_obj_a(self) -> str:
        return "A"


class FactoryB(WebvizFactory):
    def create_obj_b(self) -> str:
        return "B"


class FactoryBSub(FactoryB):
    def create_obj_b_sub(self) -> str:
        return "B_sub"


# pylint: disable=too-few-public-methods
class UnrelatedFactory:
    pass


def create_initialized_registry() -> WebvizFactoryRegistry:
    registry = WebvizFactoryRegistry()
    registry.initialize({"MyFactory": "someValue"})
    return registry


def test_uninitialized_access() -> None:
    registry = WebvizFactoryRegistry()

    with pytest.raises(RuntimeError):
        _settings = registry.all_factory_settings


def test_initialization_and_basic_access() -> None:
    registry = create_initialized_registry()

    settings = registry.all_factory_settings
    assert "MyFactory" in settings

    factory = registry.get_factory(FactoryA)
    assert factory is None


def test_multiple_initializations() -> None:
    registry = WebvizFactoryRegistry()
    registry.initialize({"MyFactory": "someValue"})

    with pytest.raises(RuntimeError):
        registry.initialize({"MyFactory": "someValue"})


def test_set_get_factory() -> None:
    registry = create_initialized_registry()

    factory_a = FactoryA()
    registry.set_factory(FactoryA, factory_a)

    factory_b = FactoryB()
    registry.set_factory(FactoryB, factory_b)

    f_a: Optional[FactoryA] = registry.get_factory(FactoryA)
    assert f_a is factory_a

    f_b: Optional[FactoryB] = registry.get_factory(FactoryB)
    assert f_b is factory_b


def test_set_get_derived_factory() -> None:
    registry = create_initialized_registry()

    factory_b = FactoryB()
    factory_b_sub = FactoryBSub()

    registry.set_factory(FactoryB, factory_b)
    registry.set_factory(FactoryBSub, factory_b_sub)
    assert registry.get_factory(FactoryB) is factory_b
    assert registry.get_factory(FactoryBSub) is factory_b_sub

    # This should be fine
    registry.set_factory(FactoryB, factory_b_sub)
    assert registry.get_factory(FactoryB) is factory_b_sub

    # This should not be legal, but cannot currently figure out how
    # to disallow it using type hinting. Currently throws an exception
    with pytest.raises(TypeError):
        registry.set_factory(FactoryBSub, factory_b)


def test_set_mismatched_factory_types() -> None:
    registry = create_initialized_registry()

    factory_a: FactoryA = FactoryA()
    factory_b: FactoryB = FactoryB()
    factory_b_sub: FactoryBSub = FactoryBSub()

    # These four are legal
    registry.set_factory(FactoryA, factory_a)
    registry.set_factory(FactoryB, factory_b)
    registry.set_factory(FactoryB, factory_b_sub)
    registry.set_factory(FactoryBSub, factory_b_sub)

    # These are rightly caught as errors by type checking since they don't derive from WebvizFactory
    # registry.set_factory(UnrelatedFactory, UnrelatedFactory())
    # registry.set_factory(FactoryA, UnrelatedFactory())
    # registry.set_factory(FactoryA, 123)

    # The following setter calls are illegal, but can't figure out how
    # to get type hinting to disallow them
    # For now, we rely on exceptions
    with pytest.raises(TypeError):
        registry.set_factory(FactoryA, factory_b)
    with pytest.raises(TypeError):
        registry.set_factory(FactoryBSub, factory_b)


def test_get_mismatched_factory_types() -> None:
    registry = create_initialized_registry()

    _f_a: Optional[FactoryA] = None
    _f_b: Optional[FactoryB] = None
    _f_b_sub: Optional[FactoryBSub] = None

    # These four are legal and do indeed pass wrt type checking
    _f_a = registry.get_factory(FactoryA)
    _f_b = registry.get_factory(FactoryB)
    _f_b = registry.get_factory(FactoryBSub)
    _f_b_sub = registry.get_factory(FactoryBSub)

    # These are rightly caught as errors by type checking, good
    # _f_b = registry.get_factory(FactoryA)
    # _f_b_sub = registry.get_factory(FactoryB)

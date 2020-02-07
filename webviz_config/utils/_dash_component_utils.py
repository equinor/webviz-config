import math


def calculate_slider_step(
    min_value: float, max_value: float, steps: int = 100
) -> float:
    """Calculates a step value for use in e.g. dcc.RangeSlider() component
    that will always be rounded.

    The number of steps will be atleast the number
    of input steps, but might not be precisely the same due to use of the floor function.

    This function is necessary since there is currently no precision control in the underlying
    React component (https://github.com/react-component/slider/issues/275).

    """

    return 10 ** math.floor(math.log10((max_value - min_value) / steps))

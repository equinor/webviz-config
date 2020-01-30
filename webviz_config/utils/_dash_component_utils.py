import math


def calculate_slider_step(min_value: float, max_value: float, steps=100):
    """Calculates a step value for use in e.g. dcc.RangeSlider() component
    that will always be rounded."""

    return 10 ** math.floor(math.log10((max_value - min_value) / steps))

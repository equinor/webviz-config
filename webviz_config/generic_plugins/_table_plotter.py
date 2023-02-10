import base64
import inspect
from pathlib import Path
from collections import OrderedDict
from typing import Optional, List, Dict, Any

import numpy as np
import pandas as pd
from plotly.graph_objects import Figure
import plotly.express as px
from dash import html, dcc, Input, Output, Dash
import webviz_core_components as wcc

from .. import WebvizPluginABC, WebvizSettings, EncodedFile
from ..webviz_store import webvizstore
from ..common_cache import CACHE


# pylint: disable=too-many-arguments
class TablePlotter(WebvizPluginABC):
    """Adds a plotter to the webviz instance, using tabular data from a provided csv file.
If feature is requested, the data could also come from a database.

---

* **`csv_file`:** Path to the csv file containing the tabular data. \
                  Either absolute path or relative to the configuration file.
* **`plot_options`:** A dictionary of plot options to initialize the plot with.
* **`filter_cols`:** Dataframe columns that can be used to filter data.
* **`filter_defaults`:** A dictionary with column names as keys, \
                         and a list of column values that should be preselected in the filter. \
                         If a columm is not defined, all values are preselected for the column.
* **`column_color_discrete_maps`:** A dictionary with column names as keys, \
                                    each key containing a new dictionary with the columns \
                                    unique values as keys, and the color they should be \
                                    plotted with as value. Hex values needs quotes '' \
                                    to not be read as a comment.
* **`lock`:** If `True`, only the plot is shown, \
              all dropdowns for changing plot options are hidden.
"""

    def __init__(
        self,
        app: Dash,
        webviz_settings: WebvizSettings,
        csv_file: Path,
        plot_options: dict = None,
        filter_cols: list = None,
        filter_defaults: dict = None,
        column_color_discrete_maps: dict = None,
        lock: bool = False,
    ) -> None:

        super().__init__()

        self.plot_options = plot_options if plot_options else {}
        self.lock = lock
        self.csv_file = csv_file
        self.data = get_data(self.csv_file)
        self.set_filters(filter_cols)
        self.columns = list(self.data.columns)
        self.numeric_columns = list(
            self.data.select_dtypes(include=[np.number]).columns
        )
        self.filter_defaults = filter_defaults
        self.column_color_discrete_maps = column_color_discrete_maps
        self.plotly_theme = webviz_settings.theme.plotly_theme
        self.set_callbacks(app)

    def set_filters(self, filter_cols: Optional[list]) -> None:
        self.filter_cols = []
        self.use_filter = False
        if filter_cols:
            for col in filter_cols:
                if col in self.data.columns:
                    if self.data[col].nunique() != 1:
                        self.filter_cols.append(col)
            if self.filter_cols:
                self.use_filter = True

    def add_webvizstore(self) -> List[tuple]:
        return [(get_data, [{"csv_file": self.csv_file}])]

    @property
    def plots(self) -> dict:
        """A dict of available plots and their options"""
        return {
            "scatter": ["x", "y", "size", "color", "facet_col"],
            "histogram": [
                "x",
                "color",
                "facet_col",
                "barmode",
                "barnorm",
                "histnorm",
            ],
            "bar": ["x", "y", "color", "facet_col", "barmode"],
            "pie": ["values", "names"],
            "scatter_3d": ["x", "y", "z", "size", "color"],
            "line": ["x", "y", "color", "line_group", "facet_col"],
            "line_3d": ["x", "y", "z", "color"],
            "box": ["x", "y", "color", "facet_col"],
            "violin": ["x", "y", "color", "facet_col"],
            "scatter_matrix": ["dimensions", "size", "color"],
            "parallel_coordinates": ["dimensions"],
            "parallel_categories": ["dimensions"],
            "density_contour": ["x", "y", "color", "facet_col"],
        }

    @property
    def plot_args(self) -> dict:
        """A dict of possible plot options and their default values"""
        return OrderedDict(
            {
                "x": {
                    "options": self.columns,
                    "value": self.plot_options.get("x", self.columns[0]),
                    "multi": False,
                    "clearable": False,
                },
                "y": {
                    "options": self.columns,
                    "value": self.plot_options.get("y", self.columns[0]),
                    "multi": False,
                    "clearable": False,
                },
                "z": {
                    "options": self.columns,
                    "value": self.plot_options.get("z", self.columns[0]),
                    "multi": False,
                    "clearable": False,
                },
                "values": {
                    "options": self.numeric_columns,
                    "value": self.plot_options.get("values", self.numeric_columns[0]),
                    "multi": False,
                    "clearable": True,
                },
                "names": {
                    "options": self.columns,
                    "value": self.plot_options.get("names", None),
                    "multi": False,
                    "clearable": True,
                },
                "size": {
                    "options": self.numeric_columns,
                    "value": self.plot_options.get("size", None),
                    "multi": False,
                    "clearable": True,
                },
                "color": {
                    "options": self.columns,
                    "value": self.plot_options.get("color", None),
                    "multi": False,
                    "clearable": True,
                },
                "facet_col": {
                    "options": self.columns,
                    "value": self.plot_options.get("facet_col", None),
                    "multi": False,
                    "clearable": True,
                },
                "line_group": {
                    "options": self.columns,
                    "value": self.plot_options.get("line_group", None),
                    "multi": False,
                    "clearable": True,
                },
                "barmode": {
                    "options": ["stack", "group", "overlay", "relative"],
                    "value": self.plot_options.get("barmode", "stack"),
                    "multi": False,
                    "clearable": True,
                },
                "barnorm": {
                    "options": ["fraction", "percent"],
                    "value": self.plot_options.get("barnorm", None),
                    "multi": False,
                    "clearable": True,
                },
                "histnorm": {
                    "options": [
                        "percent",
                        "propability",
                        "density",
                        "propability density",
                    ],
                    "value": self.plot_options.get("histnorm", None),
                    "multi": False,
                    "clearable": True,
                },
                "trendline": {
                    "options": self.numeric_columns,
                    "value": None,
                    "multi": False,
                    "clearable": True,
                },
                "dimensions": {
                    "options": self.columns,
                    "value": self.plot_options.get("dimensions", self.columns),
                    "multi": True,
                    "clearable": True,
                },
            }
        )

    def filter_layout(self) -> Optional[list]:
        """Makes dropdowns for each dataframe column used for filtering."""
        if not self.use_filter:
            return None
        df = self.data
        dropdowns = []
        for col in self.filter_cols:
            if df[col].dtype in [np.float64, np.int64]:
                min_val = df[col].min()
                max_val = df[col].max()
                mean_val = df[col].mean()
                dropdowns.append(
                    wcc.Selectors(
                        label=col.lower().capitalize(),
                        children=dcc.RangeSlider(
                            id=self.uuid(f"filter-{col}"),
                            min=min_val,
                            max=max_val,
                            step=(max_val - min_val) / 10,
                            marks={
                                min_val: f"{min_val:.2f}",
                                mean_val: f"{mean_val:.2f}",
                                max_val: f"{max_val:.2f}",
                            },
                            value=[min_val, max_val],
                        ),
                    )
                )
            else:
                elements = list(self.data[col].unique())
                dropdowns.append(
                    wcc.Selectors(
                        label=col.lower().capitalize(),
                        children=wcc.Select(
                            id=self.uuid(f"filter-{col}"),
                            options=[{"label": i, "value": i} for i in elements],
                            value=elements
                            if self.filter_defaults is None
                            else [
                                element
                                for element in self.filter_defaults.get(col, elements)
                                if element in elements
                            ],
                            size=min(15, len(elements)),
                        ),
                    )
                )
        return wcc.Selectors(
            label="Filter options", open_details=False, children=dropdowns
        )

    def plot_option_layout(self) -> List[html.Div]:
        """Renders a dropdown widget for each plot option"""

        # The plot type dropdown is handled separate
        children = [
            wcc.Dropdown(
                label="Plot type",
                id=self.uuid("plottype"),
                clearable=False,
                options=[{"label": i, "value": i} for i in self.plots],
                value=self.plot_options.get("type", "scatter"),
            ),
        ]

        # Looping through all available plot options
        # and renders a dropdown widget
        for key, arg in self.plot_args.items():
            children.append(
                html.Div(
                    style=self.style_options_div_hidden,
                    id=self.uuid(f"div-{key}"),
                    children=[
                        wcc.Dropdown(
                            label=key,
                            id=self.uuid(f"dropdown-{key}"),
                            clearable=arg["clearable"],
                            options=[{"label": i, "value": i} for i in arg["options"]],
                            value=arg["value"],
                            multi=arg["multi"],
                        ),
                    ],
                )
            )
        return wcc.Selectors(
            label="Data and visualisation options",
            style=self.style_options_div,
            children=children,
        )

    @property
    def style_options_div(self) -> Dict[str, str]:
        """Style for active plot options"""
        return {"display": "grid"}

    @property
    def style_options_div_hidden(self) -> Dict[str, str]:
        """Style for hidden plot options"""
        return {"display": "none"}

    def axis_layout(self) -> html.Div:
        return wcc.Selectors(
            label="Plot axis options",
            open_details=False,
            children=[
                wcc.Label(
                    style={"fontSize": "0.9rem", "display": "block"},
                    children="Both min and max must be set to take effect",
                ),
                wcc.Label("X-axis", style={"fontWeight": "bold"}),
                html.Div(
                    style={"display": "flex"},
                    children=[
                        wcc.Label(style={"marginRight": "10px"}, children="Min: "),
                        dcc.Input(
                            style={"maxWidth": "80px"},
                            id=self.uuid("xaxis-min"),
                            type="number",
                            minLength=1,
                            placeholder="From data",
                        ),
                        wcc.Label(
                            style={
                                "marginLeft": "10px",
                                "marginRight": "10px",
                            },
                            children="Max: ",
                        ),
                        dcc.Input(
                            style={"maxWidth": "80px"},
                            id=self.uuid("xaxis-max"),
                            type="number",
                            minLength=1,
                            placeholder="From data",
                        ),
                    ],
                ),
                wcc.Label("Y-axis", style={"fontWeight": "bold"}),
                html.Div(
                    style={"display": "flex"},
                    children=[
                        wcc.Label(style={"marginRight": "10px"}, children="Min: "),
                        dcc.Input(
                            style={"maxWidth": "80px"},
                            id=self.uuid("yaxis-min"),
                            type="number",
                            minLength=1,
                            placeholder="From data",
                        ),
                        wcc.Label(
                            style={
                                "marginLeft": "10px",
                                "marginRight": "10px",
                            },
                            children="Max: ",
                        ),
                        dcc.Input(
                            style={"maxWidth": "80px"},
                            id=self.uuid("yaxis-max"),
                            type="number",
                            minLength=1,
                            placeholder="From data",
                        ),
                    ],
                ),
            ],
        )

    @property
    def layout(self) -> html.Div:
        plot_options_style: dict = {"display": "none"} if self.lock else {}
        return html.Div(
            children=[
                wcc.FlexBox(
                    children=[
                        html.Div(
                            id=self.uuid("selector-row"),
                            children=[
                                html.Div(
                                    style=plot_options_style,
                                    children=self.plot_option_layout(),
                                ),
                                self.filter_layout(),
                                html.Div(
                                    style=plot_options_style,
                                    children=self.axis_layout(),
                                ),
                            ],
                        ),
                        wcc.Graph(
                            id=self.uuid("graph-id"),
                            style={"height": "80vh", "width": "75%"},
                        ),
                    ],
                )
            ]
        )

    @property
    def plot_output_callbacks(self) -> List[Output]:
        """Creates list of output dependencies for callback
        The outputs are the graph, and the style of the plot options"""
        outputs = []
        outputs.append(Output(self.uuid("graph-id"), "figure"))
        for plot_arg in self.plot_args.keys():
            outputs.append(Output(self.uuid(f"div-{plot_arg}"), "style"))
        return outputs

    @property
    def plot_input_callbacks(self) -> List[Input]:
        """Creates list of input dependencies for callback
        The inputs are the plot type and the current value
        for each plot option
        """
        inputs = []
        inputs.append(Input(self.uuid("plottype"), "value"))
        for plot_arg in self.plot_args.keys():
            inputs.append(Input(self.uuid(f"dropdown-{plot_arg}"), "value"))
        for filtcol in self.filter_cols:
            inputs.append(Input(self.uuid(f"filter-{filtcol}"), "value"))
        return inputs

    def set_callbacks(self, app: Dash) -> None:
        @app.callback(self.plugin_data_output, self.plugin_data_requested)
        def _user_download_data(data_requested: Optional[int]) -> Optional[EncodedFile]:
            return (
                {
                    "filename": "table-plotter.csv",
                    "content": base64.b64encode(
                        get_data(self.csv_file).to_csv().encode()
                    ).decode("ascii"),
                    "mime_type": "text/csv",
                }
                if data_requested
                else None
            )

        @app.callback(
            self.plot_output_callbacks,
            Input(self.uuid("xaxis-min"), "value"),
            Input(self.uuid("xaxis-max"), "value"),
            Input(self.uuid("yaxis-min"), "value"),
            Input(self.uuid("yaxis-max"), "value"),
            self.plot_input_callbacks,
        )
        def _update_output(
            xaxis_min: Optional[float],
            xaxis_max: Optional[float],
            yaxis_min: Optional[float],
            yaxis_max: Optional[float],
            *args: Any,
        ) -> tuple:
            """Updates the graph and shows/hides plot options"""
            plot_type = args[0]
            # pylint: disable=protected-access
            plotfunc = getattr(px._chart_types, plot_type)
            plotargs = {}
            div_style = []
            data = self.data
            # Filter dataframe if filter columns are available
            if self.use_filter:
                plot_inputs = args[1 : -len(self.filter_cols)]
                filter_inputs = args[-len(self.filter_cols) :]
                data = filter_dataframe(data, self.filter_cols, filter_inputs)
            else:
                plot_inputs = args[1:]
            for name, plot_arg in zip(self.plot_args.keys(), plot_inputs):
                if plot_type in ["parallel_coordinates"] and name == "dimensions":
                    # This plot type only accepts numerical data
                    plot_arg = [val for val in plot_arg if val in self.numeric_columns]
                if name in self.plots[plot_type]:
                    plotargs[name] = plot_arg
                    div_style.append(self.style_options_div)

                    if (
                        name == "color"
                        and self.column_color_discrete_maps is not None
                        and plot_arg in self.column_color_discrete_maps
                        and "color_discrete_map"
                        in inspect.signature(plotfunc).parameters
                    ):
                        plotargs[
                            "color_discrete_map"
                        ] = self.column_color_discrete_maps.get(plot_arg)
                else:
                    div_style.append(self.style_options_div_hidden)
            figure: Figure = plotfunc(data, template=self.plotly_theme, **plotargs)
            if xaxis_min is not None and xaxis_max is not None:
                figure.update_layout(xaxis_range=[xaxis_min, xaxis_max])
            if yaxis_min is not None and yaxis_max is not None:
                figure.update_layout(yaxis_range=[yaxis_min, yaxis_max])

            return (figure, *div_style)


@CACHE.memoize()
@webvizstore
def get_data(csv_file: Path) -> pd.DataFrame:
    return pd.read_csv(csv_file, index_col=None)


@CACHE.memoize()
def filter_dataframe(
    dframe: pd.DataFrame, columns: list, column_values: List[list]
) -> pd.DataFrame:
    df = dframe.copy()
    if not isinstance(columns, list):
        columns = [columns]
    for filt, col in zip(column_values, columns):
        if isinstance(filt, list):
            if df[col].dtype in [np.float64, np.int64]:
                df = df.loc[df[col].between(filt[0], filt[1])]
            else:
                df = df.loc[df[col].isin(filt)]
        else:
            df = df.loc[df[col] == filt]
    return df

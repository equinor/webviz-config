import inspect
import numpy as np
import pandas as pd
from pathlib import Path
from uuid import uuid4
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from ..webviz_store import webvizstore
from ..common_cache import cache
import plotly_express as px


class PlotATable:

    def __init__(self, app, title: str, csv_file: Path,
                 plot: str = 'scatter', x: str = None, y: str = None,
                 z: str = None, size: str = None, color: str = None):

        self.title = title

        self.button_id = 'submit-button-{}'.format(uuid4())
        self.div_id = 'output-state-{}'.format(uuid4())
        self.graph_id = 'graph-id{}'.format(uuid4())
        self.graph_selector = 'graph-selector{}'.format(uuid4())
        self.csv_file = csv_file
        self.data = get_data(self.csv_file)
        self.columns = list(self.data.columns)
        self.numeric_columns = list(
            self.data.select_dtypes(include=[np.number]).columns)

        self.plot = plot
        self.x = x if x else self.columns[0]
        self.y = y if y else self.columns[0]
        self.z = z if z else self.columns[0]
        self.size = size
        self.color = color

        self.selector_row = 'selector-row{}'.format(uuid4())
        self.x_selector = 'x-selector{}'.format(uuid4())
        self.x_div_selector = 'x-div_selector{}'.format(uuid4())
        self.y_selector = 'y-selector{}'.format(uuid4())
        self.y_div_selector = 'y-div-selector{}'.format(uuid4())
        self.z_selector = 'z-selector{}'.format(uuid4())
        self.z_div_selector = 'z-div-selector{}'.format(uuid4())
        self.size_selector = 'size-selector{}'.format(uuid4())
        self.size_div_selector = 'size-div-selector{}'.format(uuid4())
        self.color_selector = 'size-selector{}'.format(uuid4())
        self.color_div_selector = 'size-div-selector{}'.format(uuid4())

        self.set_callbacks(app)

    def add_webvizstore(self):
        return [(get_data, [{'csv_file': self.csv_file}])]

    @property
    def plots(self):
        return {
            'scatter': 'scatter',
            'scatter_3d': 'scatter_3d',
            # 'scatter_polar':'scatter_polar',
            # 'scatter_ternary':'scatter_ternary',
            # 'scatter_mapbox':'scatter_mapbox',
            # 'scatter_geo':'scatter_geo',
            'line': 'line',
            'line_3d': 'line_3d',
            # 'line_polar':'line_polar',
            # 'line_ternary':'line_ternary',
            # 'line_mapbox':'line_mapbox',
            # 'line_geo':'line_geo',
            'bar': 'bar',
            # 'bar_polar':'bar_polar',
            'violin': 'violin',
            'box': 'box',
            'histogram': 'histogram',
            'scatter_matrix': 'scatter_matrix',
            'parallel_coordinates': 'parallel_coordinates',
            'parallel_categories': 'parallel_categories',
            # 'choropleth':'choropleth',
            'density_contour': 'density_contour'
        }

    @property
    def style_plot_options(self):
        '''Simple grid layout for the selector row'''
        return {
            'display': 'grid',
            'align-content': 'space-around',
            'justify-content': 'space-between',
            'grid-template-columns': 'repeat(6, 1fr)'
        }

    @property
    def layout(self):
        return html.Div([
            html.H1(self.title),
            html.Div(
                id=self.selector_row,
                style=self.style_plot_options,
                children=[
                    html.Div(children=[
                             html.P('Select plot type'),
                             dcc.Dropdown(
                                 id=self.graph_selector,
                                 clearable=False,
                                 options=[{'label': i, 'value': i}
                                          for i in self.plots.keys()],
                                 value=self.plot)
                             ]),
                    html.Div(id=self.x_div_selector, children=[
                             html.P('X column'),
                             dcc.Dropdown(
                                 id=self.x_selector,
                                 clearable=False,
                                 options=[{'label': i, 'value': i}
                                          for i in self.columns],
                                 value=self.x)
                             ]),
                    html.Div(id=self.y_div_selector, children=[
                             html.P('Y column'),
                             dcc.Dropdown(
                                 id=self.y_selector,
                                 clearable=False,
                                 options=[{'label': i, 'value': i}
                                          for i in self.columns],
                                 value=self.y)
                             ]),
                    html.Div(id=self.z_div_selector, children=[
                             html.P('Z column'),
                             dcc.Dropdown(
                                 id=self.z_selector,
                                 clearable=False,
                                 options=[{'label': i, 'value': i}
                                          for i in self.columns],
                                 value=self.z)
                             ]),
                    html.Div(id=self.size_div_selector, children=[
                             html.P('Size column'),
                             dcc.Dropdown(
                                 id=self.size_selector,
                                 clearable=True,
                                 options=[{'label': i, 'value': i}
                                          for i in self.numeric_columns],
                                 value=self.size)
                             ]),
                    html.Div(id=self.color_div_selector, children=[
                        html.P('Color column'),
                        dcc.Dropdown(
                            id=self.color_selector,
                            clearable=True,
                            options=[{'label': i, 'value': i}
                                     for i in self.columns],
                            value=self.color)
                    ])
                ]),
            dcc.Graph(id=self.graph_id)
        ])

    def set_callbacks(self, app):
        @app.callback(
            [
                Output(self.graph_id, 'figure'),
                Output(self.x_div_selector, 'style'),
                Output(self.y_div_selector, 'style'),
                Output(self.z_div_selector, 'style'),
                Output(self.size_div_selector, 'style'),
                Output(self.color_div_selector, 'style')
            ],
            [
                Input(self.graph_selector, 'value'),
                Input(self.x_selector, 'value'),
                Input(self.y_selector, 'value'),
                Input(self.z_selector, 'value'),
                Input(self.size_selector, 'value'),
                Input(self.color_selector, 'value')
            ])
        def update_output(plot_type, x, y, z, size, color):
            plotfunc = getattr(px._chart_types, self.plots[plot_type])
            plotargs = inspect.getargspec(plotfunc)._asdict()
            args = {}
            if 'x' in plotargs['args']:
                args['x'] = x
                x_style = {'display': 'block'}
            else:
                x_style = {'display': 'none'}
            if 'y' in plotargs['args']:
                args['y'] = y
                y_style = {'display': 'block'}
            else:
                y_style = {'display': 'none'}
            if 'z' in plotargs['args']:
                args['z'] = z
                z_style = {'display': 'block'}
            else:
                z_style = {'display': 'none'}
            if 'size' in plotargs['args']:
                args['size'] = size
                size_style = {'display': 'block'}
            else:
                size_style = {'display': 'none'}
            if 'color' in plotargs['args']:
                args['color'] = color
                color_style = {'display': 'block'}
            else:
                color_style = {'display': 'none'}
            return (
                plotfunc(self.data, **args),
                x_style,
                y_style,
                z_style,
                size_style,
                color_style
            )


@cache.memoize(timeout=cache.TIMEOUT)
@webvizstore
def get_data(csv_file) -> pd.DataFrame:
    return pd.read_csv(csv_file)

import abc
from uuid import uuid4
from dash.dependencies import Input, Output
import webviz_core_components as wcc


class WebvizContainer(abc.ABC):
    '''All webviz containers need to subclass this abstract base class,
    e.g.

    ```python
    class MyContainer(WebvizContainer):

        def __init__(self):
            ...

        def layout(self):
            ...
    ```
    '''

    # If set to True, there will be rendered a toolbar related to the
    # containar. The containers subclassing this abstract base class can
    # override this variable setting it to False, ensuring that container
    # type will never get a toolbar rendered.
    SHOW_TOOLBAR = True

    # List of container specific assets which should be copied
    # over to the ./assets folder in the generated webviz app.
    # This is typically custom JavaScript and/or CSS files.
    # All paths in the returned ASSETS list should be absolute.
    ASSETS = []

    @abc.abstractmethod
    def layout(self):
        '''This is the only required function of a Webviz Container.
        It returns a Dash layout which by webviz-config is added to
        the main Webviz application.
        '''
        pass

    def container_layout(self, app):
        '''This function returns (if the class constant SHOW_TOOLBAR is True,
        the container layout wrapped into a common webviz config container
        component, which provides some useful buttons like download of data,
        show data contact person and download container content to png.

        CSV download button will only appear if the container class a property
        `csv_string` which should return the appropriate csv data as a string.

        If SHOW_TOOLBAR is false, this functions returns the same dash layout
        as the container class provides directly.
        '''

        if self.__class__.SHOW_TOOLBAR:
            id_container_placeholder = f'container-{uuid4()}'
            buttons = ['screenshot']

            if hasattr(self, 'csv_string'):
                buttons.append('csv_file')

                @app.callback(Output(id_container_placeholder, 'csv_data'),
                              [Input(id_container_placeholder,
                                     'csv_requested')])
                def display_output(csv_requested):
                    if not csv_requested:
                        return ''
                    else:
                        return self.csv_string

            return wcc.WebvizContainerPlaceholder(id=id_container_placeholder,
                                                  buttons=buttons,
                                                  children=[self.layout])
        else:
            return self.layout

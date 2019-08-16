import abc
from uuid import uuid4
import bleach
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

    # This is the default set of buttons to show in the rendered container
    # toolbar. If the list is empty, the subclass container layout will be
    # used directly, without any visual encapsulation layout from this
    # abstract base class. The containers subclassing this abstract base class
    # can override this variable setting by defining a class constant with 
    # the same name.
    #
    # Some buttons will only appear if in addition necessary data is available.
    # E.g. download of csv file will only appear if the container provides
    # a property csv_string, and contact person will only appear if the
    # user configuration file has this information.
    TOOLBAR_BUTTONS = ['csv_file', 'contact_person', 'screenshot', 'expand']

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

    def container_layout(self, app, contact_person=None):
        '''This function returns (if the class constant SHOW_TOOLBAR is True,
        the container layout wrapped into a common webviz config container
        component, which provides some useful buttons like download of data,
        show data contact person and download container content to png.

        CSV download button will only appear if the container class a property
        `csv_string` which should return the appropriate csv data as a string.

        If SHOW_TOOLBAR is false, this functions returns the same dash layout
        as the container class provides directly.
        '''

        id_container_placeholder = f'container-{uuid4()}'
        buttons = self.__class__.TOOLBAR_BUTTONS

        if contact_person is None:
            contact_person = {}
        else:
            # Sanitize the configuration user input
            for key in contact_person:
                contact_person[key] = bleach.clean(contact_person[key])

        if 'csv_file' in buttons:
            if hasattr(self, 'csv_string'):
                @app.callback(Output(id_container_placeholder, 'csv_string'),
                              [Input(id_container_placeholder,
                                     'csv_requested')])
                def display_output(csv_requested):
                    return self.csv_string if csv_requested else ''
            else:
                buttons.remove('csv_file')

        if buttons:
            return wcc.WebvizContainerPlaceholder(id=id_container_placeholder,
                                                  buttons=buttons,
                                                  contact_person=contact_person,
                                                  children=[self.layout])
        else:
            return self.layout

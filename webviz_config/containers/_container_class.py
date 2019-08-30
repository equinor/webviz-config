import io
import abc
import base64
import zipfile
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
    # E.g. download of zip archive will only appear if the container also
    # has defined the corresponding callback, and contact person will only
    # appear if the user configuration file has this information.
    TOOLBAR_BUTTONS = ['screenshot', 'expand',
                       'download_zip', 'contact_person']

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

    @property
    def _container_wrapper_id(self):
        if not hasattr(self, '_container_wrapper_uuid'):
            self._container_wrapper_uuid = uuid4()
        return f'container-wrapper-{self._container_wrapper_uuid}'

    @property
    def container_data_output(self):
        self._add_download_button = True
        return Output(self._container_wrapper_id, 'zip_base64')

    @property
    def container_data_requested(self):
        return Input(self._container_wrapper_id, 'data_requested')

    @staticmethod
    def container_data_compress(content):
        byte_io = io.BytesIO()

        with zipfile.ZipFile(byte_io, 'w') as zipped_data:
            for data in content:
                zipped_data.writestr(data['filename'], data['content'])

        byte_io.seek(0)

        return base64.b64encode(byte_io.read()).decode('ascii')

    def container_layout(self, app, contact_person=None):
        '''This function returns (if the class constant SHOW_TOOLBAR is True,
        the container layout wrapped into a common webviz config container
        component, which provides some useful buttons like download of data,
        show data contact person and download container content to png.

        CSV download button will only appear if the container class a property
        `csv_string` which should return the appropriate csv data as a string.

        If TOOLBAR_BUTTONS is empty, this functions returns the same
        dash layout as the container class provides directly.
        '''

        buttons = self.__class__.TOOLBAR_BUTTONS.copy()

        if contact_person is None:
            contact_person = {}
        else:
            # Sanitize the configuration user input
            for key in contact_person:
                contact_person[key] = bleach.clean(str(contact_person[key]))

        if 'download_zip' in buttons and \
                not hasattr(self, '_add_download_button'):
            buttons.remove('download_zip')

        if buttons:
            return wcc.WebvizContainerPlaceholder(
                id=self._container_wrapper_id,
                buttons=buttons,
                contact_person=contact_person,
                children=[self.layout]
            )
        else:
            return self.layout

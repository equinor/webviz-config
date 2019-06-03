import abc


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

# Contributing to Webviz configuration utility

- [Creating a new plugin](#creating-a-new-plugin)
  - [Minimal plugin](#minimal-plugin)
  - [Override plugin toolbar](#override-plugin-toolbar)
  - [Callbacks](#callbacks)
    - [Data download callback](#data-download-callback)
  - [User provided arguments](#user-provided-arguments)
  - [Data input](#data-input)
    - [Deattaching data from its original source](#deattaching-data-from-its-original-source)
  - [Custom ad-hoc plugins](#custom-ad-hoc-plugins)
- [Run tests](#run-tests)
- [Build documentation](#build-documentation)

## Creating a new plugin

Most of the development work is towards creating standard plugins.
A plugin usually does three things:

*   It has a `layout` property, consisting of multiple
    [Dash components](https://dash.plot.ly/getting-started).

*   It has/uses functionality for getting/processing
    the data it displays/visualizes.

*   It sets some [callbacks](https://dash.plot.ly/getting-started-part-2)
    to add user interactivity triggering actions in the Python backend.

### Minimal plugin

Of the three things mentioned above, it is only the `layout` proprety that is
mandatory to provide. A minimal plugin could look like:

```python
import dash_html_components as html

from webviz_config import WebvizPluginABC


class ExamplePlugin(WebvizPluginABC):

    @property
    def layout(self):
        return html.Div([
                         html.H1('This is a static title'),
                         'And this is just some ordinary text'
                        ])
```

If the file containing `ExamplePlugin` is saved to [./webviz_config/plugins](./webviz_config/plugins),
and then added to the corresponding [\_\_init\_\_ file](./webviz_config/plugins/__init__.py)
you are done. Alternatively you can create your plugins in a separate Python project and `setup.py`.
You can then configure the installation by using something like:
```python
setup(
    ...
    entry_points={
        "webviz_config_plugins": [
            "ExamplePlugin = my_package.my_module:ExamplePlugin"
        ]
    },
    ...
)
```
See [webviz-subsurface](https://github.com/equinor/webviz-subsurface) for example of this usage.

After installation, the user can then include the plugin through a configuration file, e.g.

```yaml
title: Simple Webviz example

pages:

  - title: Front page
    content: 
      - ExamplePlugin:
```

### Override plugin toolbar

In the generated webviz application, your plugin will as default be given
a button toolbar. The default buttons to appear is stored in the class constant
`WebvizPluginABC.TOOLBAR_BUTTONS`. If you want to override which buttons should
appear, redefine this class constant in your subclass. To remove all buttons,
simply define it as an empty list. See [this section](#data-download-callback)
for more information regarding the `data_download` button.

### Callbacks

If you want to include user interactivity which triggers actions in the Python
backend, you can add callbacks. A simple example of this is given below.

```python
from uuid import uuid4

import dash_html_components as html
from dash.dependencies import Input, Output
from webviz_config import WebvizPluginABC


class ExamplePlugin(WebvizPluginABC):

    def __init__(self, app):

        super().__init__()

        self.button_id = f'submit-button-{uuid4()}'
        self.div_id = f'output-state-{uuid4()}'

        self.set_callbacks(app)

    @property
    def layout(self):
        return html.Div([
                         html.H1('This is a static title'),
                         html.Button(id=self.button_id, n_clicks=0,
                                     children='Submit'),
                         html.Div(id=self.div_id)
                        ])

    def set_callbacks(self, app):
        @app.callback(Output(self.div_id, 'children'),
                      [Input(self.button_id, 'n_clicks')])
        def _update_output(n_clicks):
            return f'Button has been pressed {n_clicks} times.'
```

Callback functions are decorated with `@app.callback`. For introduction to
callbacks, see [the dash documentation](https://dash.plot.ly/getting-started-part-2).

There are three fundamental additions to the minimal example without callbacks:

*   You add the argument `app` to your `__init__` function. This is a special
    argument name which will *not* be originating from the user configuration
    file, but rather automatically given to the plugin by the core
    functionality of `webviz-config`.

*   You add a class function `set_callbacks` which contains the different
    callbacks to add. This function is called from the `__init__` function,
    such that the callbacks are set when the plugin instance is created.

*   Since the components are reusable (i.e. a user can use the plugin
    multiple times within the same application), the plugin IDs mentioned in
    the `@app.callback(...)` decorator needs to be unique. One simple way of
    ensuring this is to create unique IDs in the `__init__` function using
    [uuid.uuid4()](https://docs.python.org/3/library/uuid.html#uuid.uuid4),
    as demonstrated in the example above.

#### Data download callback

There is a [data download button](#override-plugin-toolbar) provided by
the `WebvizPluginABC` class. However, it will only appear if the corresponding
callback is set. A typical data download callback will look like

```python
@app.callback(self.plugin_data_output,
              [self.plugin_data_requested])
def _user_download_data(data_requested):
    return WebvizPluginABC.plugin_data_compress(
        [{'filename': 'some_file.txt',
          'content': 'Some download data'}]
    ) if data_requested else ''
```
By letting the plugin define the callback, the plugin author is able
to utilize the whole callback machinery, including e.g. state of the individual
components in the plugin. This way the data downloaded can e.g. depend on
the visual state or user selection.

The attributes `self.plugin_data_output` and `self.plugin_data_requested`
are Dash `Output` and `Input` instances respectively, and are provided by
the base class `WebvizPluginABC` (i.e. include them as shown here).

The function `WebvizPluginABC.plugin_data_compress` is a utility function
which takes a list of dictionaries, giving filenames and corresponding data,
and compresses them to a zip archive which is then downloaded by the user.

### User provided arguments

Since the plugins are reusable and generic, they usually take in some
user provided arguments. A minimal example could look like:

```python
import dash_html_components as html
from webviz_config import WebvizPluginABC


class ExamplePlugin(WebvizPluginABC):

    def __init__(self, title: str, number: int=42):

        super().__init__()

        self.title = title
        self.number = number

    @property
    def layout(self):
        return html.Div([
                         html.H1(self.title),
                         f'This is your number: {self.number}'
                        ])
```

The user given configuration file can now look like this:

```yaml
title: Simple Webviz example

pages:

  - title: Front page
    content: 
      - ExamplePlugin:
          title: My special title
```

The core functionality of `webviz-config` will provide user friendly
error messages in the following scenarios:

*   A required argument is not provided (in example above, that would be if
    `title` is not stated in the configuration file).

*   An unknown argument is given (that would be something else than `title` and
    `number` in this case).

*   Mismatch between type of user provided value, and the (optionally) provided
    [type hint](https://docs.python.org/3/library/typing.html) in the
    `__init__` function.

The `__init__` function above could be replaced with an equivalent argument
specification without type hints, e.g.
```python
def __init__(self, title, number=42):
```
However, the benefit of adding type hints is that `webviz-config` will
provide an user friendly error message immediately when parsing the
configuration file, if there is a type mismatch. E.g., if the user
provided the configuration file

```yaml
title: Simple Webviz example

pages:
  - title: Front page
    content: 
      - ExamplePlugin:
          title: My special title
          number: Some text instead of number
```

this error message will be given:
```
The value provided for argument `number` given to plugin `ExamplePlugin` is of type `str`. Expected type `int`
```

An additional benefit is that if the plugin author says an argument should
be of type `pathlib.Path`, the configuration parser will make sure that
the user provided path (which is a string to begin with in configuration file,
potentially non-absolute and relative to the configuration file itself) is
given to the plugin as an absolute path, and of type `pathlib.Path`.


### Data input

The plugins get data input through ordinary Python functions.
Since these functions can be costly to call, we utilize the
[flask-caching](https://pythonhosted.org/Flask-Caching/) package.
By decorating the costly functions with `@CACHE.memoize(timeout=CACHE.TIMEOUT)`
the result is cached, such that if the same function is called more than once,
within the timeout, the cached result will be used instead of starting
a new calculation.

Functionality used by multiple plugins should be put in a common module. The
applications common cache instance can be imported using
```python
from webviz_config.common_cache import CACHE
```

#### Deattaching data from its original source

There are use cases where the generated webviz instance ideally is portable
and self-contained. At the same time, there are use cases where the data input
ideally comes from "live sources" (simulations still running, production database...).

Asking each plugin to take care of both these scenarios to the full extent
involves a lot of duplicate work. The core of `webviz-config` therefore
facilitates this transition in the following way.

Assume you have a function:
```python
import pandas as pd

def get_some_data(some, arguments) -> pd.DataFrame:
    ...
```
It takes in some possibly user given arguments, reads e.g. data somewhere from
the file system, and then returns a `pd.DataFrame`. If we want
`webviz-config` to facilitate the transition to a portable webviz instance,
the plugin author needs only do three things:

1) Import the decorator: `from webviz_config.webviz_store import webvizstore`
2) Decorate the function as this:
   ```python
   @webvizstore
   def get_some_data(some, arguments) -> pd.DataFrame:
   ```
3) In the plugin class, define a class method `add_webvizstore` which
   returns a list of tuples. The first plugin in each tuple is a reference
   to a function, the second plugin is itself a list of argument combinations.

   The author of the plugin should provide a list of all the argument
   combinations that are imaginable during runtime of the application.
   Since it is a class method, the author has access to all the user provided
   arguments.

   Arguments with a default value in the function signature does not need to
   be provided in the argument dictionaries.

A full example could look like e.g.:

```python
import pandas as pd
from webviz_config.webviz_store import webvizstore
from webviz_config.common_cache import CACHE
from webviz_config import WebvizPluginABC


class ExamplePortable(WebvizPluginABC):

    def __init__(self, some_number: int):

        super().__init__()

        self.some_number = some_number

    def add_webvizstore(self):
        return [(input_data_function, [{'some_number': self.some_number}])]

    @property
    def layout(self):
        return str(input_data_function(self.some_number))


@CACHE.memoize(timeout=CACHE.TIMEOUT)
@webvizstore
def input_data_function(some_number) -> pd.DataFrame:
    print("This time I'm actually doing the calculation...")
    return pd.DataFrame(data={'col1': [some_number,   some_number*2],
                              'col2': [some_number*3, some_number*4]})
```

Creating a portable webviz instance is done from the command line using
```bash
webviz build some_config.yaml --portable /some/outputfolder
```

The core of `webviz-config` will do the following:

1) If the user has *not* asked for a portable version (i.e. not given the 
   `--portable` command line argument, the decorator `@webvizstore` will
   not change the attached function.
2) If the user asks for a portable version, it will
   1) Before writing the actual dash code, it will run all decorated functions
      with the given argument combinations. The resulting dataframes are stored
      in a folder `./webviz_storage` as parquet files.
   2) It writes the webviz-dash code (as usual), but this the decorated
      functions will return the dataframe from the stored `.parquet` files,
      instead of running the actual function code.

Currently only functions returning `pd.DataFrame`, `io.BytesIO` or `pathlib.Path` are
supported. A `NotImplementedError` will be raised if the function being
decorated with `@webvizstore` does not have a type hint being supported.

If the return type is `pathlib.Path`, the file corresponding to the path will
be copied over to the portable `webviz` instance, and the decorated function
will return a `pathlib.Path` instance pointing to the stored file. For most
use cases, the decorated function `get_resource` in
`webviz_config.webviz_store` can be imported and used.


> :bookmark_tabs: The argument hashing method used for `@webvizstore` is using
the same principles as in the `flask-caching` package.
The input arguments to a function decorated with `@webvizstore` could be
mutable objects like e.g. instances of a class, but make sure that the object
has a `__repr__` function associated with it such that instances representing
different input also have different string output from `__repr__`.

> :rocket: If you nest decorations, e.g. use both `@webvizstore` and
`@CACHE.memoize`, following the same order as in the example above usually gives 
best performance.

### Common settings

If you create multiple plugins that have some settings in common, you can
_"subscribe"_ to keys in the dictionary `shared_settings`, defined by the user
in the configuration file. E.g. assume that the user enters something like this at
top level in the configuration file:
```yaml
shared_settings:
  some_key:
    some_settings1: ...
    some_settings2: ...
```

You can then early in the application loading process get to run a function checking,
and potentially transforming, the settings. The latter is useful e.g. if you want to
convert some string, representing a path relative to the configuration file, to an
absolute path.

The way you subscribe to a shared setting is that you in your Python package add
something like
```python
import webviz_config

@webviz_config.SHARED_SETTINGS_SUBSCRIPTIONS.subscribe("some_key")
def subscribe(some_key, config_folder, portable):
    # The input argument some_key given to this function is equal to
    # shared_settings["some_key"] provided by the user from the configuration file.

    # Do some checks on the settings?

    # Do some transformation on the settings?

    return some_key # The returned value here is put back into shared_settings["some_key"]
```

The (optionally transformed) `shared_settings` are accessible to plugins through
the `app` instance (see [callbacks](#callbacks)). E.g., in this case the wanted settings
are found as `app.webviz_settings["shared_settings"]["some_key"]`.

Stating the input arguments named `config_folder` and/or `portable` in the function
signature is not necessary, however if you do you will get a
[`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path)
instance representing the absolute path to the configuration file that was used, and/or
a boolean value stating if the Webviz application running is a portable one.

### Custom ad-hoc plugins

It is possible to create custom plugins which still can be included through
the configuration file, which could be useful for quick prototyping.

As an example, assume someone on your project has made the Python file

```python
import dash_html_components as html
from webviz_config import WebvizPluginABC


class OurCustomPlugin(WebvizPluginABC):

    def __init__(self, title: str):

        super().__init__()

        self.title = title

    @property
    def layout(self):
        return html.Div([
                         html.H1(self.title),
                         'This is just some ordinary text'
                        ])
```

If this is saved such that it is available through e.g. a
[module](https://docs.python.org/3/tutorial/modules.html)
`ourmodule`, the user can include the custom plugin the same way as a standard
plugin, with the only change of also naming the module:
```yaml
title: Simple Webviz example

pages:

  - title: Front page
    content: 
      - ourmodule.OurCustomPlugin:
          title: Title of my custom plugin
```

Note that this might involve appending your `$PYTHONPATH` environment
variable with the path where your custom module is located. The same principle
applies if the custom plugin is saved in a package with submodule(s),
```yaml
    ...
      - ourpackage.ourmodule.OurCustomPlugin:
          ...
```

## Run tests

To run tests it is necessary to first install the [selenium chrome driver](https://github.com/SeleniumHQ/selenium/wiki/ChromeDriver).
Then install the Python development requirements:
```bash
pip install .[tests]
pip install dash[testing]
```
The second of these commands appears to be necessary as long as
[this `pip` issue is open](https://github.com/pypa/pip/issues/4957).

You can then run the tests using
```bash
pytest tests --forked
```

Linting can be checked by:
```bash
black --check webviz_config tests
```

## Build documentation

End-user documentation (i.e. YAML configuration file) be created
after installation by

```bash
pip install .[tests]  # if not already done
cd ./docs
python ./build_docs.py
```

Officially updated built end-user documentation (i.e. information to the
person setting up the configuration file) is
[hosted here on github](https://equinor.github.io/webviz-config/).

# Contributing to Webviz

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
from dash import html

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
a set of toolbar buttons in a settings drawer. The default buttons to appear are
fullscreen and screenshot. Additional buttons appears based on provided
information - as plugin author contact information, download data, guided tour
information and issue feedback link. See [this section](#data-download-callback)
for more information regarding downloading plugin data.

### Callbacks

If you want to include user interactivity which triggers actions in the Python
backend, you can add callbacks. A simple example of this is given below.

```python
from uuid import uuid4

from dash import html, Input, Output
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
callback is set. A typical compressed data download callback will look like

```python
@app.callback(self.plugin_data_output,
              self.plugin_data_requested)
def _user_download_data(data_requested):
    return (
        WebvizPluginABC.plugin_compressed_data(
            filename="webviz-data.zip",
            content=[{"filename": "some_file.txt", "content": "Some download data"}],
        )
        if data_requested
        else None
    )
```

A typical CSV data download from e.g. a `pandas.DataFrame` will look like:
```python
@app.callback(self.plugin_data_output,
              self.plugin_data_requested)
def _user_download_data(data_requested):
    return (
        {
            "filename": "some-file.csv",
            "content": base64.b64encode(
                some_pandas_dataframe.to_csv().encode()
            ).decode("ascii"),
            "mime_type": "text/csv",
        }
        if data_requested
        else None
    )
```

By letting the plugin define the callback, the plugin author is able
to utilize the whole callback machinery, including e.g. state of the individual
components in the plugin. This way the data downloaded can e.g. depend on
the visual state or user selection.

The attributes `self.plugin_data_output` and `self.plugin_data_requested`
are Dash `Output` and `Input` instances respectively, and are provided by
the base class `WebvizPluginABC` (i.e. include them as shown here).

The function `WebvizPluginABC.plugin_compressed_data` is a utility function
which takes a file name and a list of dictionaries, containing file names and corresponding data,
and compresses them to a zip archive which is then downloaded by the user.

### User provided arguments

Since the plugins are reusable and generic, they usually take in some
user provided arguments. A minimal example could look like:

```python
from dash import html
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
By decorating the costly functions with `@CACHE.memoize()`
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
   returns a list of tuples. The first item in each tuple is a reference
   to a function, the second item is a list of argument combinations
   (formatted as dictionaries with `'argument_name': value` pairs).
   Arguments with a default value in the function signature does not need to
   be provided in the argument dictionaries.

   The author of the plugin should provide a list of all the argument
   combinations that are imaginable during runtime of the application.
   Since it is a class method, the author has access to all the user provided
   arguments.

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


@CACHE.memoize()
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
      in a folder `./resources/webviz_storage` as parquet files.
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

Stating the input arguments named `config_folder` and/or `portable` in the function
signature is not necessary, however if you do you will get a
[`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path)
instance representing the absolute path to the configuration file that was used, and/or
a boolean value stating if the Webviz application running is a portable one.

The (optionally transformed) `shared_settings` can be retrieved in a plugin by adding
a specially named `webviz_settings` argument to the plugin's `__init__` function. The
`webviz_settings` argument works similar to the `app` argument in that it is a special
argument name that will not be originating from the configuration file, but will be
automatically given to the plugin by the core functionality of webviz-config.

Shared settings can then be accessed through `webviz_settings`. E.g., in the case
above, the wanted settings are found as `webviz_settings.shared_settings["some_key"]`
as shown in the example below:

```python
from webviz_config import WebvizPluginABC, WebvizSettings

class ExamplePlugin(WebvizPluginABC):

    def __init__(self, app, webviz_settings: WebvizSettings, title: str, number: int=42):

        super().__init__()

        self.title = title
        self.number = number
        self.some_key = webviz_settings.shared_settings["some_key"]

        self.set_callbacks(app)
```

### OAuth 2.0 Authorization Code flow

It is possible to use OAuth 2.0 Authorization Code flow to secure a `webviz` application.
In order to do so, add `oauth2` attribute in a custom plugin with a boolean `True` value.
The following is an example.

```python
class OurCustomPlugin(WebvizPluginABC):

    def __init__(self):
        super().__init__()
        self.use_oauth2 = True

    @property
    def oauth2(self):
        return self.use_oauth2
```

Information related to the application for OAuth 2.0 has to be provided in environment
variables. These environment variables are `WEBVIZ_TENANT_ID`, `WEBVIZ_CLIENT_ID`,
`WEBVIZ_CLIENT_SECRET`, `WEBVIZ_SCOPE`.

The values can be found in the Azure AD configuration page. Short explanation of these environment variables:

- `WEBVIZ_TENANT_ID`: The organization's Azure tenant ID (Equinor has exactly one tenant ID).
- `WEBVIZ_CLIENT_ID`: ID of the Webviz Azure AD app.
- `WEBVIZ_CLIENT_SECRET`: Webviz Azure AD app's client secret.
- `WEBVIZ_SCOPE`: The API permission for this Webviz Azure AD app.

If you are serving behind a proxy, you might need to configure trust for X-FORWARD headers.
Internally, this is done by using a ProxyFix class, as described in the Flask [docs](https://flask.palletsprojects.com/en/2.0.x/deploying/wsgi-standalone/#proxy-setups). To enable the use of the ProxyFix class, set one or all of the following variables to an integer describing the number of trusted forwards:

- `WEBVIZ_X_FORWARDED_FOR`: Corresponds to x_for of the ProxyFix class
- `WEBVIZ_X_FORWARDED_PROTO`: Corresponds to x_proto of the ProxyFix class
- `WEBVIZ_X_FORWARDED_HOST`: Corresponds to x_host of the ProxyFix class
- `WEBVIZ_X_FORWARDED_PORT`: Corresponds to x_port of the ProxyFix class
- `WEBVIZ_X_FORWARDED_PREFIX`: Corresponds to x_prefix of the ProxyFix class

Any omitted argument will be set to 0.

Webviz will store the users oauth and refresh tokens in the flask session. To ensure that this session is treated consistently across server replicas, you should set the environment variable `WEBVIZ_SESSION_SECRET_KEY` to the same value in all replicas.

To get the access token of the authenticated user in the flask session, use `flask.session.get("access_token")`.

To get the expiration date of the token, use `flask.session.get("expiration_date")`.

## Run tests

To run tests it is necessary to first install the [selenium chrome driver](https://github.com/SeleniumHQ/selenium/wiki/ChromeDriver).
Then install the Python development requirements:
```bash
pip install .[tests]
```

You can then run the tests using
```bash
pytest tests --forked
```

Linting can be checked by:
```bash
black --check webviz_config tests
```

## Build documentation

`webviz-config` can automatically build documentation for all installed plugins. E.g.
the end user can get an overview of all installed plugins, and their arguments, by
running
```bash
webviz docs
```
in the terminal. Behind the scenes, `webviz-config` will then create a
[`docsify`](https://github.com/docsifyjs/docsify) setup and open it `localhost`.

The setup can also be deployed to e.g. GitHub Pages directly. To store the documentation
output run
```bash
webviz docs --portable ./built_docs --skip-open
```
The `--skip-open` argument is useful in a CI/CD setting, to prevent `webviz-config`
from automatically trying to open the created documentation in the browser.

### Improve plugin documentation

Auto-built `webviz` documentation will:
- Find all installed plugins.
- Group them according to top package name.
- Show a `YAML` snippet with the plugin argument options.
  - Arguments with default values will be presented with the default value, and be marked as optional.
  - If an argument has a type annotation, that will be included in the documentation.

In addition, if the plugin class has a docstring, the content in the docstring will
be used as a short introduction to the plugin. If the docstring has several parts,
when split by a line containing only `---`, they will be used as follows:
1. First part is the introduction to the plugin.
2. Second part is a more detailed explanation of the plugin arguments.
3. Third part is information regarding plugin data input. E.g assumptions,
prerequisites and/or required/assumed data format.

Since `docsify` is used behind the scenes, you can create information boxes, warning boxes
and use GitHub emojis :bowtie: in the plugin docstring.
See [`docsify` documentation](https://docsify.js.org/#/) for details.

[KaTeX](https://katex.org/) is also used behind the scenes, meaning that you can add
math (TeX syntax) to your docstrings and get it rendered in the auto-built
documentation. Remember that `\` is an escape character in Python, i.e. either
escape it (`\\`) or use raw strings:
```python
class HistoryMatch(WebvizPluginABC):
    r"""This is a docstring with some inline math $\alpha$ and some block math:

$$\alpha = \frac{\beta}{\gamma}$$
"""
```

Example of auto-built documentation for `webviz-config` can be seen
[here on github](https://equinor.github.io/webviz-config/).

## Make your plugin project available

It is strongly recommended to store your plugin project code base in a `git` solution,
e.g. [in a new GitHub repository](https://github.com/new). If possible, it is also
_highly_ recommended to let it be an open source repository. This has several advantages:
 - Others can reuse your work - and help each other achieve better code quality, add more features and share maintenance
 - You will from the beginning make sure you keep a good separation between visualization code and data loading/processing code.
 - It becomes easier for your plugin users to use it in e.g. Docker and in cloud hosting.

`webviz-config` will make sure that portable builds, which uses one (or more) plugins
from your plugin project, includes installation instructions for the project also in
the Docker build instructions. In order for `webviz-config` to do this, you should add
[`project_urls` metadata](https://packaging.python.org/guides/distributing-packages-using-setuptools/#project-urls)
in the project's `setup.py`. An example:
```
    project_urls={
        "Download": "https://pypi.org/project/webviz-config",
        "Source": "https://github.com/equinor/webviz-config",
    },
```
The following logic applies when the user creates a portable application:
- If `Download` is specified *and* the plugin project version installed is available
  on PyPI, the Dockerfile will `pip install` the same version from PyPI.
- Otherwise the Dockerfile will install from the `Source` url. From the `setuptools_scm`
  provided version, the correct commit/version/tag will be installed.

Note that if you are a developer and working on a fork, you might want to temporarily
override the `Source` url to your fork. You can do this by specifying an environment
variable `SOURCE_URL_NAME_PLUGIN_PROJECT=https://urlyourfork`. If you also want to
explicitly state git pointer/reference (thereby not use the one derived from
`setuptools_scm` version) you can set the environment variable
`GIT_POINTER_NAME_PLUGIN_PROJECT`.

For private repositories, a GitHub SSH deploy key will need to be provided to the Docker
build process (see instructions in `README` created with the portable application).

## Deprecate plugins or arguments

Plugins can be marked as deprecated by using the `@deprecated_plugin(deprecation_info)` decorator.

```python
from webviz_config.deprecation_decorators import deprecated_plugin


@deprecated_plugin("An optional explanation of why the plugin has been deprecated.")
class MyPlugin(WebvizPluginABC):
    ...
```

Plugin arguments can be marked as deprecated by using the `@deprecated_plugin_arguments(check={})` decorator in front of the `__init__` function.
Arguments can either be marked as deprecated in any case (see `MyPluginExample1`) or their values can be checked within a function (see `MyPluginExample2`) which returns a tuple containing a short string shown to the end user in the app and a long string shown in the plugin's documentation.

```python
from typing import Optional, Tuple
from webviz_config.deprecation_decorators import deprecated_plugin_arguments


class MyPluginExample1(WebvizPluginABC):
    ...
    @deprecated_plugin_arguments(
        {
            "arg3": (
                "Short message shown to the end user both in the app and documentation.",
                (
                    "This can be a long message, which is shown only in the documentation, explaining "
                    "e.g. why it is deprecated and which plugin should be used instead."
                )
            )
        }
    )
    def __init__(self, arg1: str, arg2: int, arg3: Optional[int] = None):
        ...

def check_deprecation_example2(arg1: int, arg3: int) -> Optional[Tuple[str, str]]:
    if arg3 == arg1:
        return ("This message is shown to the end user in the app.", "This message is shown in the documentation of the plugin.")
    return None

class MyPluginExample2(WebvizPluginABC):
    ...
    @deprecated_plugin_arguments(check_deprecation_example2)
    def __init__(self, arg1: int, arg2: int, arg3: int):
        ...
```

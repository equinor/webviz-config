# Contributing to Webviz configuration utility


## Creating a new composite object

Most of the development work is towards creating standard containers.
An container usually does three things:

* It has a `layout` property, consisting of multiple [Dash components](https://dash.plot.ly/getting-started).
* It has/uses functionality for getting/processing the data it displays/visualizes.
* It sets some [callbacks](https://dash.plot.ly/getting-started-part-2) to add user interactivity triggering
  actions in the Python backend.


### Minimal container

Of the three things mentioned above, it is only the `layout` proprety that is
mandatory to provide. A minimal container could look like:

```python
import dash_html_components as html


class ExampleContainer:

    def __init__(self):
        pass

    @property
    def layout(self):
        return html.Div([
                         html.H1('This is a static title'),
                         'And this is just some ordinary text'
                        ])
```

If the file containing `ExampleContainer` is saved to [./webviz_config/containers](./webviz_config/containers),
and then added to the corresponding [\_\_init\_\_ file](./webviz_config/containers/__init__.py)
you are done. Alternatively you can create you containers in a separate project and `setup.py`.
You can then configure the installation by using something like:
```python
setup(
    ...
    entry_points={
        'webviz_config_containers': [
            'ExampleContainer = my_package.my_module:ExampleContainer'
        ]
    },
    ...
)
```
See [webviz-subsurface](https://github.com/equinor/webviz-subsurface) for example of this usage.

After installation, the user can then include the container through a configuration file, e.g.

```yaml
title: Simple Webviz example

pages:

 - title: Front page
   content: 
    - container: ExampleContainer
```


### Callbacks

If you want to include user interactivity which triggers actions in the Python
backend, you can add callbacks. A simple example of this is given below.

```python
from uuid import uuid4
import dash_html_components as html
from dash.dependencies import Input, Output


class ExampleContainer:

    def __init__(self, app):
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
        def update_output(n_clicks):
            return f'Button has been pressed {n_clicks} times.'
```

Callback functions are decorated with `@app.callback`. For introduction to
callbacks, see [the dash documentation](https://dash.plot.ly/getting-started-part-2).

There are three fundamental additions to the minimal example without callbacks:

* You add the argument `app` to your `__init__` function. This is a special
  argument name which will *not* be originating from the user configuration file,
  but rather automatically given to the container by the core functionality
  of `webviz-config`.
* You add a class function `set_callbacks` which contains the different
  callbacks to add. This function is called from the `__init__` function, such
  that the callbacks are set when the container instance is created.
* Since the components are reusable (i.e. a user can use the container multiple
  times within the same application), the container IDs mentioned in the
  `@app.callback(...)` decorator needs to be unique. One simple way of ensuring
  this is to create unique IDs in the `__init__` function using
  [uuid.uuid4()](https://docs.python.org/3/library/uuid.html#uuid.uuid4),
  as demonstrated in the example above.


### User provided arguments

Since the containers are reusable and generic, they usually take in some
user provided arguments. A minimal example could look like:

```python
import dash_html_components as html


class ExampleContainer:

    def __init__(self, title: str, number: int=42):
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
    - container: ExampleContainer
      title: My special title
```

The core functionality of `webviz-config` will provide user friendly
error messages in the following scenarios:

* A required argument is not provided (in example above, that would be if
  `title` is not stated in the configuration file).
* An unknown argument is given (that would be something else than `title` and
  `number` in this case).
* Mismatch between type of user provided value, and the (optionally) provided
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
    - container: ExampleContainer
      title: My special title
      number: Some text instead of number
```

this error message will be given:
```
The value provided for argument `number` given to container `ExampleContainer` is of type `str`. Expected type `int`
```

An additional benefit is that if the container author says an argument should
be of type `pathlib.Path`, the configuration parser will make sure that
the user provided path (which is a string to begin with in configuration file,
potentially non-absolute and relative to the configuration file itself) is
given to the container as an absolute path, and of type `pathlib.Path`.


### Data input

The containers get data input through ordinary Python functions, usually
defined outside of the container class. Since these functions can be costly to
call, we utilize the [flask-caching](https://pythonhosted.org/Flask-Caching/)
package. By decorating the costly functions with `@cache.memoize(timeout=cache.TIMEOUT)`
the result is cached, such that if the same function is called more than once,
within the timeout, the cached result will be used instead of starting
a new calculation.

Functionality used by multiple containers should be put in a common module.
In order to not have many `cache` instances in memory, it is suggested to
import the common cache instance,
```
from webviz_config.common_cache import cache
```


### Deattaching data from its original source

There are use cases where the generated webviz instance ideally is portable
and self-contained. At the same time, there are use cases where the data input
ideally comes from "live sources" (simulations still running, production database...).

Asking each container to take care of both these scenarios to the full extent
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
the container author needs only do three things:

1) Import the decorator: `from ..webviz_store import webvizstore`
2) Decorate the function as this:
   ```python
   @webvizstore
   def get_some_data(some, arguments) -> pd.DataFrame:
   ```
3) In the container class, define a class method `add_webvizstore` which
   returns a list of tuples. The first container in each tuple is a reference
   to a function, the second container is itself a list of argument combinations.

   The author of the container should provide a list of all the argument
   combinations that are imaginable during runtime of the application.
   Since it is a class method, the author has access to all the user provided
   arguments.

   Arguments with a default value in the function signature does not need to
   be provided in the argument dictionaries.

A full example could look like e.g.:

```python
import pandas as pd
from ..webviz_store import webvizstore
from ..common_cache import cache


class ExamplePortable:

    def __init__(self, some_number: int):
        self.some_number = some_number

    def add_webvizstore(self):
        return [(input_data_function, [{'some_number': self.some_number}])]

    @property
    def layout(self):
        return str(input_data_function(self.some_number))


@cache.memoize(timeout=cache.TIMEOUT)
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

Currently only functions returning `pd.DataFrame` and `pathlib.Path` are
supported. A `NotImplementedError` will be raised if the function being
decorated with `@webvizstore` does not have a type hint being supported.

If the return type is `pathlib.Path`, the file corresponding to the path will
be copied over to the portable `webviz` instance, and the decorated function
will return a `pathlib.Path` instance pointing to the stored file. For most
use cases, the decorated function `get_resource` in
`webviz_config.webviz_store` can be imported and used.


**Note:** The argument hashing method used for `@webvizstore` is using
the same principles as in `@cache.memoize` from the `flask-caching` package.
The input arguments to a function decorated with `@webvizstore` could be
mutable objects like e.g. instances of a class, but make sure that the object
has a `__repr__` function associated with it such that instances representing
different input also have different string output from `__repr__`.

**Note:** If you nest decorations, e.g. use both `@webvizstore` and
`@cache.memoize`, follow the same order as in the example above.


### Custom ad-hoc containers

It is possible to create custom containers which still can be included through
the configuration file. As an example, assume someone on your project has made

```python
import dash_html_components as html


class OurCustomContainer:

    def __init__(self, title: str):
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
`ourmodule`, the user can include the custom container the same way as a standard
container, with the only change of also naming the module:
```yaml
title: Simple Webviz example

pages:

 - title: Front page
   content: 
    - container: ourmodule.OurCustomContainer
      title: Title of my custom container
```

Note that this might involve appending your `$PYTHONPATH` environment
variable with the path where your custom module is located. The same principle
applies if the custom container is saved in a package with submodule(s),
```yaml
    - container: ourpackage.ourmodule.OurCustomContainer
```

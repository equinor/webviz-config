'''Builds automatic documentation of the installed webviz config containers.
The documentation is designed to be used by the YAML configuration file end
user. Sphinx has not been used due to

 1) Sphinx is geared towards Python end users, and templateing of apidoc output
    is not yet supported (https://github.com/sphinx-doc/sphinx/issues/3545).

 2) It is a small problem to be solved, and most of the Sphinx machinery
    is not needed.

Overall workflow is:
    * Gets all installed containers.
    * Automatically reads docstring and __init__ function signature (both
      argument names and which arguments have default values).
    * Output the extracted container information in html using jinja2.
'''

import shutil
import inspect
import pathlib
from importlib import import_module
from collections import defaultdict
import jinja2
from markdown import markdown
import webviz_config.containers

SPECIAL_ARGS = ['self', 'app', 'container_settings']

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
BUILD_DIR = SCRIPT_DIR / '_build'
TEMPLATE_FILE = SCRIPT_DIR / 'templates' / 'index.html.jinja2'
EXAMPLE = SCRIPT_DIR / '..' / 'tests' / 'basic_example.yaml'


def escape_all(input_string):
    '''Escapes any html or utf8 character in the given string.
    '''

    no_html = jinja2.escape(input_string)
    no_utf8 = no_html.encode('ascii', 'xmlcharrefreplace').decode()
    pass_through = jinja2.Markup(no_utf8)
    return pass_through


def convert_docstring(doc):
    '''Convert docstring to markdown.
    '''

    return '' if doc is None else markdown(doc, extensions=['fenced_code'])


def get_container_documentation():
    '''Get all installed containers, and document them by grabbing docstring
    and input arguments / function signature.
    '''

    containers = inspect.getmembers(webviz_config.containers, inspect.isclass)

    container_doc = []

    for container in containers:
        reference = container[1]

        container_info = {}

        container_info['name'] = container[0]
        container_info['doc'] = convert_docstring(reference.__doc__)

        argspec = inspect.getfullargspec(reference.__init__)
        container_info['args'] = [arg for arg in argspec.args
                                  if arg not in SPECIAL_ARGS]

        container_info['values'] = defaultdict(lambda: 'some value')

        if argspec.defaults is not None:
            for arg, default in dict(zip(reversed(argspec.args),
                                     reversed(argspec.defaults))).items():
                container_info['values'][arg] = \
                     f'{default}  # Optional (default value shown here).'

        module = inspect.getmodule(reference)
        container_info['module'] = module.__name__

        package = inspect.getmodule(module).__package__
        container_info['package'] = package
        container_info['package_doc'] = convert_docstring(
                                            import_module(package).__doc__
                                                         )

        if not container_info['name'].startswith('Example'):
            container_doc.append(container_info)

    # Sort the containers by package:

    package_ordered = defaultdict(lambda: {'containers': []})

    for container in sorted(container_doc, key=lambda x: (x['module'],
                                                          x['name'])):
        package = container['package']
        package_ordered[package]['containers'].append(container)
        package_ordered[package]['doc'] = container['package_doc']

    return package_ordered


def get_basic_example():
    with open(EXAMPLE) as fh:
        return escape_all(fh.read())


if __name__ == '__main__':

    template_data = {'packages': get_container_documentation(),
                     'basic_example': get_basic_example()}

    with open(TEMPLATE_FILE) as fh:
        template = jinja2.Template(fh.read())

    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    shutil.copytree(SCRIPT_DIR / '_static', BUILD_DIR / '_static')

    with open(BUILD_DIR / 'index.html', 'w') as fh:
        fh.write(template.render(template_data))

    print(f'Output available in {BUILD_DIR}')

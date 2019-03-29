import re
import sys
import pathlib
import inspect
import importlib
import yaml
from . import containers as standard_containers

SPECIAL_ARGS = ['self', 'app', 'container_settings',
                '_call_signature', '_imports']


def get_class_members(module):
    '''Returns a list of all class names defined
    in the module given as input.
    '''
    return [member[0] for member in
            inspect.getmembers(module, inspect.isclass)]


def call_signature(module, module_name, container_name,
                   container_settings, kwargs, config_folder):
    '''Takes as input the name of a container, the module it is located in,
    together with user given arguments (originating from the configuration
    file). Returns the equivalent Python code wrt. initiating an instance of
    that container (with the given arguments).

    Raises ParserError in the following scenarios:
      * User is missing a required (i.e. no default value) __init__ argument
      * User provided an argument not existing in the class' __init__ function
      * User has given one of the protected arguments in SPECIAL_ARGS
      * If there is type mismatch between user given argument value, and type
        hint in __init__ signature (given that type hint exist)
    '''
    argspec = inspect.getfullargspec(getattr(module,
                                             container_name).__init__)

    if argspec.defaults is not None:
        required_args = argspec.args[:-len(argspec.defaults)]
    else:
        required_args = argspec.args

    for arg in required_args:
        if arg not in SPECIAL_ARGS and arg not in kwargs:
            raise ParserError('\033[91m'
                              f'The container `{container_name}` requires '
                              f'the argument `{arg}` in your configuration '
                              'file.'
                              '\033[0m')

    for arg in kwargs:
        if arg in SPECIAL_ARGS:
            raise ParserError('\033[91m'
                              f'Container argument `{arg}` not allowed.'
                              '\033[0m')

        if arg not in argspec.args:
            raise ParserError('\033[91m'
                              'Unrecognized argument. The container '
                              f'`{container_name}` does not take an '
                              f'argument `{arg}`.'
                              '\033[0m')

        if arg in argspec.annotations:
            expected_type = argspec.annotations[arg]

            if expected_type == pathlib.Path:
                kwargs[arg] = (config_folder / pathlib.Path(kwargs[arg]))\
                              .resolve()

            if not isinstance(kwargs[arg], expected_type):
                raise ParserError('\033[91m'
                                  f'The value provided for argument `{arg}` '
                                  f'given to container `{container_name}` is '
                                  f'of type `{type(kwargs[arg]).__name__}`. '
                                  f'Expected type '
                                  f'`{argspec.annotations[arg].__name__}`.'
                                  '\033[0m')

    special_args = ''
    if 'app' in argspec.args:
        special_args += 'app=app, '

    if 'container_settings' in argspec.args:
        kwargs['container_settings'] = container_settings

    return f'{module_name}.{container_name}({special_args}**{kwargs})'


class ParserError(Exception):
    pass


class ConfigParser:

    STANDARD_CONTAINERS = get_class_members(standard_containers)

    def __init__(self, yaml_file):
        try:
            self._configuration = yaml.safe_load(open(yaml_file, 'r'))
        except yaml.YAMLError as e:
            extra_info = ('There is something wrong in the configuration '
                          f'file {yaml_file}. ')

            if hasattr(e, 'problem_mark'):
                extra_info += ('The typo is probably somewhere around '
                               f'line {e.problem_mark.line + 1}.')

            raise type(e)(f'{e}. \033[91m{extra_info}\033[0m')\
                .with_traceback(sys.exc_info()[2])

        self._config_folder = pathlib.Path(yaml_file).parent
        self._page_ids = []
        self.clean_configuration()

    def _generate_page_id(self, title):
        '''From the user given title, this function provides a unique
        human readable page id, not already present in self._page_ids
        '''

        base_id = re.sub('[^-a-z0-9_]+', '',
                         title.lower().replace(' ', '_'))

        page_id = base_id

        count = 1
        while page_id in self._page_ids:
            count += 1
            page_id = f'{base_id}{count}'

        return page_id

    def clean_configuration(self):
        '''Various cleaning and checks of the raw configuration read
        from the user provided yaml configuration file.
        '''

        self.configuration['_imports'] = set()

        if 'container_settings' not in self.configuration:
            container_settings = {}
        else:
            container_settings = self.configuration['container_settings']

        for mandatory_key in ['password', 'username']:
            if mandatory_key not in self.configuration:
                raise ParserError(('\033[91m'
                                   'The configuration file does not '
                                   f'have {mandatory_key} set.'
                                   '\033[0m'))

        if 'title' not in self.configuration:
            self.configuration['title'] = 'Webviz - Powered by Dash'

        if 'pages' not in self.configuration:
            raise ParserError('\033[91m'
                              'The configuration file does not have '
                              'information regarding which pages to create.'
                              '\033[0m')
        elif not isinstance(self.configuration['pages'], list):
            raise ParserError('\033[91m'
                              'The configuration input belonging to the '
                              '`pages` keyword should be a list.'
                              '\033[0m')

        for page_number, page in enumerate(self.configuration['pages']):

            if 'title' not in page:
                raise ParserError('\033[91m'
                                  f'Page number {page_number + 1} does '
                                  'not have the title specified.'
                                  '\033[0m')

            if 'id' not in page:
                page['id'] = self._generate_page_id(page['title'])
            elif page['id'] in self._page_ids:
                raise ParserError('\033[91m'
                                  'You have more than one page '
                                  'with the same `id`.'
                                  '\033[0m')

            self._page_ids.append(page['id'])

            if 'content' not in page:
                page['content'] = []
            elif not isinstance(page['content'], list):
                raise ParserError('\033[91m'
                                  'The content of page number '
                                  f'{page_number + 1} should be a list.'
                                  '\033[0m')

            containers = [e for e in page['content'] if isinstance(e, dict)]

            for container in containers:
                if 'container' not in container:
                    raise ParserError('\033[91m'
                                      'Argument `container`, stating name of '
                                      'the container to include, is required.'
                                      '\033[0m')

                kwargs = {**container}
                container_name = kwargs.pop('container')

                if '.' not in container_name:
                    if container_name not in ConfigParser.STANDARD_CONTAINERS:
                        raise ParserError(
                                      '\033[91m'
                                      'You have included an container with '
                                      f'name `{container_name}` in your '
                                      'configuration file. This is not a '
                                      'standard container.'
                                      '\033[0m')
                    else:
                        self.configuration['_imports']\
                         .add(('webviz_config.containers',
                               'standard_containers'))

                        container['_call_signature'] = call_signature(
                                                        standard_containers,
                                                        'standard_containers',
                                                        container_name,
                                                        container_settings,
                                                        kwargs,
                                                        self._config_folder
                                                                     )
                else:
                    parts = container_name.split('.')

                    container_name = parts[-1]
                    module_name = ".".join(parts[:-1])
                    module = importlib.import_module(module_name)

                    if container_name not in get_class_members(module):
                        raise ParserError('\033[91m'
                                          f'Module `{module}` does not have a '
                                          f'container named `{container_name}`'
                                          '\033[0m')
                    else:
                        self.configuration['_imports'].add(module_name)
                        container['_call_signature'] = call_signature(
                                                            module,
                                                            module_name,
                                                            container_name,
                                                            container_settings,
                                                            kwargs,
                                                            self._config_folder
                                                                     )

    @property
    def configuration(self):
        return self._configuration

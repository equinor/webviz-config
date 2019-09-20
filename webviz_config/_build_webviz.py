import os
import time
import shutil
import tempfile
import subprocess
from yaml import YAMLError
from ._webviz_ott import LocalhostLogin
from ._config_parser import ParserError
from ._write_script import write_script
from .themes import installed_themes


BUILD_FILENAME = 'webviz_app.py'
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')


def build_webviz(args):

    if args.theme not in installed_themes:
        raise ValueError(f'Theme `{args.theme}` is not installed.')

    if args.portable is None:
        build_directory = tempfile.mkdtemp()
    else:
        build_directory = args.portable
        os.makedirs(build_directory)

    shutil.copytree(os.path.join(STATIC_FOLDER, 'assets'),
                    os.path.join(build_directory, 'assets'))

    for filename in ['README.md', 'Dockerfile', '.dockerignore']:
        shutil.copy(os.path.join(STATIC_FOLDER, filename), build_directory)

    for asset in installed_themes[args.theme].assets:
        shutil.copy(asset, os.path.join(build_directory, 'assets'))

    try:
        if args.portable:
            print('\033[1m\033[94m'
                  'Extracting, processing and saving requested data to build '
                  'folder such that the webviz instance is portable.'
                  '\033[0m')

            write_script(args, build_directory,
                         'copy_data_template.py.jinja2', 'copy_data.py')

            if subprocess.call(['python3', 'copy_data.py'],
                               cwd=build_directory):
                raise RuntimeError('Something went wrong. This is probably '
                                   'not related to webviz-config, but more '
                                   'likely in one of the  dependencies used '
                                   'by one or more containers. See exact '
                                   'error message and traceback above')

            os.remove(os.path.join(build_directory, 'copy_data.py'))

            print('\033[1m\033[94m'
                  'Finished data extraction. All output saved.'
                  '\033[0m')

        ott = None if args.portable else LocalhostLogin.generate_token()
        cookie_token = None if args.portable \
            else LocalhostLogin.generate_token()

        non_default_assets = write_script(args,
                                          build_directory,
                                          'webviz_template.py.jinja2',
                                          BUILD_FILENAME,
                                          ott,
                                          cookie_token,
                                          open_browser=True)

        for asset in non_default_assets:
            shutil.copy(asset, os.path.join(build_directory, 'assets'))

        if not args.portable:
            run_webviz(args, build_directory, ott, cookie_token)

    finally:
        if not args.portable:
            print(f'Deleting temporary folder {build_directory}')
            shutil.rmtree(build_directory)


def run_webviz(args, build_directory, ott, cookie_token):

    print(' \n\033[92m'
          ' Starting up your webviz application. Please wait...'
          ' \033[0m\n')

    app_process = subprocess.Popen(['python3', BUILD_FILENAME],
                                   cwd=build_directory)

    lastmtime = os.path.getmtime(args.yaml_file)

    while app_process.poll() is None:
        time.sleep(1)

        try:
            if lastmtime != os.path.getmtime(args.yaml_file):
                lastmtime = os.path.getmtime(args.yaml_file)
                write_script(args,
                             build_directory,
                             'webviz_template.py.jinja2',
                             BUILD_FILENAME,
                             ott,
                             cookie_token)
                print('\033[1m\033[94m'
                      'Rebuilt webviz dash app from configuration file'
                      '\033[0m')

        except (ParserError, YAMLError) as e:
            print(f'{e} \033[91m Fix the error and save the '
                  'configuration file in order to trigger a new '
                  'rebuild. \033[0m')

        except Exception as e:
            app_process.kill()
            print('\033[91m'
                  'Unexpected error. Killing the webviz dash '
                  'application process.'
                  '\033[0m')
            raise e

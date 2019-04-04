from setuptools import setup, find_packages

setup(
    name='webviz-config',
    version='0.0.1',
    description='Configuration file support for webviz',
    url='https://github.com/Statoil/webviz-config',
    author='R&T Equinor',
    packages=find_packages(exclude=['tests']),
    package_data={
        'webviz_config': [
            'templates/*',
            'static/*',
            'static/.dockerignore',
            'static/assets/*'
        ]},
    entry_points={
        'console_scripts': [
           'webviz=webviz_config.command_line:main'
         ],
    },
    zip_safe=False
)

from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

tests_requires = [
    'chromedriver-binary>=74.0.3729.6.0',
    'pylint~=2.3',
    'pycodestyle~=2.5',
    'selenium~=3.141',
    'mock',
    'pytest-xdist'
]

setup(
    name='webviz-config',
    description='Configuration file support for webviz',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/equinor/webviz-config',
    author='R&T Equinor',
    packages=find_packages(exclude=['tests']),
    package_data={
        'webviz_config': [
            'templates/*',
            'static/*',
            'static/.dockerignore',
            'static/assets/*',
            'themes/default_assets/*'
        ]},
    entry_points={
        'console_scripts': [
           'webviz=webviz_config.command_line:main'
         ],
    },
    install_requires=[
        'dash~=1.1',
        'bleach~=3.1',
        'cryptography~=2.4',
        'dash-auth~=1.3',
        'requests',  # While waiting for dep. fix in dash-auth >= 1.4 on pypi
        'flask-caching~=1.4',
        'flask-talisman~=0.6',
        'jinja2~=2.10',
        'markdown~=3.0',
        'pandas~=0.24',
        'pyarrow~=0.11',
        'pyyaml~=5.1',
        'webviz-core-components>=0.0.8'
    ],
    tests_require=tests_requires,
    extras_require={'tests': tests_requires},
    setup_requires=['setuptools_scm~=3.2'],
    use_scm_version=True,
    zip_safe=False,
    classifiers=[
     'Programming Language :: Python :: 3',
     'Operating System :: OS Independent',
     'Natural Language :: English',
     'Topic :: Multimedia :: Graphics',
     'Topic :: Scientific/Engineering',
     'Topic :: Scientific/Engineering :: Visualization',
     'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)'
    ]
)

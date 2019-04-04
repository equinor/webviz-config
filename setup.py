from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

tests_requires = [
    'chromedriver-binary>=74.0.3729.6.0',
    'dash>=0.38.0',
    'markdown>=3.0.1',
    'pylint>=2.3.1',
    'pytest-dash>=2.1.1',
    'pycodestyle>=2.5.0',
    'selenium>=3.141.0'
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
            'static/assets/*'
        ]},
    entry_points={
        'console_scripts': [
           'webviz=webviz_config.command_line:main'
         ],
    },
    install_requires=[
        'cryptography>=2.5',
        'dash>=0.35.2',
        'dash-auth>=1.3.1',
        'dash-core-components>=0.42.1',
        'dash-html-components>=0.13.4',
        'dash-table>=3.4.0',
        'flask-caching>=1.4.0',
        'flask-talisman>=0.6.0',
        'jinja2>=2.10',
        'pandas==0.24.1',
        'pyarrow>=0.11.1',
        'pyyaml>=3.13',
        'webviz_components>=0.0.1'
    ],
    tests_require=tests_requires,
    extras_require={'tests': tests_requires},
    setup_requires=['setuptools_scm>=3.2.0'],
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

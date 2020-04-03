from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

TESTS_REQUIRES = [
    "pylint~=2.3",
    "selenium~=3.141",
    "mock",
    "pytest-xdist",
    "black",
    "bandit",
    "mypy",
]

setup(
    name="webviz-config",
    description="Configuration file support for webviz",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/equinor/webviz-config",
    author="R&T Equinor",
    packages=find_packages(exclude=["tests"]),
    package_data={
        "webviz_config": [
            "templates/*",
            "static/*",
            "static/.dockerignore",
            "static/assets/*",
            "themes/default_assets/*",
        ]
    },
    entry_points={"console_scripts": ["webviz=webviz_config.command_line:main"]},
    install_requires=[
        # Pinning dash to the 1.7-series as long as
        # https://github.com/plotly/dash-core-components/issues/746 is open
        "dash==1.7",
        "bleach>=3.1",
        "cryptography>=2.4",
        "flask-caching>=1.4",
        "flask-talisman>=0.6",
        "jinja2>=2.10",
        "markdown>=3.0",
        "pandas>=0.24",
        "pyarrow>=0.16",
        "pyyaml>=5.1",
        "webviz-core-components>=0.0.16",
    ],
    tests_require=TESTS_REQUIRES,
    extras_require={"tests": TESTS_REQUIRES},
    setup_requires=["setuptools_scm~=3.2"],
    use_scm_version=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Framework :: Dash",
        "Framework :: Flask",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
    ],
)

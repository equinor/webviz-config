from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

TESTS_REQUIRES = [
    "bandit",
    "black",
    "jsonschema",
    "mock",
    "mypy",
    "pylint~=2.3",
    "pytest-xdist",
    "selenium~=3.141",
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
            "_docs/static/*",
            "_docs/static/fonts/*",
            "static/*",
            "static/.dockerignore",
            "static/assets/*",
            "templates/*",
            "themes/default_assets/*",
        ]
    },
    entry_points={"console_scripts": ["webviz=webviz_config.command_line:main"]},
    install_requires=[
        "bleach>=3.1",
        "cryptography>=2.4",
        "dash>=1.7",
        "flask-caching>=1.4",
        "flask-talisman>=0.6",
        "jinja2>=2.10",
        "markdown>=3.0",
        "pandas>=0.24",
        "pyarrow>=0.16",
        "pyyaml>=5.1",
        "tqdm>=4.8",
        "typing-extensions>=3.7",  # Needed on Python < 3.8
        "webviz-core-components>=0.0.19",
    ],
    tests_require=TESTS_REQUIRES,
    extras_require={"tests": TESTS_REQUIRES},
    setup_requires=["setuptools_scm~=3.2"],
    python_requires="~=3.6",
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

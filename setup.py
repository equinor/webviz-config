import os
import re
import pathlib

from setuptools import setup, find_packages


def get_long_description() -> str:
    """Converts relative repository links to absolute URLs
    if GITHUB_REPOSITORY and GITHUB_SHA environment variables exist.
    If not, it returns the raw content in README.md.
    """

    raw_readme = pathlib.Path("README.md").read_text()

    repository = os.environ.get("GITHUB_REPOSITORY")
    sha = os.environ.get("GITHUB_SHA")

    if repository is not None and sha is not None:
        full_url = f"https://github.com/{repository}/blob/{sha}/"
        return re.sub(r"]\((?!https)", "](" + full_url, raw_readme)
    return raw_readme


TESTS_REQUIRES = [
    "bandit",
    "black>=20.8b1",
    "dash[testing]",
    "jsonschema",
    "mypy",
    "pylint",
    "pytest-xdist",
    "selenium",
    "types-bleach",
    "types-markdown",
    "types-pyyaml",
    "types-requests",
]

# pylint: disable=line-too-long
setup(
    name="webviz-config",
    description="Configuration file support for webviz",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/equinor/webviz-config",
    author="R&T Equinor",
    packages=find_packages(exclude=["tests"]),
    package_data={
        "webviz_config": [
            "_docs/static/*",
            "_docs/static/fonts/*",
            "py.typed",
            "static/*",
            "static/.dockerignore",
            "static/.gitignore",
            "static/assets/*",
            "templates/*",
            "themes/default_assets/*",
        ]
    },
    entry_points={
        "console_scripts": ["webviz=webviz_config.command_line:main"],
        "webviz_config_plugins": [
            "ExampleAssets = webviz_config.generic_plugins._example_assets:ExampleAssets",
            "ExampleDataDownload = webviz_config.generic_plugins._example_data_download:ExampleDataDownload",
            "ExamplePlugin = webviz_config.generic_plugins._example_plugin:ExamplePlugin",
            "ExamplePortable = webviz_config.generic_plugins._example_portable:ExamplePortable",
            "ExampleTour = webviz_config.generic_plugins._example_tour:ExampleTour",
            "BannerImage = webviz_config.generic_plugins._banner_image:BannerImage",
            "DataTable = webviz_config.generic_plugins._data_table:DataTable",
            "EmbedPdf = webviz_config.generic_plugins._embed_pdf:EmbedPdf",
            "Markdown = webviz_config.generic_plugins._markdown:Markdown",
            "SyntaxHighlighter = webviz_config.generic_plugins._syntax_highlighter:SyntaxHighlighter",
            "TablePlotter = webviz_config.generic_plugins._table_plotter:TablePlotter",
            "PivotTable = webviz_config.generic_plugins._pivot_table:PivotTable",
        ],
    },
    install_requires=[
        "bleach>=3.1",
        "cryptography>=2.4",
        "dash>=2.0",
        "dash-pivottable>=0.0.2",
        "dataclasses>=0.8; python_version<'3.7'",
        "flask-caching>=1.4",
        "flask-talisman>=0.6",
        "importlib-metadata>=1.7; python_version<'3.8'",
        "jinja2>=2.10",
        "markdown>=3.0",
        "msal>=1.5.0",
        "orjson>=3.3",
        "pandas>=1.0",
        "pyarrow>=0.16",
        "pyyaml>=5.1",
        "requests>=2.20",
        "tqdm>=4.8",
        "typing-extensions>=3.7; python_version<'3.8'",
        "webviz-core-components>=0.5.4",
    ],
    extras_require={
        "tests": TESTS_REQUIRES,
        "deployment": [
            "aiohttp",  # https://github.com/Azure/azure-sdk-for-python/issues/19201
            "azure-core",
            "azure-identity",
            "azure-mgmt-resource",
            "azure-mgmt-storage",
            "azure-storage-blob",
        ],
    },
    setup_requires=["setuptools_scm~=3.2"],
    python_requires="~=3.6",
    use_scm_version=True,
    zip_safe=False,
    project_urls={
        "Documentation": "https://equinor.github.io/webviz-config",
        "Download": "https://pypi.org/project/webviz-config",
        "Source": "https://github.com/equinor/webviz-config",
        "Tracker": "https://github.com/equinor/webviz-config/issues",
    },
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

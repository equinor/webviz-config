[![PyPI version](https://badge.fury.io/py/webviz-config.svg)](https://badge.fury.io/py/webviz-config)
[![Build Status](https://travis-ci.org/equinor/webviz-config.svg?branch=master)](https://travis-ci.org/equinor/webviz-config)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/1d7a659ea4784aa396ac1cb101c8e678)](https://www.codacy.com/app/anders-kiaer/webviz-config?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=equinor/webviz-config&amp;utm_campaign=Badge_Grade)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)

## Webviz configuration utility

### Introduction

Writing a Webviz application, built on top of [dash](https://github.com/plotly/dash),
gives a lot of flexibility. However, it also requires Python knowledge from the
person setting it up.

This utility reduces the skills necessary to configure a Webviz application.

*The workflow can be summarized as this:*
1) The user provides a configuration file following the [yaml](https://en.wikipedia.org/wiki/YAML) standard.
2) This utility reads the configuration file and automatically writes the corresponding Webviz Dash code.
3) The created application can either be viewed locally, or deployed to a cloud provider. Both out of the box.

Creating custom, specialized elements is possible. See the [contribution guide](./CONTRIBUTING.md) for
more details.

The [yaml](https://en.wikipedia.org/wiki/YAML) configuration file can either be
manually created, or it could be auto-generated by some other tool.

Example configuration file and information about the standard containers
can be seen in [the documentation](https://equinor.github.io/webviz-config/).

### Installation

As `dash` is using Python3-only functionality, you should use a Python3 (virtual)
environment before installation. One way of doing this is
```bash
PATH_TO_VENV='./my_new_venv'
python3 -m virtualenv $PATH_TO_VENV
source $PATH_TO_VENV/bin/activate
```

The simplest way of installing `webviz-config` is to run
```bash
pip install webviz-config
```

If you want to download the latest source code and install it manually you 
can run
```bash
git clone git@github.com:equinor/webviz-config.git
cd webviz-config
pip install .
```

### Run tests

To run tests it is necessary to first install [selenium chrome driver](https://github.com/SeleniumHQ/selenium/wiki/ChromeDriver).
Then install dev requirements and run pytest:

```bash
pip install .[tests]
pytest tests
```

Linting can be checked by:

```bash
pycodestyle webviz_config tests
```

### Build documentation

End-user documentation (i.e. YAML configuration file) be created
after installation by

```bash
pip install .[tests]
cd ./docs
python3 build_docs.py
```

Officially updated built end-user documentation (i.e. information to the
person setting up the configuration file) is
[hosted here on github](https://equinor.github.io/webviz-config/).


### Usage

After installation, there is a console script named `webviz` available
in `$PATH_TO_VENV/bin`. You can test the installation by using the provided test
configuration file,
```bash
webviz build ./examples/basic_example.yaml
```

Without any additional arguments, this will
1) create a temporary folder
2) write the Webviz Dash application code to that folder
3) start the server
4) when stopping the server (press CTRL+C at any time), the temporary folder is deleted

The optional arguments can be seen when running
```bash
webviz --help
```

For example will
```bash
webviz build ./examples/basic_example.yaml --portable /scratch/my_field/my_webviz
```
create a portable instance and store it in the provided folder.

A recent feature in dash is [hot reload](https://community.plot.ly/t/announcing-hot-reload/14177).
When the Dash Python code file is saved, the content seen in the web browser is
automatically reloaded (no need for server restart). This feature is passed on to
Webviz configuration utility, meaning that if the user runs 
```bash
webviz build ./examples/basic_example.yaml
```
and then modifies `./examples/basic_example.yaml` while the Webviz application is
still running, a hot reload will occur.

By default `webviz-config` uses `https` and runs on `localhost`.
In order to create your personal `https` certificate, run
```bash
webviz certificate
```
Certificate installation guidelines will be given when running the command.

### Creating new containers

If you are interested in creating new containers which can be configured through
the configuration file, take a look at the [contribution guide](./CONTRIBUTING.md).

### Disclaimer

This is a tool under heavy development. The current configuration file layout
will therefore also see large changes.

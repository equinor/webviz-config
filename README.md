<p align="center">
  <img height="150" src="https://github.com/equinor/webviz-config/raw/master/webviz_config/_docs/static/webviz-logo.svg?sanitize=true">
</p>

<h2 align="center">Democratizing Python web applications</h2>

<p align="center">
<a href="https://badge.fury.io/py/webviz-config"><img src="https://badge.fury.io/py/webviz-config.svg"></a>
<a href="https://equinor.github.io/webviz-config"><img src="https://img.shields.io/badge/docs-passing-brightgreen"></a>
<a href="https://github.com/equinor/webviz-config/blob/master/LICENSE"><img src="https://img.shields.io/github/license/equinor/webviz-config.svg?color=dark-green"></a>
<a href="https://github.com/equinor/webviz-config/actions?query=branch%3Amaster"><img src="https://github.com/equinor/webviz-config/workflows/webviz-config/badge.svg"></a>
<a href="https://lgtm.com/projects/g/equinor/webviz-config/alerts/"><img alt="Total alerts" src="https://img.shields.io/lgtm/alerts/g/equinor/webviz-config.svg?logo=lgtm&logoWidth=18"/></a>
<a href="https://lgtm.com/projects/g/equinor/webviz-config/context:python"><img alt="Language grade: Python" src="https://img.shields.io/lgtm/grade/python/g/equinor/webviz-config.svg?logo=lgtm&logoWidth=18"/></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10-blue.svg"></a>
<a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>
<br/>

Writing a [Dash web application](https://github.com/plotly/dash) gives a lot of flexibility, however, it also requires :snake: Python knowledge from the person setting it up.

*Webviz™* is a MIT-licensed configuration layer on top of Dash, which encourages making reusable components and dashboards, which can then be added/removed when creating an application using a short [`yaml`](https://en.wikipedia.org/wiki/YAML) configuration file.

This Python package, `webviz-config`, is the core plugin framework. For a real example repository using this plugin system, see e.g. [`webviz-subsurface`](https://github.com/equinor/webviz-subsurface).
 
**These are the main user groups targeted by *Webviz™*:**
- **You do not know Python**, and only want to add different predefined dashboards or visualizations/components in a certain order and/or on different pages in the application. Optionally with some text and mathematical equations (that you provide) inbetween the  dashboards, explaining what the user is looking at.
- **You know [Python](https://www.python.org/)**, and want to create generic or specialized dashboards you or other users can reuse by simply asking for it in the Webviz™ configuration file. This can be done without knowing JavaScript (see also [Dash](https://plot.ly/dash/) for more information).
- **You know [React](https://reactjs.org/)**, and want to create highly specialized visualization which Python or pure config-file users can reuse.

*Webviz™* will create web applications with very :lock: strict security headers and CSP settings, giving an rating of **A+** on e.g. [Mozilla observatory](https://observatory.mozilla.org/). It also facilitates a :whale: Docker setup, where the Python code can be ran completely unpriviliged in a sandbox (both with respect to file system access and network communication).

Example configuration file and information about the standard plugins can be seen in [the documentation](https://equinor.github.io/webviz-config/).

**The workflow can be summarized as this:**
1) The user provides a :book: configuration file following the [yaml](https://en.wikipedia.org/wiki/YAML) standard.
2) *Webviz™* reads the configuration file and automatically writes the corresponding :snake: Python code.
3) The created application can be viewed locally, or deployed using :whale: Docker to a cloud provider. Both out of the box.

![technical_drawing](https://user-images.githubusercontent.com/31612826/67282250-9f54fc80-f4d1-11e9-9f77-b352ec2710ed.png)

---

### Installation

The recommended and simplest way of installing `webviz-config` is to run
```bash
pip install webviz-config
```

If you want to develop `webviz-config` and install the latest source code manually you
can do something along the lines of:
```bash
git clone git@github.com:equinor/webviz-config.git
cd ./webviz-config
npm ci --ignore-scripts
# NOTE: If you are on Windows, make sure to first set `npm`'s default `script-shell` to `powershell` by running
# npm config set script-shell powershell
npm run postinstall
pip install -e .
```

After installation, there is a console script named `webviz` available. You can test the
installation by using the provided example configuration file,
```bash
webviz build ./examples/basic_example.yaml
```

Without any additional arguments, this will
1) create a temporary folder
2) write the Python application code to that folder
3) start a localhost server

When stopping the server (press CTRL+C at any time), the temporary folder is deleted.

The optional arguments can be seen when running
```bash
webviz --help
```

### Usage

See [the introduction](./INTRODUCTION.md) page for information on how you
create a `webviz` configuration file and use it.

### Creating new plugins

If you are interested in creating new plugins which can be configured through
the configuration file, take a look at the [contribution guide](./CONTRIBUTING.md).

To quickly get started, we recommend using the corresponding
[cookiecutter template](https://github.com/equinor/webviz-plugin-boilerplate).

### License

`webviz-config` is, with a few exceptions listed below, [MIT](./LICENSE) licensed.

- The [`webviz-config` logo](./webviz_config/_docs/static/webviz-logo.svg) is [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)


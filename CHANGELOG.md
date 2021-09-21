# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [UNRELEASED] - YYYY-MM-DD
### Changed
- [#502](https://github.com/equinor/webviz-config/pull/502) - Updated to `Dash 2.0`.

### Fixed
- [#498](https://github.com/equinor/webviz-config/pull/498) - Explicitly use UTC when comparing time zones in the `OAuth` implementation.
- [#476](https://github.com/equinor/webviz-config/pull/476) - Use Azure SDK Python packages instead of wrapping Azure CLI.

### Added
- [#503](https://github.com/equinor/webviz-config/pull/503) - Added `__main__.py`. This will allow users to do `python -m webviz_config [...]` in addition to `webviz [...]`.
- [#510](https://github.com/equinor/webviz-config/pull/510) - Added command line option `--debug` which enables selected underlying Dash development features.
- [#496](https://github.com/equinor/webviz-config/pull/496) - Implemented automatic menu creation from YAML file with new `wcc` Menu component (see https://github.com/equinor/webviz-core-components/pull/154).

## [0.3.4] - 2021-08-30

### Fixed
- [#482](https://github.com/equinor/webviz-config/pull/482) - Reverted the assumption
made in [#419](https://github.com/equinor/webviz-config/pull/419) that all argument
section in init-docstrings are lists of argument descriptions, and separated deprecated
plugins and arguments in doc sidebar.
- [#489](https://github.com/equinor/webviz-config/pull/489) - Use Docker user on
numerical format (in order for Radix/Kubernetes to correctly infer non-root user).
Also changed to use new Radix supported blob mount driver.

## [0.3.3] - 2021-07-13

### Changed
- [#474](https://github.com/equinor/webviz-config/pull/474) - Remove 62.5% CSS IE workaround.
- [#470](https://github.com/equinor/webviz-config/pull/470) - Improve VSCode YAML schema installation documentation.

## [0.3.2] - 2021-06-06

### Added
- [#456](https://github.com/equinor/webviz-config/pull/456) - Extended error message
when configuration file is invalid with suggestion to run `webviz docs`.
- [#426](https://github.com/equinor/webviz-config/pull/426) - Added centralized factory
registry exposed through `WEBVIZ_FACTORY_REGISTRY` for sharing factories between plugins.
- [#443](https://github.com/equinor/webviz-config/pull/443) - Added `--logconfig` command
line argument to allow detailed control of logging output in webviz.
- [#447](https://github.com/equinor/webviz-config/pull/447) - Plugin project dependencies
(indirect and direct) are now included in `PLUGIN_PROJECT_METADATA`. This enables
the generated Docker setup, when portable apps are built, to have the same dependency
versions compared to what the user had installed when creating the portable app.
- [#445](https://github.com/equinor/webviz-config/pull/445) - Added report feedback
button to `WebvizPluginABC`.

### Fixed
- [#463](https://github.com/equinor/webviz-config/pull/463) - Reflect external change.
Repository name for standard `OAuth2` Docker containers is changed from
`quay.io/pusher/oauth2_proxy` to `quay.io/oauth2-proxy/oauth2-proxy`.
- [#440](https://github.com/equinor/webviz-config/pull/440) - Fixed setting of global
log level for webviz application.
- [#457](https://github.com/equinor/webviz-config/pull/457) - Use non-root `redis`
Docker image in generated Radix setup.

## [0.3.1] - 2021-04-29

### Fixed
- [#429](https://github.com/equinor/webviz-config/pull/429) - Moved `FutureWarnings`
from `deprecated_decorators.py` to `_config_parser.py`. Simplified deprecation warnings.
- [#432](https://github.com/equinor/webviz-config/pull/432) - Replaced `WebvizPluginABC` type in
`deprecated_plugin` decorator with `Type[WebvizPluginABC]`.
- [#433](https://github.com/equinor/webviz-config/pull/433) - Removed short message
from `deprecated_plugin` decorator.
- [#435](https://github.com/equinor/webviz-config/pull/435) - Support only specifying
`source_url` in `setup.py` when building Dockerfile.

## [0.3.0] - 2021-04-27

### Added
- [#419](https://github.com/equinor/webviz-config/pull/419) - Plugins and their
arguments can now be marked as deprecated by using the newly implemented
deprecation framework that, in addition to console FutureWarnings,
automatically shows deprecation messages to the end user in the app and in the documentation.
Adjusted contributing guide accordingly.
- [#318](https://github.com/equinor/webviz-config/pull/318) - `webviz-config`
now facilitates automatically including necessary plugin projects as dependencies
in generated Docker setup. Private repositories are also supported, however the
Docker build process would then need to be given deploy keys as environment variable
secrets. First iteration of automatically creating a corresponding
[Radix config](https://www.radix.equinor.com/) and deploying a Radix application
is also added.
- [#423](https://github.com/equinor/webviz-config/pull/423) - Added class name
`webviz-config-markdown` to the output from the `webviz-config` `Markdown` plugin
output, such that Webviz themes can optionally reduce CSS scope to the output from
the `Markdown` plugin.

### Changed
- [#419](https://github.com/equinor/webviz-config/pull/419) - Changed `plugin_metadata`
and `plugin_project_metadata` in `webviz_config.plugins` to uppercase.
- [#409](https://github.com/equinor/webviz-config/pull/409) - Relax Python test
dependency constraints.
- [#318](https://github.com/equinor/webviz-config/pull/318) - Ad-hoc plugins not
supported anymore (i.e. plugins not being part of a Python project with `setup.py`).
This enables us to reserve the configuration file syntax `prefix.PluginName` to later.
Requiring a formal Python project also enables useful features in the framework
(see e.g. the `Added` section for this PR).

### Fixed
- [#415](https://github.com/equinor/webviz-config/pull/415) - Reduce height of main
sidebar to prevent overflow.
- [#422](https://github.com/equinor/webviz-config/pull/422) - Remove deprecated 'plugin-types' CSP directive.

## [0.2.9] - 2021-02-23

### Changed
- [#395](https://github.com/equinor/webviz-config/pull/395) - Update `npm` dependencies.
See also [#392](https://github.com/equinor/webviz-config/pull/392)
(`docsify-copy-code` update) and [#393](https://github.com/equinor/webviz-config/pull/393)
(`katex` update).

## [0.2.8] - 2021-01-26

### Added
- [#345](https://github.com/equinor/webviz-config/pull/345) - Added Oauth2
Authorization Code flow support for Azure AD applications.

### Changed
- [#374](https://github.com/equinor/webviz-config/pull/374) - Removed Webviz
  SSL certificate generation and forcing of HTTPS connections.
- [#388](https://github.com/equinor/webviz-config/pull/388) - Firefox preferred as
default browser over Chrome/Chromium to ease the transition on localhost after #374.
Browser defined with `webviz preferences --browser somebrowser` is still used instead
of the new default (Firefox).

### Fixed
- [#380](https://github.com/equinor/webviz-config/pull/380) - Don't write warning
for multiple versions of same plugin if the metadata is equal.

## [0.2.7] - 2021-01-14

### Changed
- [#368](https://github.com/equinor/webviz-config/pull/368) - Made Webviz global
settings available to plugin implementations through special `webviz_settings`
argument. This argument is an instance of the `WebvizSettings` class and currently
contains both the `shared_settings` and `theme` properties.

### Deprecated
- [#368](https://github.com/equinor/webviz-config/pull/368) - Access to `webviz_settings`
as an attribute on the Dash application instance object (currently being passed to the
plugins as the special `app` argument) has been deprecated.

## [0.2.6] - 2021-01-07

### Fixed
- [#373](https://github.com/equinor/webviz-config/pull/373) - Fix for import of TypedDict
in Python versions older than 3.8. Check against Python version instead of using try-except.

## [0.2.5] - 2020-12-19

### Changed
- [#367](https://github.com/equinor/webviz-config/pull/367) - Made type information
available to package consumers by indicating support for typing as specified in
[PEP 561](https://www.python.org/dev/peps/pep-0561/).

## [0.2.4] - 2020-12-08

### Changed
- [#362](https://github.com/equinor/webviz-config/pull/362) - Bumped pandas requirement
to `pandas>=1.0`, as `pandas==0.24.2` is no longer needed in internal deployment.

### Fixed
- [#351](https://github.com/equinor/webviz-config/pull/351) - Fixed bug in automatically
generated docs when having a defaulted input argument of type `pathlib.Path` in plugin
arguments.
- [#354](https://github.com/equinor/webviz-config/pull/354) - Fixed bug in automatically
generated docs when having type hinted return value of plugin `__init__` functions.

## [0.2.3] - 2020-11-26

### Added
- [#337](https://github.com/equinor/webviz-config/pull/337) - New generic plugin to
generate a [Pivot table](https://en.wikipedia.org/wiki/Pivot_table) based on
[Dash Pivottable](https://github.com/plotly/dash-pivottable).
- [#333](https://github.com/equinor/webviz-config/pull/333) - Warning is now raised
if more than one plugin project provides a plugin with the same name.

## [0.2.2] - 2020-11-16

### Fixed
- [#339](https://github.com/equinor/webviz-config/pull/339) - After
[#230](https://github.com/equinor/webviz-config/pull/230) generated app started using
Dash `dcc.Location` and `dcc.Link` instead of tabs for multi-page apps. This enabled
URL routing. At the same time, the root url `/` special case was set to show
"Front page", however, users did not from before necessarily have a page called
"Front page", as the "Front page" shown earlier was simply the first page in the list.
Changed back to behavior prior to #230 - i.e. show first page in config as "Front page"
and not rely on page title.

## [0.2.1] - 2020-10-29

### Changed
- [#324](https://github.com/equinor/webviz-config/pull/324) - Now also `webviz-config`
shipped plugins install themselves through the `webviz_config_plugins` entrypoints group.
- [#325](https://github.com/equinor/webviz-config/pull/325) - Removed support for
ad-hoc plugins as this is costly to maintain. Also, the `module.PluginName` notation in
configuration files can then in future be used fo distinguish between multiple plugin
packages using the same plugin name.
- [#330](https://github.com/equinor/webviz-config/pull/330) - Pie chart plot type now
available in table plotter.

### Fixed
- [#325](https://github.com/equinor/webviz-config/pull/325) - Support plugin projects
that use different name for top level package and distribution name.

## [0.2.0] - 2020-10-06

### Changed
- [#230](https://github.com/equinor/webviz-config/pull/230) - Instead of using
`dcc.Tabs` to give the impression of a "multipage app", webviz now uses `dcc.Link` and
`dcc.Location`. This has two main advantages: Big applications can have significantly
faster loading time, as only callbacks on selected "page" fire initially. In addition,
the user can navigate with forward/backward buttons in browser, as well as getting
an URL they can share with others in order to point them to the correct "page". Plugin
authors should check that persistence is set to `session` on Dash components they use
if they want user selections to remain across "page" changes. In order to get more
easily typed URLs, runtime generated page IDs now use `-` instead of `_` for spaces.

### Fixed
- [#321](https://github.com/equinor/webviz-config/pull/321) - Allowed for `blob:`
in `img-src` CSP such that `plotly.js` "Download to png" works properly.

## [0.1.4] - 2020-09-24

### Added
- [#311](https://github.com/equinor/webviz-config/pull/311) - Automatically add a comment
in generated application regarding which Python executable (`sys.executable`) was used
when building a portable application.
- [#310](https://github.com/equinor/webviz-config/pull/310) - Added `RuntimeWarning`
which appears if `@webvizstore` decorated functions are given argument values of type
`pandas.DataFrame` or `pandas.Series` (Which are known to not have `__repr__` functions
useful for hashing).

### Fixed
- [#313](https://github.com/equinor/webviz-config/pull/313) - Added `min-width` to menu CSS
such that it does not collapse on wide content. In addition, make sure menu `width` is
only specified on screen widths wide enough to be above the Dash `Tabs` provided breakpoint at
`800px`.

## [0.1.3] - 2020-09-22
### Added
- [#283](https://github.com/equinor/webviz-config/pull/283) - Auto-generated Webviz plugin documentation
now has search functionality (using [`docsify` full text search](https://docsify.js.org/#/plugins?id=full-text-search)).
- [#278](https://github.com/equinor/webviz-config/pull/278) - Plugin authors can now use Dash inline callbacks
(i.e. `app.clientside_callback(...)`) without being in conflict with the strict
[CSP rules](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy)
enforced by `webviz-config` (inline script hashes are added automatically).

### Changed
- [#294](https://github.com/equinor/webviz-config/pull/294) - Plugin authors can now define file type to download
(including specifying MIME type). Before only `.zip` archives were supported.
- [#281](https://github.com/equinor/webviz-config/pull/281) - Now uses `importlib` instead of `pkg_resources` for
detecting plugin entry points and package versions.
- [#306](https://github.com/equinor/webviz-config/pull/306) - Now runs `WEBVIZ_ASSETS.make_portable` before
`WEBVIZ_STORE.build_store` when building portables, as it usually takes shorter time, and therefore will give
feedback quicker if something is wrong.

### Fixed
- [#308](https://github.com/equinor/webviz-config/pull/308) - Fixed `UnclosedFile` and `Resource` warnings,
which would appear if developer enabled e.g. `export PYTHONWARNINGS=default`. Also, Webviz now gracefully
exits on CTRL+C (`KeyboardInterrupt`) instead of giving (unnecessary) traceback to the user.
- [#295](https://github.com/equinor/webviz-config/pull/295) - Menu width is now specified. This both ensures
the menu does not collapse if plugin content is wide, as well as not too wide itself if page titles are long
(instead page titles in the menu are wrapped). Also added `<meta name="viewport" content="width=device-width, initial-scale=1">`
for better experience on mobiles.

## [0.1.2] - 2020-09-09
### Added
- [#279](https://github.com/equinor/webviz-config/pull/279) - Added scrollbar to menu (when larger than screen size).

## [0.1.1] - 2020-09-02
### Added
- [#269](https://github.com/equinor/webviz-config/pull/269) - Added an optional argument `screenshot_filename` to `WebvizPluginABC`. Can be used to let plugin authors specify filename used when screenshots of the plugin are saved.
- [#275](https://github.com/equinor/webviz-config/pull/275) - Indented docstrings are now supported by `webviz docs`.

## [0.1.0] - 2020-08-24
### Added
- [#265](https://github.com/equinor/webviz-config/pull/265) - Added support to automatically create JSON/YAML schema based on installed plugins to be used in e.g. VSCode with the [Red Hat YAML extension for VSCode](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml). Create a schema by running `webviz schema`.

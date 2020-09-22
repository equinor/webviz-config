# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - YYYY-MM-DD
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

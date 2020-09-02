# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2020-09-02
### Added
- [#269](https://github.com/equinor/webviz-config/pull/269) - Added an optional argument `screenshot_filename` to `WebvizPluginABC`. Can be used to let plugin authors specify filename used when screenshots of the plugin are saved.
- [#275](https://github.com/equinor/webviz-config/pull/275) - Indented docstrings are now supported by `webviz docs`.

## [0.1.0] - 2020-08-24
### Added
- [#265](https://github.com/equinor/webviz-config/pull/265) - Added support to automatically create JSON/YAML schema based on installed plugins to be used in e.g. VSCode with the [Red Hat YAML extension for VSCode](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml). Create a schema by running `webviz schema`.

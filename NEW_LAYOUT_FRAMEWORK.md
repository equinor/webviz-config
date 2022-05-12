# New Webviz Plugin Framework

The new `Webviz Plugin Framework` aims to improve consistency, (re-)usability and structure of Webviz plugins. It provides
new abstract Python classes that can be inherited from in order to build easily understandable plugins with better 
separation of different views on a common data source.

## Motivation

Webviz is a liberal framework which gives a lot of freedom to developers to design and implement their individual 
plugins. However, even though a high degree of freedom can be beneficial regarding its different applications and the 
different requirements of its users, it also comes with its downsides. Having a pool of developers with various 
backgrounds and experiences, it can be challenging to deliver a consistent experience to the end users. Moreover,
the way plugins are implemented and structured is also object to individual preference and experience.

The goal of this framework is to structure Webviz plugins in a way that promises better usability and comprehensibility
while still providing a high degree of freedom to the individual plugin developers. Moreover, it allows for easier reusability of individual views and view elements.

## Introduction / Overview

The layout of a Webviz application can be separated in three main elements: 

- the `Main menu` for navigating the pages of an application, 
- the `Settings drawer` for displaying all preferences affecting the current view, and
- the `Content container` which wraps the plugins of the current page.

![Webviz Layout High-level Overview](/assets/high-level-overview.png)

A Webviz application consists of one or multiple pages. These are shown in the `main menu` and each can contain one or 
more plugins. A plugin is regarded as a set of views on a concrete data source. A view is structured by using view 
elements which contain a single visualization element and are shown in the `content container`. A visualization element 
can for example be a table, a plot or a map. Each plugin, view and view element can have its own settings. 
These can be separated in three different types:

- Settings which change the whole data source and affect all views,
- Settings which only change the currently active view, and
- Settings which change the style/view of a concrete element, e.g. the axes range of a plot or the number of rows shown 
in a table.

The first two types are displayed in the settings drawer while the last one is accessible via the `View element` actions 
(see below).

The following illustration gives an overview over all elements in the new layout framework.

![Webviz Layout Overview](/assets/webviz-layout-overview.png)
 
## Changes from old layout framework

### Views: From tabs to view selector

One of the major changes from the old to the new layout framework is the replacement of tabs with views.

![Before and after: From tabs to views](/assets/before-after-tabs-views.png)

Tabs have been widely used to provide different views on the same data source. They were placed at the top of a plugin 
and had to be implemented in the plugin's `layout()` function as individual containers. However, it was up to the 
plugin author to decide how views were made available in the user interface. The new view framework provides a 
consistent way to define views and makes them accessible via the `View selector` in the settings drawer. This has the 
advantage of saving space at the top of the page and provides a consistent user experience, since it standardises how
views are presented and accessed.  

### Plugin settings: From individual settings container to settings drawer

Another change is the standardisation of how plugin settings are made available. Before, settings were often displayed
in a separate container on either of the sides of the plugin (left and/or right). However, there was no consistent way 
of displaying settings. The new layout framework solves this issue by always displaying plugin and view settings in the 
settings drawer next to the main menu.

![Before and after: From individual settings container to settings drawer](/assets/before-after-settings.png)

### Plugin actions: Moved from `PluginPlaceholder` to settings drawer

Plugin actions, as e.g. `full screen` and `screenshot`, have been moved from the plugin placeholder to the settings 
drawer.

![Before and after: Plugin actions](/assets/before-after-plugin-actions.png)

## Getting started

### Terminology

#### - `ID`
Identifier for an entity within a plugin. This is not a unique identifier yet, but becomes one in combination with the plugin's `UUID`.

#### - `UID`
Unique identifier for a specific entity within a specific plugin. Created by combining an entity's `ID` with a plugin's `UUID`.

#### - `UUID`
[Universal Unique Identifier](https://en.wikipedia.org/wiki/Universally_unique_identifier) - Each plugin creates such a `UUID` when being initialized. This is used to uniquely identify each instance of a plugin.

#### - `View`
Represents a specific perspective on the plugin's dataset. Consists of one or multiple `ViewElements` and uses `ViewLayoutElements` to structure these in rows and columns.

*Python base class: `ViewABC`*

#### - `ViewLayoutElement`
A layout helper element that can either be a row or a column. These layout elements can again contain other `ViewLayoutElements` or `ViewElements`, allowing for creation of complex view layouts. 

*Python base class: `ViewLayoutABC`*

#### - `ViewElement`
Layout element wrapping a data visualization, description or documentation. A `View` consists of one or more `ViewElements`.

*Python base class: `ViewElementABC`* 


### Implementing a new plugin

Every new plugin starts with a new class inheriting from `WebvizPluginABC`.

```python
from webviz_config import WebvizPluginABC

class MyPlugin(WebvizPluginABC):
    def __init__(self):
        super().__init__()
```

The data supposed to be visualized in the plugin is either given directly as an argument from within the config file or the path to a data source (e.g. a file) is provided. The latter is the most common approach.

```python
from pathlib import Path

import pandas as pd

from webviz_config import WebvizPluginABC

class MyPlugin(WebvizPluginABC):
    def __init__(self, path_to_csv_file: Path):
        super().__init__()

        self.data = pd.read_csv(path_to_csv_file)
```

When wanting to add a view to the plugin, a new class inheriting from `ViewABC` must be implemented.

```python
from webviz_config.webviz_plugin_subclasses._views import ViewABC

class MyView(ViewABC):
    def __init__(self):
        super().__init__("My view")
```

This views can then be added to the plugin by using

```python
self.add_view(MyView(), "MyView")
```

whereas the second argument is the id of the view that can be used to access it later on.

#### Views

#### Shared settings

###

- Add ViewElements directly or indirectly
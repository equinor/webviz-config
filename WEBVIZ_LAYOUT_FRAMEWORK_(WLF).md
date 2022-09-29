# Webviz Layout Framework (WLF)

The `Webviz Layout Framework (WLF)` aims to improve consistency, (re-)usability and structure of Webviz plugins. It provides
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

#### - `UniqueID`
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

![Implement a new plugin](/assets/implement-plugin.svg)

Every new plugin starts with a class inheriting from `WebvizPluginABC`.

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

### Creating a view

![Implement a new view](/assets/implement-view.svg)

When wanting to add a view to the plugin, a new class inheriting from `ViewABC` must be implemented.

```python
from webviz_config.webviz_plugin_subclasses._views import ViewABC

class MyView(ViewABC):
    def __init__(self):
        super().__init__("My view")
```

This view can then be added to any plugin by using

```python
class MyPlugin(WebvizPluginABC):
    def __init__(self):
        super().__init__()
        ...
        self.add_view(MyView(self.data), "MyView")
```

whereas the second argument is the id of the view which can be used to access it later on.

Data can also be provided from the plugin to the view by passing it as an argument to the constructor.

```python
class MyView(ViewABC):
    def __init__(self, data: pd.DataFrame):
        super().__init__("My view")
        self.data = data
```

NOTE: It is recommended to use a file per plugin which defines all elements' IDs. Read more about this best practice here: MISSING LINK

### Add content to a view - implement a view element

![Implement a new view element](/assets/implement-view-element.svg)

A view by itself does not contain anything yet. In order to create content, usually a ViewElement is implemented.

```python
from webviz_config.webviz_plugin_subclasses._views import ViewElementABC

class MyViewElement(ViewElementABC):
    def __init__(self):
        super().__init__("My view element")
```

The content of the view element itself is defined in the ViewElement's `inner_layout` function.

```python
    def inner_layout(self) -> Component:
        return html.Div() # return any Dash components here
```

All elements in the layout function can be given a unique id by using the `ViewLement.register_component_unique_id` function. This is a requirement for using the components in Dash callbacks later on.

```python
    def inner_layout(self) -> Component:
        return html.Div(id=self.register_component_unique_id("MyDiv"))
```

### Add a settings group

![Implement a settings group](/assets/implement-settings-group.svg)

A settings group is the preferred place to implement the settings for either a view or even the whole plugin.

```python
from webviz_config.webviz_plugin_subclasses._views import SettingsGroupABC

class MySettingsGroup(SettingsGroupABC):
    def __init__(self):
        super().__init__("My settings")
```

It is either added in the view's or the plugin's `__init__` function.

```python
class MyView(ViewABC):
    def __init__(self):
        super().__init__()
        ...
        self.add_settings_group(MySettingsGroup(), "MySettingsGroup")
```

When added to the latter it is added as a shared settings group that is shared among multiple views.

```python
class MyPlugin(WebvizPluginABC):
    def __init__(self):
        super().__init__()
        ...
        self.add_shared_settings_group(MySettingsGroup(), "MySettingsGroup")
```

It can be controlled in which views the settings group shall be visible or in which it should be hidden.

```python
class MyPlugin(WebvizPluginABC):
    def __init__(self):
        super().__init__()
        ...
        self.add_shared_settings_group(MySettingsGroup(), "MySettingsGroup", visible_in_views=[self.view("MyView").get_unique_id().to_string()])
```

```python
class MyPlugin(WebvizPluginABC):
    def __init__(self):
        super().__init__()
        ...
        self.add_shared_settings_group(MySettingsGroup(), "MySettingsGroup", not_visible_in_views=[self.view("MyView").get_unique_id().to_string()])
```

The layout of a settings group is implemented in its `layout` function. Note that this function needs to return a list of components.

```python
    ...
    def layout(self) -> List[Component]:
        return [html.Div()]
```

### Handling IDs while guaranteeing uniqueness

It is very important for each component to have a unique ID within a Webviz application in order to identify each single component in any callback. The WLF ID handling system helps with this issue. Each plugin automatically gets a UUID assigned. The ID of each view or shared settings group is then appended to this UUID, e.g.:

```
{plugin-uuid}-{view-id}
```

This concept is continued for view elements and their components or settings groups.
```
{plugin-uuid}-{view-id}-{view-element-id}
{plugin-uuid}-{view-id}-{view-element-id}-{component-id}
{plugin-uuid}-{view-id}-{view-element-id}-{settings-group-id}
{plugin-uuid}-{view-id}-{settings-group-id}
```

The unique ID of any layout element is accessible via its `get_unique_id()` method. This will return a `LayoutUniqueId` object which can be used to get any of the parent IDs and which can be transformed to a string (e.g. when using in a callback) by using its `to_string()` method (or its string representation).

```python
my_view.get_unique_id() # returns a LayoutUniqueId object
my_view.get_unique_id().to_string() # returns a string representation of the unique ID
str(my_view.get_unique_id()) # returns a string representation of the unique ID
```

In order for this concept to work, it is important to use it for all components, i.e. when implementing the layout of a view element or a settings group, all components' IDs should be assigned using the `self.register_component_unique_id("component-id")` function. This returns a string representation of a unique ID in the shape of e.g. 

```
{plugin-uuid}-{view-id}-{view-element-id}-{component-id}
```

Moreover, this registers the ID of the component in the plugin and guarantees its uniqueness. A plugin does not allow two components in the same layout element to have the same ID. 

A component's ID does only need to be registered once, in the respective `layout` function (otherwise, the plugin will warn about a duplicate ID). When wanting to get the unique ID of a component in a callback, the layout element's `component_unique_id("component-id")` can be used. 

Note: In each encapsulation, i.e. layout element (view, view element, settings group etc.), each component's or layout element's local ID ("component-id" in the examples above) must be unique. However, the same local ID can be used in any other layout element, since the global unique ID will always be different (remember e.g. `{plugin-uuid}-{view-id}-{view-element-id}-{component-id}`). This concept allows for using e.g. the same view class twice in a plugin (e.g. with different arguments and IDs).

### Group multiple views

Sometimes, it is desirable to group views together, e.g. when these are represent different ways of visualizing one aspect of the data source. When adding a view to a plugin, a view group name can be added. All groups with the same group name will automatically be grouped together.

```python
class MyPlugin(WebvizPluginABC):
    def __init__(self):
        super().__init__()
        ...
        self.add_view(MyView(self.data1), "MyView1", "My View Group")
        self.add_view(MyView(self.data2), "MyView2", "My View Group")
```

###

- Add ViewElements directly or indirectly

#### ElementIdFile

### How to set initially active view

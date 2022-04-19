# New Webviz Plugin Framework

The new `Webviz Plugin Framework` aims on improving consistency, usability and structure of Webviz plugins. It provides
new abstract Python classes that can be inherited from in order to build easily understandable plugins with better 
separation of different views on a common data source.

## Motivation

Webviz is a liberal framework which gives a lot of freedom to developers to design and implement their individual 
plugins. However, even though a high degree of freedom can be beneficial regarding its different applications and the 
different requirements of its users, it also comes with its downsides. Having a pool of developers with various 
backgrounds and experiences, it can be challenging to deliver a consistent experience to the end users. Moreover,
the way plugins are implemented and structured is also object to individual preference and experience.

The goal of this framework is to structure Webviz plugins in a way that promises better usability and comprehensibility
while still providing a high degree of freedom for the individual plugin developers.

## Introduction / Overview

A Webviz application consists of one or multiple pages. Each of these can again contain one or more plugins. A plugin
is regarded as a set of views on a concrete data source. A view is structured by using view elements which contain a 
single visualization element. This can for example be a table, a plot or a map. 

The layout of a Webviz application can be separated in three main elements: 
- the `Main menu` for navigating the pages of an application, 
- the `Settings drawer` for displaying all preferences affecting the current view, and
- the `Content container` which wraps the plugins of the current page.

![Webviz Layout High-level Overview](/assets/high-level-overview.png)

Settings that users can apply to a Webviz application can be separated in three different types:
- Settings which change the whole data source and affect all views,
- Settings which only change the currently active view, and
- Settings which change the style of a concrete element, e.g. the axes range of a plot or the number of rows shown in a 
table.


The first two types are displayed in the settings drawer while the last one is accessible via the `View element` actions 
(see below).

The new layout framework comes with a couple of new elements and containers which are highlighted and explained in the 
following illustration.

![Webviz Layout Overview](/assets/webviz-layout-overview.png)


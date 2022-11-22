# This is a big title

## This is a somewhat smaller title

### This is a subsubtitle

Hi from a Markdown text file containing Norwegian letters (æ ø å), some
**bold** letters, _italic_ letters. _You can also **combine** them._

You can also add (potential multi-line) equations as illustrated here with the Maxwell equations,
$$
\begin{aligned}
\nabla \cdot \mathbf{E} &= \frac {\rho} {\varepsilon_0} \\\\
\nabla \cdot \mathbf{B} &= 0 \\\\
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}} {\partial t} \\\\
\nabla \times \mathbf{B} &= \mu_0\left(\mathbf{J} + \varepsilon_0 \frac{\partial \mathbf{E}} {\partial t} \right)
\end{aligned}
$$
You can also add inline math where you e.g. describe the different parameters that goes into
the equations, like $\varepsilon_0$ being permittivity of free space.

---

Horizontal line splitting two paragraphs.

#### An unordered list

* Item 1
* Item 2
    * Item 2a
    * Item 2b

#### An automatically ordered list

1. Item 1
1. Item 2
     1. Item 2a
     1. Item 2b

#### An image with a caption

![width=40%,height=300px](./example_banner.png "Some caption")

#### Quote

> Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
> tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
> quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

#### Collapsible text

<details>
  <summary>This is the title of some detailed information</summary>
  Here is some more information, which can be extended/collapsed on demand.
</details>

#### An example table

First Header | Second Header
------------ | -------------
Content Cell | Content Cell
Content Cell | Content Cell

#### Some code

```python
def some_function(input: int) -> int:
    return 42 * input
```
# astruc
A pretty `code2graph` parser for Python. The backbone is the Abstract Syntax Tree.



## Toy Example

Source code:

```python
def relu(x):
    if x > 0:
        return x
    else:
        return 0
```

Graph:

```mermaid
graph TD
    funcdef(relu) --> arg(arguments)
    funcdef --> if(If) --> return1(Return)
    arg --> name1(x)
    if --> return2(Return)
    if --> compare(Compare)
    compare --> name2(x)
    compare --> op(Gt)
    compare --> num1(0)
    return1 --> num2(1)
    return2 --> num3(0)
```



## Installation

```bash
pip install astruc
```



## Usage

**Quick start**

```python
from astruc import CodeStruc

source =\
"""def relu(x):
    if x > 0:
        return x
    else:
        return 0
"""
cs = CodeStruc(code)
# Obtain the AST.
tree = cs.walk()
# Obtain the adjacency matrix.
adj = cs.matrix()
```


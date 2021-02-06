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
    func(relu) --> arg(arguments)
    func --> if(If) --> return1(Return)
    arg --> x1(x)
    if --> return2(Return)
    if --> compare(Compare)
    compare --> x2(x)
    compare --> gt(Gt)
    compare --> n1(0)
    return1 --> n2(1)
    return2 --> n3(0)
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


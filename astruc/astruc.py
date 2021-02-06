import ast
import asttokens
import numpy as np


class CodeStruc(object):
    """
    CodeStruc is used to transform a code snippet to its Abstract Syntax Tree.
    It supports additional tokenizer to further split node tokens into sub-tokens.
    """
    class Node(object):
        """Special node type for walking Abstract Syntax Tree."""
        def __init__(self, node, token, pos, sl=0):
            self.node = node
            self.token = token
            self.pos = pos
            self.sl = sl

    def __init__(self, source, tokenizer=None):
        self.source = source
        self.astok = asttokens.ASTTokens(source, parse=True)
        self.use_tokenizer = True if tokenizer else False
        self.tokenizer = tokenizer

        self.ast = []
        self.tokens = []
        self.le = 0

    def walk(self):
        """
        Applies depth-first pre-order traversal on the AST, Similar as asttokens.util.walk().
        However, it directly returns the AST in the format of a json list.
        """
        if self.ast:
            return self.ast

        root = self.astok.tree
        # We skip the Module node, which is nothing but an entry.
        if isinstance(root, ast.Module):
            root = list(self.iter_children(root))[0]
        stack = [self.get_node(root)]
        while stack:
            current = stack.pop()
            children = []
            ins = len(stack)
            for c in self.iter_children(current.node):
                # Though we do not include Store and Load nodes into the graph,
                # we still reserve them for indicating data dependency.
                if isinstance(c, (ast.Store, ast.Load)):
                    current.sl = 1 if isinstance(c, ast.Store) else 2
                    # It must be a terminal node.
                    break
                node = self.get_node(c)
                children += [node]
                stack.insert(ins, node)
            self.ast += [{"current": current, "children": children}]

        for node in self.ast:
            self.tokens.extend(node["current"].token)
        self.ast.sort(key=lambda x: x["current"].pos[0])
        return self.ast

    def get_node(self, node):
        """Return a Node object of a specific AST node."""
        if self.use_tokenizer:
            tokens = self.tokenizer.tokenize(self.get_text(node)).words()
            # In case of empty token.
            if not tokens:
                tokens = ['_']
            node = self.Node(node, tokens, list(range(self.le, self.le + len(tokens))))
            self.le += len(node.pos)
            return node
        else:
            node = self.Node(node, [self.get_text(node)], [self.le])
            self.le += 1
            return node

    def get_text(self, node):
        """
        Return the corresponding text of an AST node, which is composed of both type and value information.
        We use type information to represent the singleton nodes which do not correspond to specific text.
        """
        if isinstance(node, ast.FunctionDef):
            return node.name
        else:
            if self.astok.get_text(node):
                text = self.astok.get_text(node)
                # Terminal nodes.
                if not any(self.iter_children(node)):
                    return text
                # Non-terminal nodes but with Store or Load child.
                elif all([isinstance(c, (ast.Store, ast.Load)) for c in self.iter_children(node)]):
                    return text
                else:
                    return str(node.__class__)[13: -2]
            else:
                return str(node.__class__)[13: -2]

    def matrix(self):
        """Return the adjacency matrix of the generated AST in the format of an array of numpy."""
        matrix = np.zeros([512, 512], dtype=np.bool) if self.le <= 512 else np.zeros([self.le, self.le], dtype=np.bool)
        for i, node in enumerate(self.ast):
            pos = node["current"].pos
            for p in pos:
                matrix[p][p] = 1
            for c in node["children"]:
                for p in pos:
                    matrix[p, c.pos] = 1
                    matrix[c.pos, p] = 1
            if node["current"].sl == 2:
                for j in range(i):
                    if self.ast[j]["current"].token == node["current"].token and self.ast[j]["current"].sl == 1:
                        for p in pos:
                            matrix[p, self.ast[j]["current"].pos] = 1

        return matrix

    def tree(self):
        """
        Return the prettified tree.
        Each node is composed of two properties, tokens and position.
        """
        tree = []
        for node in self.ast:
            tree += [
                {
                    "current": (node["current"].token, node["current"].pos),
                    "children": [(c.token, c.pos) for c in node["children"]]
                }
            ]
        return tree

    @staticmethod
    def iter_children(node):
        """
          Yields all direct children of an AST node, similar as asttokens.util.iter_children_ast().
          However, we do not skip the singleton nodes like Store and Load.
          """
        if node.__class__.__name__ == 'JoinedStr':
            return

        if isinstance(node, ast.Dict):
            for (key, value) in zip(node.keys, node.values):
                if key is not None:
                    yield key
                yield value
            return

        for child in ast.iter_child_nodes(node):
            yield child

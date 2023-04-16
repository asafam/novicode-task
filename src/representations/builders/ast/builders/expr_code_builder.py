import ast
from representations.builders.ast.builders.base_builder import BaseBuilder
from representations.tree.node import Node


class ExprBuilder(BaseBuilder):
    def build(self, root_item):
        text = ast.unparse(root_item)
        node = Node(text)

        return node

    def get_priority(self):
        return super().get_priority() + 1

    def is_match(self, item):
        name = type(item).__name__
        return name == "Expr"

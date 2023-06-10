import builtins
from typing import Optional
import symtable
# from symtable import symtable, SymbolTable
import libcst as cst
from libcst.metadata import (
    GlobalScope, ClassScope, FunctionScope, ComprehensionScope)


def list_symtable(source) -> list:
    table = symtable.symtable(source, "<string>", compile_type="exec")
    return _list_symtable_inner(table, [])


def _list_symtable_inner(table: symtable.SymbolTable, result: list):
    result.append(table)
    if table.has_children():
        for child in table.get_children():
            _list_symtable_inner(child, result)

    return result


def assert_scope_table_mapping(scope, table):

    assert len(scope) == len(table)

    # Global namespace
    s, t = scope[0], table[0]
    assert isinstance(s, cst.metadata.GlobalScope)
    assert t.get_type() == 'module'

    for s, t in zip(scope[1:], table[1:]):

        if isinstance(s, ClassScope):
            assert t.get_type() == 'class'
            assert s.name == t.get_name()

        elif isinstance(s, FunctionScope):
            assert t.get_type() == 'function'
            if s.name:
                assert s.name == t.get_name()
            else:
                assert t.get_name() == 'lambda'

        elif isinstance(s, ComprehensionScope):
            assert t.get_type() == 'function'
            # listcomp, dictcomp, setcomp, genexpr
            assert (name := t.get_name())[-4:] == 'comp' or name == 'genexpr'

        else:
            raise RuntimeError("must not happen")


class ModulassTransformer(cst.CSTTransformer):

    def __init__(self, source):
        super().__init__()
        self.source = source
        self.wrapper = cst.metadata.MetadataWrapper(cst.parse_module(source))
        self.module = self.wrapper.module
        self.node_to_scope = n_to_s = self.wrapper.resolve(cst.metadata.ScopeProvider)
        self.scopes = list(dict.fromkeys(n_to_s.values()))
        self.symtables = list_symtable(source)
        self.global_names = self.symtables[0].get_identifiers()
        assert_scope_table_mapping(self.scopes, self.symtables)

        self.builtins = set(n for n in builtins.__dict__.keys()
                            if n[:2] != '__' or n[-2:] != '__')

        # state variables
        self.in_func = 0
        self.attr_stack = []
        self.funcdef_name = None

    # @property
    # def global_names(self):
    #     return self.symtables[0].get_identifiers()

    def is_global(self, node: cst.Name):

        scope = self.node_to_scope.get(node, None)
        if not scope:
            return False

        i = next(i for i, v in enumerate(self.scopes) if scope == v)
        table = self.symtables[i]
        if table.get_type() == 'function':
            return node.value in table.get_globals()
        else:
            return node.value in table.get_identifiers()

    def should_replace(self, node: cst.Name):

        name = node.value
        # if name in self.builtins:
        if self.is_global(node):
            if name in self.global_names:   # including overwritten builtin names
                return True
            elif name in self.builtins:
                return False
            else:
                return True # Name not defined in the module namespace
        else:
            return False
        # return (self.is_global(node) and (self.global_names) and (name not in self.builtins))


    @property
    def transformed(self):
        return self.module.visit(self).code

    # def visit_Import(self, node: "Import") -> Optional[bool]:
    #     return False
    #
    # def visit_ImportFrom(self, node: "ImportFrom") -> Optional[bool]:
    #     return False

    def visit_AsName(self, node: "AsName") -> Optional[bool]:
        return False

    def visit_FunctionDef(self, node: "FunctionDef") -> Optional[bool]:

        if self.in_func > 0:
            self.in_func += 1
            return False

        self.funcdef_name = node.name
        self.in_func += 1

    def leave_FunctionDef(
        self, original_node: "FunctionDef", updated_node: "FunctionDef"
    ):
        if self.in_func > 1:
            self.in_func -= 1
            return updated_node

        self_param = cst.Param(name=cst.Name(value='self'))
        new_params = updated_node.params.with_changes(
            params=(self_param,) + tuple(updated_node.params.params)
        )

        self.funcdef_name = None
        self.in_func -= 1
        return updated_node.with_changes(params=new_params)

    def visit_ClassDef(self, node: "ClassDef") -> Optional[bool]:
        return False

    def visit_Attribute(self, node: "Attribute") -> Optional[bool]:
        self.attr_stack.append(node.attr)

    def leave_Attribute(
        self, original_node: "Attribute", updated_node: "Attribute"
    ) -> "BaseExpression":
        self.attr_stack.pop()
        return updated_node

    def leave_Name(
        self, original_node: "Name", updated_node: "Name"
    ) -> "BaseExpression":

        if original_node == self.funcdef_name:
            return updated_node
        elif self.attr_stack and self.attr_stack[-1] == original_node:
            return updated_node
        elif self.should_replace(original_node):
            return cst.Attribute(value=cst.Name('self'), attr=updated_node)
        else:
            return updated_node


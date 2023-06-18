import keyword
import sys
import builtins
import symtable
import textwrap
import argparse
import pathlib
from typing import Optional


# from symtable import symtable, SymbolTable
import libcst as cst
from libcst.metadata import (
    GlobalScope, ClassScope, FunctionScope, ComprehensionScope, ParentNodeProvider)
import libcst.matchers as m


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


class ModulassTransformer(m.MatcherDecoratableTransformer):

    METADATA_DEPENDENCIES = (ParentNodeProvider,)
    matchers_compstats = m.If() | m.Try() | m.With() | m.For() | m.While()

    def __init__(self, source, extract=None):
        super().__init__()
        self.source = source
        self.extract = extract
        self.wrapper = cst.metadata.MetadataWrapper(cst.parse_module(source))
        self.module = self.wrapper.module
        self.node_to_scope = n_to_s = self.wrapper.resolve(cst.metadata.ScopeProvider)
        self.parents = self.wrapper.resolve(ParentNodeProvider)
        self.scopes = list(dict.fromkeys(n_to_s.values()))
        self.symtables = list_symtable(source)
        assert_scope_table_mapping(self.scopes, self.symtables)

        self.name_to_symbol = [
            {s.get_name(): s for s in table.get_symbols()} for table in self.symtables
        ]
        self.global_names = set()

        self.builtins = set(n for n in builtins.__dict__.keys()
                            if n[:2] != '__' or n[-2:] != '__')

        # state variables
        self.in_func = 0
        self.attr_stack = []
        self.funcdef_name = None
        self.is_import = False

    def should_replace(self, node: cst.Name):

        # Name nodes in import statements are not in the keys of self.node_to_scope
        # For such names, their parents' scopes are looked for
        n = node
        while not (scope := self.node_to_scope.get(n, None)):
            prev = n
            n = self.parents[n]
            if n == prev:
                raise RuntimeError(f"scope not found for {n.value}")

        i = next(i for i, v in enumerate(self.scopes) if scope == v)

        if symbol := self.name_to_symbol[i].get(node.value, None):
            if symbol.is_global():
                if symbol_top := self.name_to_symbol[0].get(node.value, None):
                    return symbol_top.is_global() and symbol_top.is_assigned()
                elif node.value in self.builtins:
                    return False
                else:
                    return True
            else:
                return False
        else:   # names between from and import, True, False, None
            return False

    @property
    def transformed(self):
        return self.wrapper.visit(self).code

    @m.call_if_not_inside(m.FunctionDef())
    @m.leave(m.SimpleStatementLine() | matchers_compstats | m.Comment() | m.EmptyLine())
    def remove_statements(self, original_node, updated_node):
        if (parent := self.get_metadata(ParentNodeProvider, original_node)) == self.module:
            is_import = self.is_import
            self.is_import = False

            if self.extract == 'func':
                return cst.RemoveFromParent()
            elif self.extract == 'import':
                if is_import:
                    return updated_node
                else:
                    return cst.RemoveFromParent()
            elif self.extract == 'init':
                if is_import:
                    return cst.RemoveFromParent()
                else:
                    return updated_node
            else:
                return updated_node
        else:
            return updated_node

    @m.leave(m.Import() | m.ImportFrom())
    def flag_import(self, original_node, updated_node):
        self.is_import = True
        return updated_node

    def visit_FunctionDef(self, node: "FunctionDef") -> Optional[bool]:

        if self.extract and self.extract != 'func':
            return False

        if self.in_func > 0:
            self.in_func += 1
            return False

        self.funcdef_name = node.name
        self.in_func += 1

    def leave_FunctionDef(
        self, original_node: "FunctionDef", updated_node: "FunctionDef"
    ):
        if self.extract and self.extract != 'func':
            return cst.RemoveFromParent()

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

    def leave_ClassDef(
        self, original_node: "ClassDef", updated_node: "ClassDef"
    ):
        return cst.RemoveFromParent()

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
            # Do nothing if node is an attribute of another name
            return updated_node
        elif self.should_replace(original_node):
            return cst.Attribute(value=cst.Name('self'), attr=updated_node)
        else:
            return updated_node


_template = """\
{imports}

class {name}:

    def __init__(self):
{instance_vars}

{method_defs}
"""


def transform(source: str, class_name: str):
    imps = ModulassTransformer(source, extract='import').transformed
    vars = ModulassTransformer(source, extract='init').transformed
    defs = ModulassTransformer(source, extract='func').transformed

    return _template.format(
        name=class_name,
        imports=imps,
        instance_vars=textwrap.indent(vars, ' ' * 8),
        method_defs=textwrap.indent(defs, ' ' * 4)
    )


def transform_file(infile, outfile, class_name: str = ''):

    if not class_name:
        class_name = pathlib.Path(infile).stem

    if not class_name.isidentifier() or keyword.iskeyword(class_name):
        raise ValueError(f"{class_name} not a valid class name")

    with open(infile, 'r') as f_in:
        result = transform(f_in.read(), class_name)

    with open(outfile, 'w') as f_out:
        f_out.write(result)


def main(argv=sys.argv[1:]):
    """Transform a Python module into a class"""

    parser = argparse.ArgumentParser(description="Transform a module into a class")
    parser.add_argument('input',
                        help="input file path")
    parser.add_argument('output',
                        help="output file path")
    parser.add_argument('-n', '--name',
                        default='',
                        help="class name")

    args = vars(parser.parse_args(argv))
    transform_file(args['input'], args['output'], args['name'])

    return 0


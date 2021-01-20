from jsonpath_rw import parse
from json import loads
from pathlib import Path
from eth_vertigo.mutator.source_file import SourceFile


def _get_ast(json_file):
    return loads(json_file.read_text("utf-8"))


def _get_src(src_str: str):
    return [int(e) for e in src_str.split(":")]


def _get_binaryop_info(node: dict):
    """
    Gets info on the binary operation from an ast node
    This ast node must be referencing an binary operation

    :param node: ast node to look for
    :return: the operator, src for the operator
    """
    if node["nodeType"] != "BinaryOperation":
        raise ValueError("Passed node is not a binary operation")

    c_src = _get_src(node["src"])

    original_operator = node["operator"]
    op0_src = _get_src(node["leftExpression"]["src"])
    op1_src = _get_src(node["rightExpression"]["src"])

    if not (c_src[2] == op0_src[2] == op1_src[2]):
        raise ValueError("src fields are inconsistent")

    start = op0_src[0] + op0_src[1]
    length = op1_src[0] - start
    op_src = (start, length, c_src[2])

    return original_operator, op_src


def _get_op_info(node: dict):
    c_src = _get_src(node["src"])

    original_operator = node["operator"]
    op0_src = _get_src(node["leftHandSide"]["src"])
    op1_src = _get_src(node["rightHandSide"]["src"])

    if not (c_src[2] == op0_src[2] == op1_src[2]):
        raise ValueError("src fields are inconsistent")

    start = op0_src[0] + op0_src[1]
    length = op1_src[0] - start
    op_src = (start, length, c_src[2])

    return original_operator, op_src


class SolidityFile(SourceFile):
    def __init__(self, json_path: Path):
        self.json = _get_ast(json_path)
        self.ast = self.json["ast"]
        file = Path(self.json["sourcePath"])
        super().__init__(file)

    def get_binary_op_locations(self):
        path_expr = parse('*..nodeType.`parent`')
        for match in path_expr.find(self.ast):
            if match.value["nodeType"] != "BinaryOperation":
                continue
            yield _get_binaryop_info(match.value)

    def get_if_statement_binary_ops(self):
        path_expr = parse('*..nodeType.`parent`')
        for match in path_expr.find(self.ast):
            if match.value["nodeType"] != "IfStatement":
                continue
            condition = match.value["children"][0]
            yield _get_binaryop_info(condition)

    def get_assignments(self):
        path_expr = parse('*..nodeType.`parent`')
        for match in path_expr.find(self.ast):
            if match.value["nodeType"] != "Assignment":
                continue
            yield _get_op_info(match.value)

    def get_void_calls(self):
        path_expr = parse('*..nodeType.`parent`')
        for match in path_expr.find(self.ast):
            if match.value["nodeType"] != "FunctionCall":
                continue
            function_identifier = match.value["expression"]

            function_typedef = function_identifier["typeDescriptions"]["typeString"]
            if "returns" in function_typedef:
                continue
            if "function" not in function_typedef:
                continue
            if function_identifier["typeDescriptions"]["typeIdentifier"].startswith("t_function_event"):
                continue

            try:
                if "require" in function_identifier["name"]:
                    continue
            except KeyError:
                continue
            yield (None, _get_src(match.value["src"]))

    def get_modifier_invocations(self):
        path_expr = parse('*..nodeType.`parent`')
        for match in path_expr.find(self.ast):
            if match.value["nodeType"] != "ModifierInvocation":
                continue
            yield (None, _get_src(match.value["src"]))

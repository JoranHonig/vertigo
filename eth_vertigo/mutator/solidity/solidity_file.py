from jsonpath_rw import parse
from subprocess import Popen, PIPE
import re
from json import loads, JSONDecodeError
from pathlib import Path
from eth_vertigo.mutator.source_file import SourceFile


def _get_ast(file: Path):
    # Assert precondition
    if not file.exists():
        raise ValueError("File does not exist")

    # Execute solc
    command = ["/home/walker/installers/solc", "--ast-json"]
    command += [str(file)]
    proc = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = proc.communicate()

    if output == "":
        raise Exception("Error while retrieving the ast: {}".format(err))

    # Find the different ast's
    found_asts = {}
    current_contract = None
    current_json_lines = []

    for line in output.decode('utf-8').split("\n"):
        if re.match("======= .* =======", line):
            if current_json_lines and current_contract:
                json_string = "\n".join(current_json_lines)
                try:
                    found_asts[current_contract] = loads(json_string)
                except JSONDecodeError:
                    pass

            current_contract = line.split(" ")[1]
            current_json_lines = []
        else:
            current_json_lines.append(line)

    if str(file) in found_asts.keys():
        return found_asts[str(file)]
    return None


def _get_src(src_str: str):
    return [int(e) for e in src_str.split(":")]


def _get_binaryop_info(node: dict):
    """
    Gets info on the binary operation from an ast node
    This ast node must be referencing an binary operation

    :param node: ast node to look for
    :return: the operator, src for the operator
    """
    if node["name"] != "BinaryOperation":
        raise ValueError("Passed node is not a binary operation")

    c_src = _get_src(node["src"])

    original_operator = node["attributes"]["operator"]
    op0_src = _get_src(node["children"][0]["src"])
    op1_src = _get_src(node["children"][1]["src"])

    if not (c_src[2] == op0_src[2] == op1_src[2]):
        raise ValueError("src fields are inconsistent")

    start = op0_src[0] + op0_src[1]
    length = op1_src[0] - start
    op_src = (start, length, c_src[2])

    return original_operator, op_src


def _get_op_info(node: dict):
    c_src = _get_src(node["src"])

    original_operator = node["attributes"]["operator"]
    op0_src = _get_src(node["children"][0]["src"])
    op1_src = _get_src(node["children"][1]["src"])

    if not (c_src[2] == op0_src[2] == op1_src[2]):
        raise ValueError("src fields are inconsistent")

    start = op0_src[0] + op0_src[1]
    length = op1_src[0] - start
    op_src = (start, length, c_src[2])

    return original_operator, op_src


class SolidityFile(SourceFile):
    def __init__(self, file: Path):
        super().__init__(file)
        self.ast = _get_ast(file)

    def get_binary_op_locations(self):
        path_expr = parse('*..name.`parent`')
        for match in path_expr.find(self.ast):
            if match.value["name"] != "BinaryOperation":
                continue
            yield _get_binaryop_info(match.value)

    def get_if_statement_binary_ops(self):
        path_expr = parse('*..name.`parent`')
        for match in path_expr.find(self.ast):
            if match.value["name"] != "IfStatement":
                continue
            condition = match.value["children"][0]
            yield _get_binaryop_info(condition)

    def get_assignments(self):
        path_expr = parse('*..name.`parent`')
        for match in path_expr.find(self.ast):
            if match.value["name"] != "Assignment":
                continue
            yield _get_op_info(match.value)

    def get_void_calls(self):
        path_expr = parse('*..name.`parent`')
        for match in path_expr.find(self.ast):
            if match.value["name"] != "FunctionCall":
                continue
            function_identifier = match.value["childen"][0]
            function_typedef = function_identifier["attributes"]["type"]
            if "returns" in function_typedef:
                continue
            if "function" not in function_typedef:
                continue
            if "require" in function_identifier["attributes"]["value"]:
                continue
            yield (None, _get_src(match.value["src"]))

    def get_modifier_invocations(self):
        return []

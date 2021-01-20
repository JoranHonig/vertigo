import re
from typing import Dict
from eth_vertigo.test_runner.test_result import TestResult

swarm_hash_regex = re.compile("((a165)(.*)(5820)[a-f0-9]{64}(0029))$")

def strip_metadata(bytecode: str) -> str:
    return swarm_hash_regex.sub("", bytecode)


def normalize_mocha(mocha_json: dict) -> Dict[str, TestResult]:
    tests = {}
    for failure in mocha_json["failures"]:
        tests[failure["fullTitle"]] = TestResult(failure["title"], failure["fullTitle"], failure["duration"], False)
    for success in mocha_json["passes"]:
        tests[success["fullTitle"]] = TestResult(success["title"], success["fullTitle"], success["duration"], True)
    return tests
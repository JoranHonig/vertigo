import re
from typing import Dict
from eth_vertigo.test_runner.test_result import TestResult

swarm_hash_regex = re.compile("((a165)(.*)(5820)[a-f0-9]{64}(0029))$")

def strip_metadata(bytecode: str) -> str:
    return swarm_hash_regex.sub("", bytecode)


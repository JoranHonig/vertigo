from subprocess import Popen, run, getoutput,  PIPE
from typing import Optional
from tempfile import TemporaryFile
from time import sleep
from loguru import logger
DEFAULT_GANACHE_PARAMETERS = []  # ["--dbMemdown"]


class Ganache:
    def __init__(self, port, parameters, ganache_binary="ganache"):
        # Remove any pre-set port options
        self.parameters = parameters
        self.parameters.extend(["--port", str(port)])

        for param in DEFAULT_GANACHE_PARAMETERS:
            if param in self.parameters:
                continue
            self.parameters.append(param)

        self.ganache_binary = ganache_binary
        self.process = None  # type: Optional[subprocess.Popen]

    def start(self):
        if self.process is not None:
            raise ValueError("Process has already been terminated")

        self.process = Popen(
            [self.ganache_binary] + self.parameters,
            stderr=PIPE, stdout=PIPE
        )

        while True:
            line = self.process.stdout.readline()
            if "Listening on" in str(line):
                break

        if self.process.poll() is not None:
            raise Exception("Could not create ganache network")

    def stop(self):
        if self.process is None:
            raise ValueError("Process has not yet been started")
        if self.process.poll():
            raise ValueError("Process has already terminated")
        self.process.terminate()

import subprocess
from typing import Optional
DEFAULT_GANACHE_PARAMETERS = ["--dbMemdown"]


class Ganache:
    def __init__(self, ganache_binary="ganache", parameters=()):
        # Remove any pre-set port options
        self.parameters = [p for p in parameters if "--port" not in p]

        for param in DEFAULT_GANACHE_PARAMETERS:
            if param in self.parameters:
                continue
            self.parameters.append(param)

        self.ganache_binary = ganache_binary
        self.process = None  # type: Optional[subprocess.Popen]

    def start(self):
        if self.process is not None:
            raise ValueError("Process has already been terminated")

        self.process = subprocess.Popen(
            [self.ganache_binary] + self.parameters
        )

        if self.process.poll() is None:
            raise Exception("Could not create ganache network")

    def stop(self):
        if self.process is None:
            raise ValueError("Process has not yet been started")
        if self.process.poll() is None:
            raise ValueError("Process has already terminated")
        self.process.terminate()

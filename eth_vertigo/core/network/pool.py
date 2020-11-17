from abc import abstractmethod, ABC
from typing import Tuple, Callable, List, Dict


class Network:
    def __init__(self, name: str, port: int, provider=None):
        self.name = name
        self.port = port
        self.provider = provider


class NetworkPool(ABC):
    @abstractmethod
    def claim(self) -> str:
        pass

    @abstractmethod
    def yield_network(self, network: str):
        pass

    @property
    @abstractmethod
    def size(self):
        pass


class StaticNetworkPool(NetworkPool):
    def __init__(self, networks: List[str]):
        self.available_networks = list(networks)
        self.claimed_networks = []

    def claim(self) -> str:
        if not self.available_networks:
            raise ValueError("No network available")

        network = self.available_networks.pop()
        self.claimed_networks.append(network)

        return network

    def yield_network(self, network: str):
        if network not in self.claimed_networks:
            raise ValueError("Trying to yield unclaimed network")
        self.claimed_networks.remove(network)
        self.available_networks.append(network)

    @property
    def size(self):
        return len(self.available_networks) + len(self.claimed_networks)


class DynamicNetworkPool(NetworkPool):
    def __init__(self, networks: List[Tuple[str, int]], builder: Callable):
        self.available_networks = {n[0]: Network(n[0], n[1]) for n in networks}  # type: Dict
        self.claimed_networks = {}
        self.builder = builder

    def claim(self) -> str:
        if not self.available_networks:
            raise ValueError("No network available")

        # Claim one network from the available networks
        network = self.available_networks.pop(list(self.available_networks.keys())[0])

        # Put it in the claimed networks
        self.claimed_networks[network.name] = network
        network.provider = self.builder(network.port)

        # Spin up the dynamic network
        try:
            network.provider.start()
        except ValueError:
            raise

        return network.name

    def yield_network(self, network: str):
        if network not in self.claimed_networks:
            raise ValueError("Network not claimed")

        network = self.claimed_networks.pop(network)

        # Spin down the dynamic network
        try:
            network.provider.stop()
        except ValueError:
            raise

        # Yield the network back
        self.available_networks[network.name] = network


    @property
    def size(self):
        return len(self.available_networks) + len(self.claimed_networks)
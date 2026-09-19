from .containerlab import ContainerlabCollector
from .netmiko import NetmikoCollector


def get_collector_for_device(device):
    source = (device or {}).get("source")

    if source == "containerlab":
        return ContainerlabCollector()
    if source == "netmiko":
        return NetmikoCollector()
    return None

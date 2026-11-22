"""Read interface status from a Cisco IOS XE device over NETCONF (optional feature).

Owner: Abraham Y. Ileto
Branch: feature/device-status
"""

INTERFACES_FILTER = (
    '<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>'
)


def get_interface_status(host, port, username, password):
    """Return a list of (interface name, oper-status) tuples.

    Return an empty list if the device cannot be reached,
    so the stand-up still posts without device status.
    """
    raise NotImplementedError

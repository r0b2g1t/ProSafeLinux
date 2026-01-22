#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProSafeLinux CLI - Typer Implementation

Manage Netgear ProSafe Plus switches under Linux.
"""

import sys
from typing import Annotated, List, Optional

import typer

from psl_class import ProSafeLinux
import psl_typ

app = typer.Typer(
    name="psl-cli",
    help="Manage Netgear ProSafe Plus switches under Linux.",
    add_completion=False,
)

# Global state
class State:
    """Global state container for CLI options."""
    switch: ProSafeLinux = None
    interface: str = "eth0"
    debug: bool = False
    timeout: float = 0.1


state = State()


@app.callback()
def main(
    interface: Annotated[
        str,
        typer.Option("--interface", "-i", help="Network interface to use")
    ] = "eth0",
    debug: Annotated[
        bool,
        typer.Option("--debug", "-d", help="Enable debug output")
    ] = False,
    timeout: Annotated[
        float,
        typer.Option("--timeout", "-t", help="Timeout for switch commands")
    ] = 0.1,
):
    """
    Manage Netgear ProSafe Plus switches under Linux.
    """
    state.interface = interface
    state.debug = debug
    state.timeout = timeout
    state.switch = ProSafeLinux()
    state.switch.set_timeout(timeout)
    if debug:
        state.switch.set_debug_output()


def _bind_switch() -> bool:
    """Bind switch to interface. Returns False if binding fails."""
    if not state.switch.bind(state.interface):
        print("Interface has no addresses, cannot talk to switch")
        return False
    return True


@app.command()
def discover():
    """
    Search for ProSafe Plus switches in all subnets.
    """
    if not _bind_switch():
        raise typer.Exit(1)
    
    print("Searching for ProSafe Plus Switches ...\n")
    found = False
    for data in state.switch.discover():
        found = True
        for entry in data.keys():
            print(f"{entry.get_name()}: {data[entry]}")
        print("")

    if not found:
        print("No result received...")
        print("did you try to adjust your timeout?")


@app.command()
def exploit(
    mac: Annotated[
        str,
        typer.Option("--mac", "-m", help="Hardware address of the switch")
    ],
    new_password: Annotated[
        str,
        typer.Option("--new-password", "-p", help="New password to set")
    ],
):
    """
    Set a password without knowing the old one (exploit in 2012 firmware).
    """
    if not _bind_switch():
        raise typer.Exit(1)
    
    state.switch.passwd_exploit(mac, new_password)


@app.command()
def query(
    mac: Annotated[
        str,
        typer.Option("--mac", "-m", help="Hardware address of the switch")
    ],
    query_items: Annotated[
        List[str],
        typer.Argument(help="What to query for (use 'list' to see options, 'all' for everything)")
    ],
    passwd: Annotated[
        Optional[str],
        typer.Option("--passwd", "-p", help="Switch password")
    ] = None,
):
    """
    Query values from the switch.
    """
    if not _bind_switch():
        raise typer.Exit(1)
    
    # Get valid query commands
    valid_choices = [cmd.get_name() for cmd in state.switch.get_query_cmds()]
    valid_choices.append("all")
    
    # Handle "list" to show available options
    if "list" in query_items:
        print("Available query options:")
        for choice in sorted(valid_choices):
            print(f"  {choice}")
        raise typer.Exit(0)
    
    # Validate query items
    for item in query_items:
        if item not in valid_choices:
            print(f"Error: Invalid query option '{item}'")
            print(f"Valid options: {', '.join(sorted(valid_choices))}")
            raise typer.Exit(1)
    
    # Login if password provided
    if passwd is not None:
        login = {state.switch.CMD_PASSWORD: passwd}
        state.switch.transmit(login, mac)
    
    print("Query Values..\n")
    
    for qarg in query_items:
        if qarg == "all":
            for k in state.switch.get_query_cmds():
                if k != ProSafeLinux.CMD_VLAN_ID and k != ProSafeLinux.CMD_VLAN802_ID:
                    _query_single(mac, k)
        else:
            query_cmd = state.switch.get_cmd_by_name(qarg)
            _query_single(mac, query_cmd)


def _query_single(mac: str, query_cmd):
    """Query a single command from the switch."""
    switchdata = state.switch.query([query_cmd], mac)
    if switchdata is not False:
        if switchdata == {}:
            print(f"{query_cmd.get_name():<29} empty data received")
        else:
            for key in list(switchdata.keys()):
                if isinstance(key, psl_typ.PslTyp):
                    key.print_result(switchdata[key])
                else:
                    if state.debug:
                        print(f"-{key:<29}{switchdata[key]}")
    else:
        print(f"-- {query_cmd.get_name()} --")
        print("No result received...")
        print("did you try to adjust your timeout?")
    print("")


@app.command()
def query_raw(
    mac: Annotated[
        str,
        typer.Option("--mac", "-m", help="Hardware address of the switch")
    ],
    passwd: Annotated[
        Optional[str],
        typer.Option("--passwd", "-p", help="Switch password")
    ] = None,
):
    """
    Query raw values from the switch (including unknown commands).
    """
    if not _bind_switch():
        raise typer.Exit(1)
    
    print("QUERY DEBUG RAW")
    
    # Login if password provided
    if passwd is not None:
        login = {state.switch.CMD_PASSWORD: passwd}
        state.switch.transmit(login, mac)
    
    i = 0x0001
    while i < ProSafeLinux.CMD_END.get_id():
        query_cmd = [psl_typ.PslTypHex(i, f"Command {i}")]
        try:
            switchdata = state.switch.query(query_cmd, mac)
            found = None
            for qcmd in list(switchdata.keys()):
                if isinstance(qcmd, psl_typ.PslTyp):
                    if qcmd.get_id() == i:
                        found = qcmd

            if found is None:
                print(f"NON:{i:04x}:{'':<29}:{switchdata['raw']}")
            else:
                print(f"RES:{i:04x}:{switchdata[found]:<29}:{switchdata['raw']} ")
            if state.debug:
                for key in list(switchdata.keys()):
                    print(f"{i:x}-{key:<29}{switchdata[key]}")
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            print(f"ERR:{i:04x}:{sys.exc_info()[1]}")
        i = i + 1


@app.command(name="set")
def set_values(
    mac: Annotated[
        str,
        typer.Option("--mac", "-m", help="Hardware address of the switch")
    ],
    passwd: Annotated[
        str,
        typer.Option("--passwd", "-p", help="Switch password")
    ],
    # String settings
    name: Annotated[
        Optional[str],
        typer.Option("--name", help="Switch name")
    ] = None,
    location: Annotated[
        Optional[str],
        typer.Option("--location", help="Switch location")
    ] = None,
    # IP settings
    ip: Annotated[
        Optional[str],
        typer.Option("--ip", help="IP address")
    ] = None,
    netmask: Annotated[
        Optional[str],
        typer.Option("--netmask", help="Netmask")
    ] = None,
    gateway: Annotated[
        Optional[str],
        typer.Option("--gateway", help="Gateway")
    ] = None,
    # Password
    new_password: Annotated[
        Optional[str],
        typer.Option("--new-password", help="New password")
    ] = None,
    # DHCP
    dhcp: Annotated[
        Optional[str],
        typer.Option("--dhcp", help="DHCP setting (on/off)")
    ] = None,
    # Actions
    reboot: Annotated[
        bool,
        typer.Option("--reboot", help="Reboot the switch")
    ] = False,
    factory_reset: Annotated[
        bool,
        typer.Option("--factory-reset", help="Factory reset the switch")
    ] = False,
    reset_port_stat: Annotated[
        bool,
        typer.Option("--reset-port-stat", help="Reset port statistics")
    ] = False,
    # VLAN settings
    vlan_support: Annotated[
        Optional[str],
        typer.Option("--vlan-support", help="VLAN support mode (none/port/id/802.1q_id/802.1q_extended)")
    ] = None,
    vlan_id: Annotated[
        Optional[str],
        typer.Option("--vlan-id", help="VLAN ID settings: VLAN_ID:PORTS (e.g., '10:1,2,3')")
    ] = None,
    vlan802_id: Annotated[
        Optional[str],
        typer.Option("--vlan802-id", help="802.1Q VLAN: VLAN_ID:TAGGED_PORTS:UNTAGGED_PORTS (e.g., '20:1,7:2,3' or '20:7:' for only tagged)")
    ] = None,
    vlan_pvid: Annotated[
        Optional[str],
        typer.Option("--vlan-pvid", help="VLAN PVID: PORT:VLAN_ID (e.g., '1:10')")
    ] = None,
    # QoS settings
    qos: Annotated[
        Optional[str],
        typer.Option("--qos", help="QoS mode (port_based/802.1p)")
    ] = None,
    port_based_qos: Annotated[
        Optional[str],
        typer.Option("--port-based-qos", help="Port-based QoS: PORT:PRIORITY (e.g., '1:HIGH')")
    ] = None,
    # Bandwidth settings
    bandwidth_in: Annotated[
        Optional[str],
        typer.Option("--bandwidth-in", help="Incoming bandwidth limit: PORT:LIMIT (e.g., '1:512K')")
    ] = None,
    bandwidth_out: Annotated[
        Optional[str],
        typer.Option("--bandwidth-out", help="Outgoing bandwidth limit: PORT:LIMIT (e.g., '1:1M')")
    ] = None,
    broadcast_bandwidth: Annotated[
        Optional[str],
        typer.Option("--broadcast-bandwidth", help="Broadcast bandwidth limit: PORT:LIMIT (e.g., '1:NONE')")
    ] = None,
    # Port mirror
    port_mirror: Annotated[
        Optional[str],
        typer.Option("--port-mirror", help="Port mirroring: DST_PORT:SRC_PORTS (e.g., '1:2,3,4' or '0:0' to disable)")
    ] = None,
    # IGMP
    igmp_snooping: Annotated[
        Optional[str],
        typer.Option("--igmp-snooping", help="IGMP snooping (none or VLAN_ID)")
    ] = None,
    block_unknown_multicast: Annotated[
        Optional[str],
        typer.Option("--block-unknown-multicast", help="Block unknown multicast (on/off)")
    ] = None,
    igmp_header_validation: Annotated[
        Optional[str],
        typer.Option("--igmp-header-validation", help="IGMP header validation (on/off)")
    ] = None,
):
    """
    Set values on the switch.
    """
    if not _bind_switch():
        raise typer.Exit(1)
    
    switch = state.switch
    cmds = {ProSafeLinux.CMD_PASSWORD: passwd}
    
    # Map CLI options to switch commands
    option_map = {
        "name": (name, ProSafeLinux.CMD_NAME),
        "location": (location, ProSafeLinux.CMD_LOCATION),
        "ip": (ip, ProSafeLinux.CMD_IP),
        "netmask": (netmask, ProSafeLinux.CMD_NETMASK),
        "gateway": (gateway, ProSafeLinux.CMD_GATEWAY),
        "new_password": (new_password, ProSafeLinux.CMD_NEW_PASSWORD),
        "vlan_support": (vlan_support, ProSafeLinux.CMD_VLAN_SUPPORT),
        "qos": (qos, ProSafeLinux.CMD_QUALITY_OF_SERVICE),
        "igmp_snooping": (igmp_snooping, ProSafeLinux.CMD_IGMP_SNOOPING),
    }
    
    # Boolean options (on/off)
    boolean_map = {
        "dhcp": (dhcp, ProSafeLinux.CMD_DHCP),
        "block_unknown_multicast": (block_unknown_multicast, ProSafeLinux.CMD_BLOCK_UNKNOWN_MULTICAST),
        "igmp_header_validation": (igmp_header_validation, ProSafeLinux.CMD_IGMP_HEADER_VALIDATION),
    }
    
    # Action options
    action_map = {
        "reboot": (reboot, ProSafeLinux.CMD_REBOOT),
        "factory_reset": (factory_reset, ProSafeLinux.CMD_FACTORY_RESET),
        "reset_port_stat": (reset_port_stat, ProSafeLinux.CMD_RESET_PORT_STAT),
    }
    
    # Multi-arg options (comma-separated strings to lists)
    multi_arg_map = {
        "vlan_id": (vlan_id, ProSafeLinux.CMD_VLAN_ID, 2),
        "vlan802_id": (vlan802_id, ProSafeLinux.CMD_VLAN802_ID, 3),
        "vlan_pvid": (vlan_pvid, ProSafeLinux.CMD_VLANPVID, 2),
        "port_based_qos": (port_based_qos, ProSafeLinux.CMD_PORT_BASED_QOS, 2),
        "bandwidth_in": (bandwidth_in, ProSafeLinux.CMD_BANDWIDTH_INCOMING_LIMIT, 2),
        "bandwidth_out": (bandwidth_out, ProSafeLinux.CMD_BANDWIDTH_OUTGOING_LIMIT, 2),
        "broadcast_bandwidth": (broadcast_bandwidth, ProSafeLinux.CMD_BROADCAST_BANDWIDTH, 2),
        "port_mirror": (port_mirror, ProSafeLinux.CMD_PORT_MIRROR, 2),
    }
    
    # Process simple options
    for opt_name, (opt_val, cmd) in option_map.items():
        if opt_val is not None:
            cmds[cmd] = opt_val
    
    # Process boolean options
    for opt_name, (opt_val, cmd) in boolean_map.items():
        if opt_val is not None:
            cmds[cmd] = (opt_val.lower() == "on")
    
    # Process action options
    for opt_name, (opt_val, cmd) in action_map.items():
        if opt_val:
            cmds[cmd] = True
    
    # Process multi-arg options (parse colon-separated values)
    for opt_name, (opt_val, cmd, num_args) in multi_arg_map.items():
        if opt_val is not None:
            # Split by colon, preserving empty strings for trailing colons
            parts = opt_val.split(":", num_args - 1)
            if len(parts) < num_args:
                # Pad with empty strings if needed
                parts.extend([""] * (num_args - len(parts)))
            cmds[cmd] = parts
    
    # Verify data
    valid, errors = switch.verify_data(cmds)
    if not valid:
        for error in errors:
            print(error)
        raise typer.Exit(1)
    
    print("Changing Values..\n")
    result = switch.transmit(cmds, mac)
    if 'error' in result:
        print(f"FAILED: Error with {result['error']}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

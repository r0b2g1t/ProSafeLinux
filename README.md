# ProSafeLinux

Manage Netgear ProSafe Plus switches under Linux.

If your interface is **not** eth0 please specify it using the `--interface` option.

## Installation

```bash
pip install typer
```

Or with uv:

```bash
uv sync
```

## Usage

### Typer CLI (`psl_cli_typer.py`)

The recommended CLI uses [Typer](https://typer.tiangolo.com/) for a modern command-line experience.

#### Global Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--interface` | `-i` | Network interface to use | `eth0` |
| `--debug` | `-d` | Enable debug output | off |
| `--timeout` | `-t` | Timeout for switch commands | `0.1` |

#### Commands

**discover** - Search for ProSafe Plus switches in all subnets:

```bash
./psl_cli_typer.py discover
./psl_cli_typer.py --interface en0 discover
```

**query** - Query values from the switch:

```bash
# Query VLAN PVID for all ports
./psl_cli_typer.py query --mac B0:B9:8A:57:F6:56 vlan_pvid

# Query multiple items
./psl_cli_typer.py query --mac B0:B9:8A:57:F6:56 name ip netmask

# Query all available values
./psl_cli_typer.py query --mac B0:B9:8A:57:F6:56 --passwd "password" all
```

Available query items: `bandwidth_in`, `bandwidth_out`, `block_unknown_multicast`, `broadcast_bandwidth`, `dhcp`, `firmware_active`, `firmwarever`, `gateway`, `igmp_header_validation`, `igmp_snooping`, `ip`, `location`, `MAC`, `model`, `name`, `netmask`, `number_of_ports`, `port_based_qos`, `port_mirror`, `port_stat`, `qos`, `speed_stat`, `vlan802_id`, `vlan_pvid`, `vlan_id`, `vlan_support`, `all`

**set** - Set values on the switch:

```bash
# Set switch name
./psl_cli_typer.py set --mac B0:B9:8A:57:F6:56 --passwd "password" --name "MySwitch"

# Set 802.1Q VLAN PVID for port 4 to VLAN 1
./psl_cli_typer.py set --mac B0:B9:8A:57:F6:56 --passwd "password" --vlan-pvid "4:1"

# Set 802.1Q VLAN with tagged and untagged ports
./psl_cli_typer.py set --mac B0:B9:8A:57:F6:56 --passwd "password" --vlan802-id "20:1,7:2,3"

# Configure port mirroring (mirror ports 2,3,4 to port 1)
./psl_cli_typer.py set --mac B0:B9:8A:57:F6:56 --passwd "password" --port-mirror "1:2,3,4"

# Reboot the switch
./psl_cli_typer.py set --mac B0:B9:8A:57:F6:56 --passwd "password" --reboot
```

Set command options include: `--name`, `--location`, `--ip`, `--netmask`, `--gateway`, `--new-password`, `--dhcp`, `--reboot`, `--factory-reset`, `--reset-port-stat`, `--vlan-support`, `--vlan-id`, `--vlan802-id`, `--vlan-pvid`, `--qos`, `--port-based-qos`, `--bandwidth-in`, `--bandwidth-out`, `--broadcast-bandwidth`, `--port-mirror`, `--igmp-snooping`, `--block-unknown-multicast`, `--igmp-header-validation`

**query-raw** - Query raw values from the switch (for debugging):

```bash
./psl_cli_typer.py query-raw --mac B0:B9:8A:57:F6:56 --passwd "password"
```

**exploit** - Set a password without knowing the old one (exploit in 2012 firmware):

```bash
./psl_cli_typer.py exploit --mac B0:B9:8A:57:F6:56 --new-password "newpass"
```

### Legacy CLI (`psl-cli.py`)

The legacy CLI is still available:

```bash
./psl-cli.py --help
./psl-cli.py query --mac B0:B9:8A:57:F6:56 vlan_pvid
./psl-cli.py set --passwd "password" --mac B0:B9:8A:57:F6:56 --vlan_pvid 4 1
```


# Help wanted

Im sorry I am not active at this project anymore. It is open-source so perhabs you could find soneone who can help you.
 
I have found a security problem with this switch and was very disapointed in the answer from netgear. They need more than 6 Month to fix it and want the ethernet adress of it 
 
Because of this, I do not use this switch anymore.
 
If you can read german, please read this two articles:
 
http://www.linux-magazin.de/Blogs/Insecurity-Bulletin/Gastbeitrag-Security-by-Obscurity-bei-Netgear-Switches
http://www.linux-magazin.de/Ausgaben/2012/10/Switch
 
Please feel free to fork the code and do any push request.

Please contact me if you like to do the new maintainer of the projekt Sven Anders &lt;psl-github2013@sven.anders.im&gt;

# Other similar projects

https://github.com/Z3po/Netgearizer (We are merging code together.)

# Authors

* Asbjørn Sloth Tønnesen 
* Lars Dennis Renneberg Andersen
* Svenne Krap
* Shane Kerr
* Sven Anders

See also: http://git.asbjorn.biz/?p=gs105e.git;a=summary

It would be nice if you pay attribution to this project if you use this code.

If you like the projekt, you may [![Flattr this git repo](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=tabacha&url=https://github.com/tabacha/ProSafeLinux&title=ProSafeLinux&language=&tags=github&category=software)

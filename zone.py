import logging
from fortigate_api import FortiGateAPI
import requests

logging.getLogger().setLevel(logging.DEBUG)

# FortiGate connection details
HOST = "IP-Address"
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"
VDOM = "Test"  # Specify the VDOM name here

# Initialize FortiGateAPI with the specific VDOM
fgt = FortiGateAPI(
    host=HOST,
    username=USERNAME,
    password=PASSWORD,
    scheme="https",
    port=443,
    vdom=VDOM,  # Using VDOM in API configuration
    logging_error=True
)

def fetch_fortigate_interfaces(vdom):
    """Fetch interfaces from a specified VDOM in FortiGate API."""
    try:
        # Fetch interfaces with VDOM specified in the URL
        response = fgt.fortigate.get(url=f"api/v2/cmdb/system/interface?vdom={vdom}")
        if response.status_code != 200:
            logging.error(f"Failed to fetch interfaces for VDOM '{vdom}': HTTP {response.status_code} - {response.text}")
            return None
        return response.json().get("results", [])
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while fetching interfaces: {e}")
        return None

def convert_interface_to_juniper_cli(interface):
    """Convert FortiGate interface to Juniper CLI commands."""
    interface_name = interface.get("name", "")
    ip = interface.get("ip", "0.0.0.0/0")
    description = interface.get("description", "")
    vlan_id = interface.get("vlanid", None)
    
    # Start with interface configuration
    commands = [f"set interfaces {interface_name} unit 0 family inet address {ip}"]

    # Add description if available
    if description:
        commands.append(f"set interfaces {interface_name} description \"{description}\"")

    # Add VLAN configuration if applicable
    if vlan_id:
        commands.insert(0, f"set interfaces {interface_name} vlan-id {vlan_id}")
        commands.insert(0, f"set security zones security-zone {interface_name} interfaces {vlan_id}")
        
    return commands

def main():
    """Main function to fetch and convert FortiGate interfaces from VDOM to Juniper CLI commands."""
    # Fetch interfaces from the specified VDOM
    interfaces = fetch_fortigate_interfaces(VDOM)

    if interfaces is None:
        logging.error("No interfaces fetched. Exiting.")
        return

    # Convert each interface to Juniper CLI commands
    juniper_commands = []
    for interface in interfaces:
        juniper_commands.extend(convert_interface_to_juniper_cli(interface))

    # Output Juniper commands
    print("\n# Interface Configuration for VDOM:", VDOM)
    for cmd in juniper_commands:
        print(cmd)

if __name__ == "__main__":
    main()

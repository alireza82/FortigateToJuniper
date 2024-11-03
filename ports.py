import logging
from fortigate_api import FortiGateAPI
import requests

logging.getLogger().setLevel(logging.DEBUG)

# FortiGate connection details
HOST = "IP-Address"
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"

# Initialize FortiGateAPI
fgt = FortiGateAPI(
    host=HOST,
    username=USERNAME,
    password=PASSWORD,
    scheme="https",
    port=4444,
    vdom="Test",  # Adjust this for your specific VDOM
    logging_error=True
)

def fetch_fortigate_services():
    """Fetch services from FortiGate API and handle errors."""
    try:
        # Fetch FortiGate services from API
        response = fgt.fortigate.get(url="api/v2/cmdb/firewall.service/custom")
        print(response.json().get("results", []))
        if response.status_code != 200:
            logging.error(f"Failed to fetch services: HTTP {response.status_code} - {response.text}")
            return None

        return response.json().get("results", [])

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while fetching services: {e}")
        return None


def convert_fortigate_service_to_juniper(forti_service):
    """Convert a FortiGate service to Juniper CLI commands."""
    service_name = forti_service.get("name", "")
    protocol = forti_service.get("protocol", 6)  # Default to TCP (protocol number 6)
    tcp_portrange = forti_service.get("tcp-portrange", "")
    udp_portrange = forti_service.get("udp-portrange", "")

    # Determine Juniper protocol (6 = TCP, 17 = UDP)
    protocol_name = "tcp" if protocol == 6 else "udp" if protocol == 17 else ""

    # Generate Juniper CLI command for defining the service
    juniper_commands = []
    
    if protocol_name == "tcp" and tcp_portrange:
        # Handle TCP ports
        for port_range in tcp_portrange.split(','):
            juniper_commands.append(
                f'set applications application {service_name} protocol tcp destination-port {port_range.strip()}'
            )
    elif protocol_name == "udp" and udp_portrange:
        # Handle UDP ports
        for port_range in udp_portrange.split(','):
            juniper_commands.append(
                f'set applications application {service_name} protocol udp destination-port {port_range.strip()}'
            )
    else:
        juniper_commands.append(f'# Skipping unknown or unsupported protocol for {service_name}')

    
    return juniper_commands


def main():
    """Main function to fetch and convert FortiGate services to Juniper CLI commands."""
    # Fetch FortiGate services
    services = fetch_fortigate_services()

    if services is None:
        logging.error("No services fetched. Exiting.")
        return

    # Convert each service to Juniper CLI commands
    juniper_commands = []
    for service in services:
        service_commands = convert_fortigate_service_to_juniper(service)
        juniper_commands.extend(service_commands)

    # Output Juniper commands
    for cmd in juniper_commands:
        print(cmd)


if __name__ == "__main__":
    main()

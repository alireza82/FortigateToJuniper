import logging
from fortigate_api import FortiGateAPI

# Enable detailed logging for debugging purposes
logging.getLogger().setLevel(logging.DEBUG)

# FortiGate credentials and host
HOST = "IP-Address"
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"


# Initialize FortiGateAPI connection with custom parameters
fgt = FortiGateAPI(
    host=HOST,
    username=USERNAME,
    password=PASSWORD,
    scheme="https",
    port=443,  # Ensure that the FortiGate accepts API requests on this port
    vdom="Test",  # Virtual domain you're working in
    logging_error=True
)

# Optional: Login to the FortiGate device
fgt.login()

# Fetch firewall address objects from the CMDB API
try:
    response = fgt.fortigate.get(url="api/v2/cmdb/firewall/address")
    response.raise_for_status()  # Raises an error for bad HTTP responses
    

    # Parse the results
    result = response.json().get("results", [])
  

    # Function to convert FortiGate result to Juniper CLI format
    def convert_to_juniper_cli(forti_result, address_book):
        juniper_commands = []

        for address in forti_result:
            name = address.get("name", "unknown")
            address_type = address.get("type", "")
            
            # Determine the CLI format based on the address type
            if address_type == "ipmask":
                subnet = address.get("subnet", "")
                if subnet:
                    cmd = f'set security address-book {address_book} address {name} {subnet}'
                else:
                    cmd = f'# Skipping {name}, missing subnet value'
            elif address_type == "fqdn":
                fqdn = address.get("fqdn", "")
                if fqdn:
                    cmd = f'set security address-book {address_book} address {name} dns-name {fqdn}'
                else:
                    cmd = f'# Skipping {name}, missing FQDN value'
            elif address_type == "iprange":
                start_ip = address.get("start-ip", "")
                end_ip = address.get("end-ip", "")
                if start_ip and end_ip:
                    cmd = f'set security address-book {address_book} address {name} range-address {start_ip} to {end_ip}'
                else:
                    cmd = f'# Skipping {name}, missing IP range values'
            elif address_type == "geography":
                country = address.get("country", "")
                if country:
                    cmd = f'set security address-book {address_book} address {name} country {country}'
                else:
                    cmd = f'# Skipping {name}, missing country value'
            elif address_type == "dynamic-device":
                device_name = address.get("device-name", "")
                if device_name:
                    cmd = f'set security address-book {address_book} address {name} dynamic-address {device_name}'
                else:
                    cmd = f'# Skipping {name}, missing device name value'
            else:
                # Handle unknown or unsupported address types
                cmd = f'# Skipping unknown address type ({address_type}) for {name}'
            
            # Add comment if it exists
            comment = address.get("comment", "")
            if comment:
                cmd += f' description "{comment}"'
            
            juniper_commands.append(cmd)

        return juniper_commands

    # Convert FortiGate result to Juniper CLI commands
    address_book_name = "global"  # Adjust to your needs (could be a specific zone/address-book)
    juniper_cli_commands = convert_to_juniper_cli(result, address_book_name)

    # Print the Juniper CLI commands
    for cmd in juniper_cli_commands:
        print(cmd)

except Exception as e:
    logging.error(f"Error fetching firewall addresses: {e}")
    if response:
        logging.error(f"HTTP Response: {response.text}")

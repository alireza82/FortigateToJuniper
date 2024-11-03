import logging
from fortigate_api import FortiGateAPI
from datetime import datetime
# Enable logging
logging.basicConfig(level=logging.INFO)

# Initialize connection to FortiGate
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
    port=443,
    vdom="Test",  # Adjust this as needed for your specific VDOM
    logging_error=True
)

fgt.login()

# Get address groups from FortiGate
fortigate_schedules = fgt.cmdb.firewall.addrgrp.get()

# Convert FortiGate address groups to Juniper CLI commands
juniper_commands = []
for group in fortigate_schedules:
    # Start creating the Juniper CLI command
    group_name = group.get('name')
    members = group.get('member', [])
    
    # Juniper CLI for creating an address book group
    juniper_commands.append(f"set security address-book global address-set {group_name}")
    for member in members:
        member_name = member.get('name')
        juniper_commands.append(f"set security address-book global address-set {group_name} address {member_name}")

# Logout from FortiGate
fgt.logout()

# Print Juniper CLI commands
for command in juniper_commands:
    print(command)

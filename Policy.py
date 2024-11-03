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
    port=443,
    vdom="Test",  # Adjust this as needed for your specific VDOM
    logging_error=True
)

def fetch_fortigate_policies():
    """Fetch firewall policies from FortiGate API and handle errors."""
    try:
        response = fgt.fortigate.get(url="api/v2/cmdb/firewall/policy")

        # Check for non-200 status code (e.g., forbidden, not found, etc.)
        if response.status_code != 200:
            logging.error(f"Failed to fetch policies: HTTP {response.status_code} - {response.text}")
            return None
        
        # Return the result from the response
        return response.json().get("results", [])
    
    except requests.exceptions.ConnectionError:
        logging.error("Failed to connect to FortiGate device. Please check the host or network.")
        return None
    except requests.exceptions.Timeout:
        logging.error("Request to FortiGate API timed out.")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while fetching policies: {e}")
        return None

def convert_fortigate_rule_to_juniper(forti_policy):
    
    """Convert a FortiGate firewall rule to Juniper CLI commands."""
    try:
        juniper_commands = []
        
        # Extract rule information with default values for missing fields
        policy_id = forti_policy.get("policyid", "unknown")
        srcintf = forti_policy.get("srcintf", [{"name": "unknown"}])[0].get("name", "unknown")
        dstintf = forti_policy.get("dstintf", [{"name": "unknown"}])[0].get("name", "unknown")
        srcaddr = forti_policy.get("srcaddr", 'srcaddr')
        formatted_srcaddr = ' '.join(f'source-address {item["name"]}' for item in srcaddr)
        dstaddr = forti_policy.get("dstaddr", 'dstaddr')
        formatted_dstaddr = ' '.join(f'destination-address {item["name"]}' for item in dstaddr)
        service = forti_policy.get("service", "Unknown")
        formatted_services = ' '.join(f'application {item["name"]}' for item in service)
        action = forti_policy.get("action", "deny")
        logtraffic = forti_policy.get("logtraffic", "disable")
        status = forti_policy.get("status", "disable")
        schedule = forti_policy.get("schedule", "always")
        comments = forti_policy.get("comments", "")
        # Skip disabled rules
        if status == "disable":
            logging.info(f"Skipping policy {policy_id} (disabled)")
            return 

        # Create Juniper security policy commands
        cmd = f'set security policies from-zone {srcintf} to-zone {dstintf} policy policy-{policy_id}'
        cmd += f' match {formatted_srcaddr}'
        cmd += f' {formatted_dstaddr} '
        cmd += f' {formatted_services} '
        cleaned_comment = comments.replace("\n", " ") if comments else "NO-COMMENT"
        cmd += f'\nset security policies from-zone {srcintf} to-zone {dstintf} policy policy-{policy_id} description "{cleaned_comment}"'
        cmd += f'\nset security policies from-zone {srcintf} to-zone {dstintf} policy policy-{policy_id}'
        # Add scheduling if necessary
        if schedule != "always":
            cmd += f' scheduler-name  {schedule}'

        # Set action
        if action == "accept":
            cmd += ' then permit'
        else:
            cmd += ' then deny'

        # Enable logging if required
        cmd += f'\nset security policies from-zone {srcintf} to-zone {dstintf} policy policy-{policy_id} then '
        if logtraffic == "all":
            cmd += ' log session-init session-close'

       
        juniper_commands.append(cmd)
        return juniper_commands
    
    except KeyError as e:
        logging.error(f"Key error when processing policy {forti_policy.get('policyid', 'unknown')}: Missing {e}")
        return [f"# Error processing policy {forti_policy.get('policyid', 'unknown')} due to missing {e}"]

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return [f"# Error processing policy {forti_policy.get('policyid', 'unknown')} due to unexpected error"]

def main():
    """Main function to fetch and convert FortiGate policies to Juniper CLI commands."""
    # Fetch FortiGate firewall policies
    forti_policies = fetch_fortigate_policies()

    if forti_policies is None:
        logging.error("No policies fetched. Exiting.")
        return
    
    # Convert all FortiGate policies to Juniper CLI commands
    juniper_commands = []
    for policy in forti_policies:
        commands = convert_fortigate_rule_to_juniper(policy)
        if commands:
            juniper_commands.extend(commands)

    # Output Juniper commands
    
    for cmd in juniper_commands:
        print(cmd)
        with open('cmd.txt', 'a') as file:
         file.write(cmd+'\n')

if __name__ == "__main__":
    main()

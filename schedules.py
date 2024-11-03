import logging
from fortigate_api import FortiGateAPI
from datetime import datetime
# Enable logging
logging.basicConfig(level=logging.INFO)

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


try:
    # Log into the FortiGate
    fgt.login()

    # Fetch one-time schedules from FortiGate
    fortigate_schedules = fgt.cmdb.firewall_schedule.onetime.get()
    if not fortigate_schedules:
        logging.error("No schedules returned from FortiGate API.")
        exit()


    # Convert each FortiGate schedule to Juniper CLI format
    juniper_commands = []
    for schedule in fortigate_schedules:
        name = schedule["name"]
        start = schedule.get("start", "")
        end = schedule.get("end", "")

        # Convert to Juniper CLI command for one-time schedule
        if start and end:
            date_obj = datetime.strptime(start, "%H:%M %Y/%m/%d")
            formatted_date_start = date_obj.strftime("%Y-%m-%d.%H:%M")
            date_obj = datetime.strptime(end, "%H:%M %Y/%m/%d")
            formatted_date_end = date_obj.strftime("%Y-%m-%d.%H:%M")
            cmd = f'set schedulers scheduler  {name} start-date {formatted_date_start} stop-date "{formatted_date_end}"'
        else:
            cmd = f'# Skipping schedule {name} due to missing start or end time'

        juniper_commands.append(cmd)

    # Print or log the Juniper CLI commands
    for command in juniper_commands:
        print(command)

except Exception as e:
    logging.error(f"An error occurred: {e}")

finally:
    # Log out of the FortiGate
    fgt.logout()

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
    fortigate_schedules = fgt.cmdb.firewall_schedule.recurring.get()
    if not fortigate_schedules:
        logging.error("No schedules returned from FortiGate API.")
        exit()


    # Convert each FortiGate schedule to Juniper CLI format
    juniper_commands = []
    for schedule in fortigate_schedules:
        name = schedule["name"]
        start = schedule.get("start", "")
        end = schedule.get("end", "")
        day = schedule.get("day", "Unknown")
        days_array = day.split()
        daystring=''
        for day in days_array:
           daystring += f'set schedulers scheduler  {name} {day} start-time {start} stop-time {end}\n'
      

        juniper_commands.append(daystring)

    # Print or log the Juniper CLI commands
    for command in juniper_commands:
        print(command)

except Exception as e:
    logging.error(f"An error occurred: {e}")

finally:
    # Log out of the FortiGate
    fgt.logout()

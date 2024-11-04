
# FortiGate to Juniper Configuration Converter

## Overview
This tool connects to a FortiGate device using the `fortigate-api` library and retrieves configuration a specified VDOM and then converted into Juniper CLI commands to facilitate migration.

## Requirements

### Python Version
- Python 3.7 or higher

### Libraries
The following Python libraries are required:
- **fortigate-api**: For connecting and interacting with the FortiGate API.
- **requests**: For handling HTTP requests.
- **logging**: For error and process logging.

To install these dependencies, run:
```bash
pip install fortigate-api requests
```

## Setup
1. Clone the repository:
    ```bash
    git clone https://github.com/alireza82/FortigateToJuniper.git
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration
Update the FortiGate connection details in the script:
- `HOST`: IP address of the FortiGate device.
- `USERNAME`: Username for authentication.
- `PASSWORD`: Password for authentication.
- `VDOM`: The VDOM (Virtual Domain) name to fetch interfaces from.

## Usage
Run the script to fetch FortiGate configuration and convert them to Juniper CLI commands:
```bash
python converter.py
```

Upon successful execution, the Juniper CLI commands will be printed in the console, providing the equivalent configuration.



## Disclaimer
This tool is provided "as is" without any warranties, express or implied. The authors and contributors are not responsible for any potential damages or misconfigurations resulting from the use of this tool. It is recommended to review the generated configurations before applying them to any production environment.

## Blog
https://arabiyan.ir

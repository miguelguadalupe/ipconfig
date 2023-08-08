import subprocess
import platform
import re
from colorama import init, Fore, Style

# Initialize colorama
init()

def get_network_info():
    if platform.system().lower() not in ['linux', 'darwin']:
        raise OSError("This script is only compatible with Linux or macOS.")

    try:
        # Run 'ifconfig' command and capture the output
        ifconfig_output = subprocess.check_output(['ifconfig'])
        ifconfig_output = ifconfig_output.decode('utf-8')
        return ifconfig_output
    except subprocess.CalledProcessError as e:
        print("Error occurred while running ifconfig:", e)
        return ""

def get_default_gateway(interface):
    if platform.system().lower() == 'linux':
        try:
            ip_output = subprocess.check_output(['ip', 'route'])
        except subprocess.CalledProcessError as e:
            print("Error occurred while running ip:", e)
            return ""

        # Find the line with the specific interface
        for line in ip_output.decode('utf-8').splitlines():
            if 'default' in line and interface in line:
                default_gateway_match = re.search(r'via (\d+\.\d+\.\d+\.\d+)', line)
                if default_gateway_match:
                    return default_gateway_match.group(1)

        return "".format(interface)

    elif platform.system().lower() == 'darwin':
        try:
            netstat_output = subprocess.check_output(['netstat', '-rn'])
        except subprocess.CalledProcessError as e:
            print("Error occurred while running netstat:", e)
            return ""

        default_gateway_match = re.search(r'Default\s+(\d+\.\d+\.\d+\.\d+)\s+{}'.format(interface), netstat_output.decode('utf-8'))
        if default_gateway_match:
            return default_gateway_match.group(1)

    return "Default gateway not found."
def parse_network_info(ifconfig_output):
    interfaces_info = {}
    interface = None

    for line in ifconfig_output.splitlines():
        if 'flags=' in line:
            interface = line.split(':')[0].strip()
            interfaces_info[interface] = {}
        elif interface:
            ipv4_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)\s+netmask (\d+\.\d+\.\d+\.\d+)', line)
            ipv6_match = re.search(r'inet6 ([a-fA-F0-9:]+)', line)
            mac_match = re.search(r'ether (\S+)', line)

            if ipv4_match:
                interfaces_info[interface]['IPv4 Address'] = ipv4_match.group(1)
                interfaces_info[interface]['Subnet Mask'] = ipv4_match.group(2)
            if ipv6_match:
                interfaces_info[interface]['IPv6 Address'] = ipv6_match.group(1)
            if mac_match:
                interfaces_info[interface]['MAC Address'] = mac_match.group(1)

        # Get the default gateway for the current interface
        default_gateway = get_default_gateway(interface)
        if default_gateway:
            interfaces_info[interface]['Default Gateway'] = default_gateway

    return interfaces_info

def display_network_info(interfaces_info):
    print(Fore.GREEN + "Network Information:\n" + Style.RESET_ALL)

    for interface, info in interfaces_info.items():
        if 'IPv4 Address' in info or 'IPv6 Address' in info:
            print(Fore.BLUE + f"Interface: {interface}" + Style.RESET_ALL)
            for key, value in info.items():
                if key != 'Default Gateway':  # Omit displaying Default Gateway if not found
                    print(f"  {key}: {value}")
            if 'Default Gateway' in info:  # Only display Default Gateway if it is found
                print(f"  Default Gateway: {info['Default Gateway']}")
            print()

if __name__ == "__main__":
    network_info = get_network_info()
    if not network_info:
        print("Unable to retrieve network information.")
    else:
        parsed_info = parse_network_info(network_info)
        display_network_info(parsed_info)

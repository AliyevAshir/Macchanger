import subprocess
import re

def get_current_mac(interface):
    try:
        # Use netsh command for Windows
        ifconfig_result = subprocess.check_output(["netsh", "interface", "show", "interface"]).decode("utf-8")
        # Find the interface and extract the MAC address
        mac_address_search_result = re.search(r"Physical Address\s*:\s*([0-9A-Fa-f-]{17}|[0-9A-Fa-f]{12})", ifconfig_result)
        if mac_address_search_result:
            return mac_address_search_result.group(1)
        else:
            print("MAC address not found.")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def change_mac(interface, new_mac):
    try:
        print(f"Current MAC address for {interface}: {get_current_mac(interface)}")
        print(f"New MAC address for {interface}: {new_mac}")

        # Command to change the MAC address
        subprocess.call(["netsh", "interface", "set", "interface", interface, "newmac", new_mac])

        print("MAC address successfully changed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    interface = input("Enter the interface you want to change the MAC address for (e.g., Ethernet): ")
    new_mac = input("Enter the new MAC address (e.g., 00:1A:2B:3C:4D:5E): ")
    change_mac(interface, new_mac)

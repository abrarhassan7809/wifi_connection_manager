# import tkinter as tk
# import subprocess
#
# def scan_networks():
#     cmd = "nmcli -f SSID device wifi list"
#     process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     output, _ = process.communicate()
#     output = output.decode("utf-8")
#     available_networks = output.split('\n')[1:]
#     network_listbox.delete(0, tk.END)
#     for network in available_networks:
#         network_listbox.insert(tk.END, network)
#
# def connect_to_network():
#     selected_index = network_listbox.curselection()
#     if selected_index:
#         selected_network = network_listbox.get(selected_index)
#         selected_network = selected_network.strip()  # Remove trailing whitespace
#         cmd = f"nmcli device wifi connect '{selected_network}' password ''"
#         subprocess.run(cmd, shell=True)
#
# # Create the Tkinter window
# window = tk.Tk()
# window.title("Wi-Fi Network Scanner")
# window.geometry("300x400")
#
# # Create the Scan button
# scan_button = tk.Button(window, text="Scan Wi-Fi", command=scan_networks)
# scan_button.pack()
#
# # Create and populate the network listbox
# network_listbox = tk.Listbox(window)
# network_listbox.pack()
#
# # Create the Connect button
# connect_button = tk.Button(window, text="Connect", command=connect_to_network)
# connect_button.pack()
#
# # Start the Tkinter event loop
# window.mainloop()

# ========================
import nmap


def get_connected_devices():
    # Create a new instance of the PortScanner object
    nm = nmap.PortScanner()

    # Scan the network to retrieve connected devices
    nm.scan(hosts='192.168.0.0/24', arguments='-sn')

    # Get the list of connected devices
    connected_devices = []
    for host in nm.all_hosts():
        if 'mac' in nm[host]['addresses']:
            ip = nm[host]['addresses']['ipv4']
            mac = nm[host]['addresses']['mac']
            connected_devices.append((ip, mac))

    return connected_devices


# Call the function to get the connected devices
devices = get_connected_devices()

# Print the IP addresses of connected devices
for device in devices:
    print("IP Address:", device[0])

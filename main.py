import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog

root = tk.Tk()
root.withdraw()


def connect_to_network(network):
    password = simpledialog.askstring("WiFi Password", f"Enter password for {network}")
    if password:
        cmd = ["nmcli", "dev", "wifi", "connect", network, "password", password]
        result = subprocess.run(cmd, capture_output=True, text=True)
        previous_network = get_connected_network()
        if result.returncode == 0:
            current_network = get_connected_network()
            if current_network == network:
                messagebox.showinfo("Connection Status", f"Connected to {current_network}")
                root.quit()
            else:
                messagebox.showerror("Connection Status", f"Failed to connect to {network}")
                root.quit()
        else:
            messagebox.showerror("Connection Status", "Invalid password.")
            root.quit()
    else:
        messagebox.showwarning("Connection Status", "Password not provided.")
        root.quit()


def get_connected_network():
    output = subprocess.run(["nmcli", "-t", "-f", "NAME", "connection", "show", "--active"], capture_output=True,
                            text=True)
    connected_network = output.stdout.strip()
    return connected_network


def get_wifi_networks():
    if subprocess.run(["which", "nmcli"], capture_output=True).returncode == 0:
        # For Linux
        output = subprocess.run(["nmcli", "-f", "SSID", "dev", "wifi"], capture_output=True, text=True)
        networks = output.stdout.splitlines()[2:]
        return [network.strip() for network in networks]
    elif subprocess.run(["which", "airport"], capture_output=True).returncode == 0:
        # For macOS
        output = subprocess.run(["airport", "-s"], capture_output=True, text=True)
        networks = output.stdout.splitlines()[1:]
        return [network.split()[1] for network in networks]
    elif subprocess.run(["which", "netsh"], capture_output=True).returncode == 0:
        # For Windows
        output = subprocess.run(["netsh", "wlan", "show", "networks"], capture_output=True, text=True)
        networks = output.stdout.splitlines()
        return [network.split(":")[1].strip() for network in networks if "SSID" in network]
    else:
        messagebox.showerror("Error", "Unsupported operating system.")
        return []


wifi_networks = get_wifi_networks()

if wifi_networks:
    selected_network = messagebox.askquestion("WiFi Networks", "Click 'Yes' to connect to a network.")
    if selected_network == 'yes':
        root = tk.Tk()
        root.title("WiFi Networks")
        root.geometry("500x600")

        # Create buttons for each network
        for network in wifi_networks:
            btn = tk.Button(root, text=network, command=lambda network=network: [root.destroy(), connect_to_network(network)])
            btn.pack(pady=5)

        root.mainloop(1)
else:
    messagebox.showinfo("WiFi Networks", "No WiFi networks found.")

# ======second-method=========
# import platform
# import subprocess
# import tkinter as tk
# import tkinter.messagebox as messagebox
# import wifi
# import re
#
#
# # Platform-specific imports
# if platform.system() == 'Linux':
#     wifi_interface = 'wlan0'  # Update the interface name for Linux
# elif platform.system() == 'Windows':
#     wifi_interface = 'Wi-Fi'  # Update the interface name for Windows
# elif platform.system() == 'Darwin':  # macOS
#     wifi_interface = 'en0'  # Update the interface name for macOS
#
#
# def scan_wifi():
#     wifi_list.delete(0, tk.END)  # Clear the listbox
#     if platform.system() == 'Linux':
#         cmd = ['nmcli', '-t', '-f', 'SSID', 'dev', 'wifi', 'list']
#         try:
#             output = subprocess.check_output(cmd, text=True)
#             networks = output.strip().split('\n')
#             for network in networks:
#                 wifi_list.insert(tk.END, network)
#         except subprocess.CalledProcessError:
#             messagebox.showerror("Error", "Failed to scan WiFi networks.")
#     elif platform.system() == 'Darwin':
#         cmd = ['networksetup', '-listallhardwareports']
#         try:
#             output = subprocess.check_output(cmd, text=True)
#             interfaces = re.findall(r'Hardware Port: (.*?)\nDevice: (.*?)\n', output)
#             for _, interface in interfaces:
#                 cmd = ['airport', '-s', '-I', interface]
#                 output = subprocess.check_output(cmd, text=True)
#                 networks = output.strip().split('\n')[1:]
#                 for network in networks:
#                     ssid = network.split()[1]
#                     wifi_list.insert(tk.END, ssid)
#         except subprocess.CalledProcessError:
#             messagebox.showerror("Error", "Failed to scan WiFi networks.")
#     elif platform.system() == 'Windows':
#         cmd = ['netsh', 'wlan', 'show', 'networks']
#         try:
#             output = subprocess.check_output(cmd, text=True)
#             networks = re.findall(r'SSID\s+:\s(.*?)\r', output)
#             for network in networks:
#                 wifi_list.insert(tk.END, network)
#         except subprocess.CalledProcessError:
#             messagebox.showerror("Error", "Failed to scan WiFi networks.")
#     else:
#         messagebox.showerror("Error", "Unsupported operating system.")
#
#
# def connect_wifi():
#     selected_index = wifi_list.curselection()
#     if selected_index:
#         selected_ssid = wifi_list.get(selected_index)
#         password = password_entry.get()
#
#         if platform.system() == 'Linux':
#             try:
#                 cmd = ['nmcli', 'dev', 'wifi', 'connect', selected_ssid, 'password', password]
#                 subprocess.run(cmd, check=True)
#
#                 # Check the currently connected SSID
#                 output = subprocess.check_output(['nmcli', '-t', '-f', 'NAME', 'connection', 'show', '--active'],
#                                                  text=True)
#                 connected_ssid = output.strip()
#
#                 if connected_ssid == selected_ssid:
#                     messagebox.showinfo("Connection Status", f"Connected to {selected_ssid}")
#                 else:
#                     messagebox.showerror("Error",
#                                          f"Failed to connect to {selected_ssid}.")
#             except subprocess.CalledProcessError:
#                 messagebox.showerror("Error", "Failed to connect to the network")
#         elif platform.system() == 'Windows':
#             try:
#                 subprocess.run(["netsh", "wlan", "connect", "name", f'"{selected_ssid}"', "password", f'"{password}"'],
#                                check=True)
#                 messagebox.showinfo("Connection Status", f"Connected to {selected_ssid}")
#             except subprocess.CalledProcessError:
#                 messagebox.showerror("Error", "Failed to connect to the network")
#         elif platform.system() == 'Darwin':  # macOS
#             try:
#                 subprocess.run(["networksetup", "-setairportnetwork", wifi_interface, selected_ssid, password],
#                                check=True)
#                 messagebox.showinfo("Connection Status", f"Connected to {selected_ssid}")
#             except subprocess.CalledProcessError:
#                 messagebox.showerror("Error", "Failed to connect to the network")
#     else:
#         messagebox.showwarning("Warning", "No network selected")
#
#
# def disconnect_wifi():
#     if platform.system() == 'Linux':
#         try:
#             # Disable the interface
#             subprocess.run(['nmcli', 'dev', 'disconnect', wifi_interface], check=True)
#
#             # Remove the saved Wi-Fi connection profile
#             wifi.Scheme.delete(wifi_interface)
#
#             messagebox.showinfo("Connection Status", "Permanently disconnected from the network")
#         except subprocess.CalledProcessError:
#             messagebox.showerror("Error", "Failed to disconnect from the network")
#     elif platform.system() == 'Windows':
#         try:
#             # Disable the interface
#             subprocess.run(['netsh', 'interface', 'set', 'interface', wifi_interface, 'admin=disable'], check=True)
#
#             # Remove the saved Wi-Fi connection profile
#             subprocess.run(['netsh', 'wlan', 'delete', 'profile', 'name=', wifi_interface], check=True)
#
#             messagebox.showinfo("Connection Status", "Permanently disconnected from the network")
#         except subprocess.CalledProcessError:
#             messagebox.showerror("Error", "Failed to disconnect from the network")
#     elif platform.system() == 'Darwin':  # macOS
#         try:
#             # Disable the interface
#             subprocess.run(["networksetup", "-setairportpower", wifi_interface, "off"], check=True)
#
#             # Remove the saved Wi-Fi connection profile
#             subprocess.run(["networksetup", "-removepreferredwirelessnetwork", wifi_interface, wifi_interface], check=True)
#
#             messagebox.showinfo("Connection Status", "Permanently disconnected from the network")
#         except subprocess.CalledProcessError:
#             messagebox.showerror("Error", "Failed to disconnect from the network")
#
#
# # Create the main window
# root = tk.Tk()
# root.title("WiFi Connection Manager")
#
# # Create and pack the widgets
# scan_button = tk.Button(root, text="Scan", command=scan_wifi)
# scan_button.pack(pady=10)
#
# wifi_list = tk.Listbox(root, selectmode=tk.SINGLE)
# wifi_list.pack()
#
# password_label = tk.Label(root, text="Password:")
# password_label.pack()
#
# password_entry = tk.Entry(root, show="*")
# password_entry.pack()
#
# connect_button = tk.Button(root, text="Connect", command=connect_wifi)
# connect_button.pack(pady=10)
#
# disconnect_button = tk.Button(root, text="Disconnect", command=disconnect_wifi)
# disconnect_button.pack(pady=10)
#
# # Start the main event loop
# root.mainloop()

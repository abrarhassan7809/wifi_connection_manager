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
        if result.returncode == 0:
            messagebox.showinfo("Connection Status", f"Connected to {network}")
            root.quit()
        else:
            messagebox.showerror("Connection Status", "Invalid password.")
            root.quit()
    else:
        messagebox.showwarning("Connection Status", "Password not provided.")
        root.quit()


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
        root.geometry("300x200")

        # Create buttons for each network
        for network in wifi_networks:
            btn = tk.Button(root, text=network, command=lambda network=network: connect_to_network(network))
            btn.pack(pady=5)

        root.mainloop(1)
else:
    messagebox.showinfo("WiFi Networks", "No WiFi networks found.")

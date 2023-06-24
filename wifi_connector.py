import platform
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, Scrollbar

root = tk.Tk()
root.withdraw()


def check_wifi_connection():
    output = subprocess.run(["nmcli", "-t", "-f", "NAME", "connection", "show", "--active"], capture_output=True, text=True)
    connected_network = output.stdout.strip()
    if connected_network:
        return True
    else:
        return False


def connect_to_network(network):
    current_network = get_connected_network()
    saved_networks = get_saved_networks()

    if current_network == network:
        messagebox.showinfo("Connection Status", f"Already connected to {current_network}")
        return
    elif network in saved_networks:
        connect_without_password(network, current_network)
    else:
        password = simpledialog.askstring("WiFi Password", f"Enter password for {network}")
        if password:
            connect_with_password(network, current_network, password)
        else:
            messagebox.showwarning("Connection Status", "Password not provided.")

    connected_network = get_connected_network()
    if connected_network == network:
        messagebox.showinfo("Connection Status", f"Connected to {network}")
    elif connected_network:
        messagebox.showinfo("Connection Status", f"Connected to {connected_network}")
    else:
        messagebox.showerror("Connection Status", f"Failed to connect {network}")
        return
    scan_wifi_networks()


def connect_without_password(network, current_network):
    cmd = ["nmcli", "dev", "wifi", "connect", network]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        if current_network == network:
            messagebox.showinfo("Connection Status", f"Connected to {current_network}")
    else:
        messagebox.showerror("Connection Status", "Failed to connect.")
        return


def connect_with_password(network, current_network, password):
    cmd = ["nmcli", "dev", "wifi", "connect", network, "password", password]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        if current_network == network:
            messagebox.showinfo("Connection Status", f"Connected to {current_network}")
    else:
        messagebox.showerror("Connection Status", "Invalid password.")


def get_connected_network():
    output = subprocess.run(["nmcli", "-t", "-f", "NAME", "connection", "show", "--active"], capture_output=True, text=True)
    connected_network = output.stdout.strip()
    return connected_network


def get_saved_networks():
    output = subprocess.run(["nmcli", "-t", "-f", "NAME", "connection", "show"], capture_output=True, text=True)
    saved_networks = output.stdout.splitlines()
    return [network.strip() for network in saved_networks if network.strip() != ""]


def get_wifi_networks():
    current_os = platform.system()
    if current_os == 'Linux':
        if subprocess.run(["which", "nmcli"], capture_output=True).returncode == 0:
            output = subprocess.run(["nmcli", "-f", "SSID", "dev", "wifi"], capture_output=True, text=True)
            networks = output.stdout.splitlines()[1:]
            return [network.strip() for network in networks if network.strip()]
        elif subprocess.run(["which", "iwlist"], capture_output=True).returncode == 0:
            output = subprocess.run(["iwlist", "wlan0", "scan"], capture_output=True, text=True)
            networks = [line.strip() for line in output.stdout.splitlines() if "ESSID:" in line]
            return [network.split(":")[1].strip().strip('"') for network in networks]
        else:
            print("Neither nmcli nor iwlist command found.")
            return []

    elif current_os == 'Darwin':
        if subprocess.run(["which", "airport"], capture_output=True).returncode == 0:
            output = subprocess.run(["airport", "-s"], capture_output=True, text=True)
            networks = output.stdout.splitlines()[1:]
            return [network.split()[0] for network in networks]
        else:
            print("airport command not found.")
            return []

    elif current_os == 'Windows':
        if subprocess.run(["which", "netsh"], capture_output=True).returncode == 0:
            output = subprocess.run(["netsh", "wlan", "show", "networks"], capture_output=True, text=True)
            networks = output.stdout.splitlines()
            ssid_index = networks[0].index("SSID")
            return [network[ssid_index + 5:].strip() for network in networks[1:] if "SSID" in network]
        else:
            print("netsh command not found.")
            return []

    else:
        print("Unsupported operating system.")
        return []


def scan_wifi_networks():
    wifi_networks = get_wifi_networks()
    listbox.delete(0, tk.END)

    if wifi_networks:
        for network in wifi_networks:
            listbox.insert(tk.END, network)
    else:
        messagebox.showinfo("WiFi Networks", "No WiFi networks found.")


def on_select():
    selected_index = listbox.curselection()
    if selected_index:
        selected_network = listbox.get(selected_index[0])
        connect_to_network(selected_network)
    else:
        messagebox.showwarning("Connection Status", "Please select a Wi-Fi network.")


def forget_password(network):
    cmd = ["nmcli", "connection", "delete", network]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        messagebox.showwarning("Connection Status", f"Forgot Wi-Fi network: {network}")
    else:
        messagebox.showerror("Connection Status", "Not connected to the Wi-Fi network.")


def on_forget_password():
    selected_index = listbox.curselection()
    if selected_index:
        selected_network = listbox.get(selected_index[0])
        forget_password(selected_network)
    else:
        messagebox.showwarning("Connection Status", "Please select a Wi-Fi network.")


wifi_networks = get_wifi_networks()

if not wifi_networks:
    selected_network = messagebox.askquestion("WiFi Networks", "Click 'Yes' to connect to a network.")
    if selected_network == 'yes':
        root = tk.Tk()
        root.title("WiFi Networks")

        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.geometry(f"{width}x{height}+0+0")

        scrollbar = Scrollbar(root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = Listbox(root, yscrollcommand=scrollbar.set)
        listbox.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=listbox.yview)

        if wifi_networks:
            for network in wifi_networks:
                listbox.insert(tk.END, network)

        scan_button = tk.Button(root, text="Scan", command=scan_wifi_networks)
        scan_button.pack(side=tk.LEFT, pady=5)

        connect_button = tk.Button(root, text="Connect", command=on_select)
        connect_button.pack(side=tk.LEFT, pady=5)

        forget_button = tk.Button(root, text="Forgot Password", command=on_forget_password)
        forget_button.pack(side=tk.LEFT, pady=5)

        root.mainloop(1)
else:
    messagebox.showinfo("WiFi Networks", "Already connected WiFi networks")


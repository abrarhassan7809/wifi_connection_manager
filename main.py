import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, Scrollbar

root = tk.Tk()
root.withdraw()


def connect_to_network(network):
    current_network = get_connected_network()
    print(current_network)
    saved_networks = get_saved_networks()

    if current_network == network:
        messagebox.showwarning("Connection Status", f"Already connected to {current_network}")
    elif network in saved_networks:
        connect_without_password(network, current_network)
    else:
        password = simpledialog.askstring("WiFi Password", f"Enter password for {network}")
        if password:
            connect_with_password(network, current_network, password)
        else:
            messagebox.showwarning("Connection Status", "Password not provided.")


def connect_without_password(network, current_network):
    print(f'without: {current_network} network: {network}')
    cmd = ["nmcli", "dev", "wifi", "connect", network]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        if current_network == network:
            messagebox.showinfo("Connection Status", f"Connected to {network}")
        else:
            messagebox.showinfo("Connection Status", f"Connected to {current_network}")
    else:
        messagebox.showerror("Connection Status", "Failed to connect.")


def connect_with_password(network, current_network, password):
    print(f'password: {current_network}')
    cmd = ["nmcli", "dev", "wifi", "connect", network, "password", password]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        if current_network == network:
            messagebox.showinfo("Connection Status", f"Connected to {network}")
        else:
            messagebox.showinfo("Connection Status", f"Connected to {current_network}")
    else:
        messagebox.showerror("Connection Status", "Invalid password.")


def forget_password(network):
    cmd = ["nmcli", "connection", "delete", network]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        messagebox.showinfo("Connection Status", f"Forget Wi-Fi network: {network}")
    else:
        messagebox.showerror("Connection Status", "Failed to forget password.")


def get_connected_network():
    output = subprocess.run(["nmcli", "-t", "-f", "NAME", "connection", "show", "--active"], capture_output=True,
                            text=True)
    connected_network = output.stdout.strip()
    return connected_network


def get_saved_networks():
    output = subprocess.run(["nmcli", "-t", "-f", "NAME", "connection", "show"], capture_output=True, text=True)
    saved_networks = output.stdout.splitlines()
    return [network.strip() for network in saved_networks if network.strip() != ""]


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


def scan_wifi_networks():
    wifi_networks = get_wifi_networks()
    listbox.delete(0, tk.END)  # Clear the listbox

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


def on_forget_password():
    selected_index = listbox.curselection()
    if selected_index:
        selected_network = listbox.get(selected_index[0])
        if selected_network == get_connected_network():
            current_network = selected_network
            password = simpledialog.askstring("WiFi Password", f"Enter password for {selected_network}")
            if password:
                connect_with_password(selected_network, current_network, password)
            else:
                messagebox.showwarning("Connection Status", "Password not provided.")
        else:
            forget_password(selected_network)

    else:
        messagebox.showwarning("Connection Status", "Please select a Wi-Fi network.")


wifi_networks = get_wifi_networks()

if wifi_networks:
    selected_network = messagebox.askquestion("WiFi Networks", "Click 'Yes' to connect to a network.")
    if selected_network == 'yes':
        root = tk.Tk()
        root.title("WiFi Networks")
        root.geometry("600x600")

        scrollbar = Scrollbar(root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = Listbox(root, yscrollcommand=scrollbar.set)
        listbox.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=listbox.yview)

        # Populate listbox with Wi-Fi networks
        if wifi_networks:
            for network in wifi_networks:
                listbox.insert(tk.END, network)

        scan_button = tk.Button(root, text="Scan", command=scan_wifi_networks)
        scan_button.pack(pady=5)

        connect_button = tk.Button(root, text="Connect", command=on_select)
        connect_button.pack(pady=5)

        forget_button = tk.Button(root, text="Forget Password", command=on_forget_password)
        forget_button.pack(pady=5)

        root.mainloop(1)
else:
    messagebox.showinfo("WiFi Networks", "No WiFi networks found.")

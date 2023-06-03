import platform
import subprocess
import tkinter as tk
import tkinter.messagebox as messagebox
import re

# Platform-specific imports
if platform.system() == 'Linux':
    wifi_interface = 'wlan0'  # Update the interface name for Linux
elif platform.system() == 'Windows':
    wifi_interface = 'Wi-Fi'  # Update the interface name for Windows
elif platform.system() == 'Darwin':  # macOS
    wifi_interface = 'en0'  # Update the interface name for macOS

previous_ssid_file = "previous_ssid.txt"  # File to store the previous SSID


def scan_wifi():
    wifi_list.delete(0, tk.END)  # Clear the listbox
    if platform.system() == 'Linux':
        cmd = ['nmcli', '-t', '-f', 'SSID', 'dev', 'wifi', 'list']
        try:
            output = subprocess.check_output(cmd, text=True)
            networks = output.strip().split('\n')
            for network in networks:
                wifi_list.insert(tk.END, network)
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to scan WiFi networks.")
    elif platform.system() == 'Darwin':
        cmd = ['networksetup', '-listallhardwareports']
        try:
            output = subprocess.check_output(cmd, text=True)
            interfaces = re.findall(r'Hardware Port: (.*?)\nDevice: (.*?)\n', output)
            for _, interface in interfaces:
                cmd = ['airport', '-s', '-I', interface]
                output = subprocess.check_output(cmd, text=True)
                networks = output.strip().split('\n')[1:]
                for network in networks:
                    ssid = network.split()[1]
                    wifi_list.insert(tk.END, ssid)
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to scan WiFi networks.")
    elif platform.system() == 'Windows':
        cmd = ['netsh', 'wlan', 'show', 'networks']
        try:
            output = subprocess.check_output(cmd, text=True)
            networks = re.findall(r'SSID\s+:\s(.*?)\r', output)
            for network in networks:
                wifi_list.insert(tk.END, network)
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to scan WiFi networks.")
    else:
        messagebox.showerror("Error", "Unsupported operating system.")


def on_wifi_select(event):
    # Clear the password entry field
    password_entry.delete(0, tk.END)

    # Get the selected Wi-Fi network
    selected_index = wifi_list.curselection()
    if selected_index:
        selected_ssid = wifi_list.get(selected_index)

        connected_ssid = None
        previous_ssid = None

        if platform.system() == 'Linux':
            try:
                # Check the currently connected SSID
                output = subprocess.check_output(['nmcli', '-t', '-f', 'NAME', 'connection', 'show', '--active'],
                                                 text=True)
                connected_ssid = output.strip()
            except subprocess.CalledProcessError:
                pass
        elif platform.system() == 'Darwin':
            try:
                output = subprocess.check_output(['networksetup', '-getairportnetwork', wifi_interface], text=True)
                connected_ssid = re.findall(r'Current Wi-Fi Network: (.+)', output)[0]
            except subprocess.CalledProcessError:
                pass
        elif platform.system() == 'Windows':
            try:
                output = subprocess.check_output(['netsh', 'wlan', 'show', 'interface'], text=True)
                match = re.search(r'SSID\s+: (.+)', output)
                if match:
                    connected_ssid = match.group(1)
            except subprocess.CalledProcessError:
                pass

        if platform.system() == 'Windows':
            # Retrieve the previous connected SSID from the file
            try:
                with open(previous_ssid_file, 'r') as file:
                    previous_ssid = file.read().strip()
            except FileNotFoundError:
                pass

        if connected_ssid == selected_ssid or previous_ssid == selected_ssid:
            # Disable the password entry field if already connected or previously connected
            password_entry.config(state=tk.DISABLED)
        else:
            # Enable the password entry field for non-connected networks
            password_entry.config(state=tk.NORMAL)


def connect_wifi():
    selected_index = wifi_list.curselection()
    if selected_index:
        selected_ssid = wifi_list.get(selected_index)

        password = password_entry.get()

        if not password:
            messagebox.showerror("Error", "Please enter the password for the selected network.")
            return

        if platform.system() == 'Linux':
            try:
                cmd = ['nmcli', 'dev', 'wifi', 'connect', selected_ssid, 'password', password]
                subprocess.run(cmd, check=True)

                # Check the currently connected SSID
                output = subprocess.check_output(['nmcli', '-t', '-f', 'NAME', 'connection', 'show', '--active'],
                                                 text=True)
                connected_ssid = output.strip()

                if connected_ssid == selected_ssid:
                    messagebox.showinfo("Connection Status", f"Connected to {selected_ssid}")

                    # Store the connected SSID in the file
                    with open(previous_ssid_file, 'w') as file:
                        file.write(selected_ssid)
                else:
                    messagebox.showerror("Error", f"Failed to connect to {selected_ssid}.")
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", "Failed to connect to the network")
        elif platform.system() == 'Windows':
            try:
                subprocess.run(["netsh", "wlan", "connect", "name", f'"{selected_ssid}"', "password", f'"{password}"'],
                               check=True)
                messagebox.showinfo("Connection Status", f"Connected to {selected_ssid}")

                # Store the connected SSID in the file
                with open(previous_ssid_file, 'w') as file:
                    file.write(selected_ssid)
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", "Failed to connect to the network")
        elif platform.system() == 'Darwin':  # macOS
            try:
                subprocess.run(["networksetup", "-setairportnetwork", wifi_interface, selected_ssid, password],
                               check=True)
                messagebox.showinfo("Connection Status", f"Connected to {selected_ssid}")

                # Store the connected SSID in the file
                with open(previous_ssid_file, 'w') as file:
                    file.write(selected_ssid)
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", "Failed to connect to the network")
    else:
        messagebox.showwarning("Warning", "No network selected")


def forget_wifi():
    selected_index = wifi_list.curselection()
    if selected_index:
        selected_ssid = wifi_list.get(selected_index)

        if platform.system() == 'Linux':
            try:
                # Remove the saved Wi-Fi connection profile
                subprocess.run(['nmcli', 'connection', 'delete', 'id', selected_ssid], check=True)

                messagebox.showinfo("Network Status", f"Forgotten Wi-Fi network: {selected_ssid}")
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", f"Failed to forget Wi-Fi network: {selected_ssid}")
        elif platform.system() == 'Windows':
            try:
                # Remove the saved Wi-Fi connection profile
                subprocess.run(['netsh', 'wlan', 'delete', 'profile', 'name=', selected_ssid], check=True)

                messagebox.showinfo("Network Status", f"Forgotten Wi-Fi network: {selected_ssid}")
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", f"Failed to forget Wi-Fi network: {selected_ssid}")
        elif platform.system() == 'Darwin':  # macOS
            try:
                # Remove the saved Wi-Fi connection profile
                subprocess.run(["networksetup", "-removepreferredwirelessnetwork", wifi_interface, selected_ssid],
                               check=True)

                messagebox.showinfo("Network Status", f"Forgotten Wi-Fi network: {selected_ssid}")
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", f"Failed to forget Wi-Fi network: {selected_ssid}")
    else:
        messagebox.showwarning("Warning", "No network selected")


# Create the main window
window = tk.Tk()
window.title("Wi-Fi Connector")
window.geometry("500x600")

# Create a listbox to display available Wi-Fi networks
wifi_list = tk.Listbox(window, width=30, height=15)
wifi_list.pack(pady=10)

# Bind the on_wifi_select function to the ListboxSelect event
wifi_list.bind("<<ListboxSelect>>", on_wifi_select)

# Create a scrollbar for the listbox
scrollbar = tk.Scrollbar(window)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
wifi_list.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=wifi_list.yview)

# Create buttons for actions
scan_button = tk.Button(window, text="Scan Wi-Fi", command=scan_wifi)
scan_button.pack(pady=(40, 0))

# Create a label and entry for the password
password_label = tk.Label(window, text="Enter Password:")
password_label.pack(pady=(20, 0))
password_entry = tk.Entry(window, show="*")
password_entry.pack(pady=5)

connect_button = tk.Button(window, text="Connect", command=connect_wifi)
connect_button.pack(pady=10)

forget_button = tk.Button(window, text="Forget", command=forget_wifi)
forget_button.pack(pady=10)

# Start the Tkinter event loop
window.mainloop()
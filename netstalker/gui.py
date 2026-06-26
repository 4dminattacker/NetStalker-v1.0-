"""GUI interface for NetStalker."""

try:
    import customtkinter as ctk
    from tkinter import messagebox
    import threading
    import logging
    from netstalker.utils import setup_logger, ColorScheme
    from netstalker.core import NetworkManager, NetworkScanner, AttackManager
    
    logger = setup_logger("netstalker-gui")
    
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    
    class NetStalkerGUI(ctk.CTk):
        """Main GUI application."""
        
        def __init__(self):
            """Initialize GUI application."""
            super().__init__()
            
            self.title("NetStalker - WiFi Penetration Testing Suite")
            self.geometry("1200x700")
            
            self.attack_manager = AttackManager()
            self.networks = []
            
            self._setup_ui()
        
        def _setup_ui(self):
            """Setup user interface."""
            # Configure grid
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(0, weight=1)
            
            # Sidebar
            sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#1a1a1a")
            sidebar.grid(row=0, column=0, sticky="nsew")
            sidebar.grid_propagate(False)
            
            # Header
            header = ctk.CTkLabel(
                sidebar,
                text="NetStalker",
                font=ctk.CTkFont(size=28, weight="bold")
            )
            header.pack(pady=(30, 10))
            
            subheader = ctk.CTkLabel(
                sidebar,
                text="Professional Edition",
                font=ctk.CTkFont(size=10),
                text_color="#888888"
            )
            subheader.pack(pady=(0, 30))
            
            # Interface selection
            ctk.CTkLabel(
                sidebar,
                text="INTERFACE",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#3b8ed0"
            ).pack(pady=(10, 5))
            
            self.iface_var = ctk.StringVar(value="Select Interface")
            self.iface_menu = ctk.CTkOptionMenu(
                sidebar,
                values=NetworkManager.get_interfaces(),
                variable=self.iface_var
            )
            self.iface_menu.pack(pady=5, padx=15, fill="x")
            
            # Buttons
            button_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
            button_frame.pack(pady=20, padx=15, fill="both", expand=True)
            
            buttons = [
                ("SCAN NETWORKS", self._scan_networks, "#2e7d32"),
                ("DEAUTH ATTACK", self._deauth_attack, "#c62828"),
                ("CAPTURE HANDSHAKE", self._capture_handshake, "#f9a825"),
                ("STOP ALL", self._stop_attack, "#37474f"),
            ]
            
            for text, command, color in buttons:
                btn = ctk.CTkButton(
                    button_frame,
                    text=text,
                    command=command,
                    fg_color=color,
                    height=35
                )
                btn.pack(pady=8, fill="x")
            
            # Main view
            main_view = ctk.CTkFrame(self, fg_color="transparent")
            main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
            main_view.grid_columnconfigure(0, weight=1)
            main_view.grid_rowconfigure(1, weight=1)
            
            # Title
            ctk.CTkLabel(
                main_view,
                text="Network Discovery",
                font=ctk.CTkFont(size=20, weight="bold")
            ).grid(row=0, column=0, sticky="w", pady=(0, 10))
            
            # Network list
            self.network_list = ctk.CTkTextbox(
                main_view,
                height=400,
                wrap="word"
            )
            self.network_list.grid(row=1, column=0, sticky="nsew")
            
            # Status bar
            self.status_label = ctk.CTkLabel(
                main_view,
                text="Ready",
                font=ctk.CTkFont(size=10),
                text_color="#888888"
            )
            self.status_label.grid(row=2, column=0, sticky="w", pady=(10, 0))
        
        def _update_status(self, message: str):
            """Update status label."""
            self.status_label.configure(text=message)
            self.update()
        
        def _scan_networks(self):
            """Scan for networks in thread."""
            iface = self.iface_var.get()
            if iface == "Select Interface":
                messagebox.showerror("Error", "Please select an interface")
                return
            
            def scan():
                self._update_status("Enabling monitor mode...")
                if not NetworkManager.enable_monitor_mode(iface):
                    messagebox.showerror("Error", "Failed to enable monitor mode")
                    return
                
                self._update_status("Scanning networks...")
                scanner = NetworkScanner()
                networks = scanner.scan_networks(iface, duration=15)
                
                self.networks = networks
                self._display_networks()
                
                self._update_status(f"Found {len(networks)} networks")
                NetworkManager.disable_monitor_mode(iface)
            
            thread = threading.Thread(target=scan, daemon=True)
            thread.start()
        
        def _display_networks(self):
            """Display networks in text widget."""
            self.network_list.delete("1.0", "end")
            
            header = f"{'No':<4} {'BSSID':<20} {'SSID':<32} {'Channel':<8} {'Signal':<8} {'Security'}\n"
            header += "-" * 85 + "\n"
            
            self.network_list.insert("end", header)
            
            for i, net in enumerate(self.networks, 1):
                ssid = net.ssid[:30] if len(net.ssid) > 30 else net.ssid
                line = f"{i:<4} {net.bssid:<20} {ssid:<32} {net.channel:<8} {net.signal_strength:<8} {net.security}\n"
                self.network_list.insert("end", line)
        
        def _deauth_attack(self):
            """Start deauthentication attack."""
            messagebox.showinfo("Deauth Attack", "Feature coming soon")
        
        def _capture_handshake(self):
            """Start handshake capture."""
            messagebox.showinfo("Capture Handshake", "Feature coming soon")
        
        def _stop_attack(self):
            """Stop all attacks."""
            self.attack_manager.stop_attack()
            self._update_status("Attack stopped")
    
    
    def main():
        """Main GUI entry point."""
        app = NetStalkerGUI()
        app.mainloop()
    
    
    if __name__ == "__main__":
        main()

except ImportError:
    print("Error: customtkinter not installed. Install with: pip install customtkinter")
    sys.exit(1)

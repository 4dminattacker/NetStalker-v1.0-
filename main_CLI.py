#!/usr/bin/env python3
"""NetStalker CLI - Professional WiFi Penetration Testing Tool v2.0"""

import os
import sys
import signal
import logging
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

from core.network_manager import NetworkManager
from core.scanner import WiFiScanner
from core.attack import WiFiAttacker, AttackConfig


class NetStalkerCLI:
    """Command-line interface for NetStalker."""

    def __init__(self):
        """Initialize the CLI application."""
        self.network_manager = NetworkManager()
        self.scanner = WiFiScanner(self.network_manager)
        self.attacker = WiFiAttacker(AttackConfig())
        self.selected_interface: Optional[str] = None
        self.networks = []
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """Handle cleanup on exit."""
        logger.info("\n\nShutting down...")
        self._cleanup()
        sys.exit(0)

    def _cleanup(self):
        """Cleanup resources."""
        try:
            self.attacker.stop_attack()
            if self.selected_interface:
                logger.info(f"Restoring {self.selected_interface} to managed mode...")
                self.network_manager.set_managed_mode(self.selected_interface)
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    @staticmethod
    def show_banner():
        """Display application banner."""
        banner = r"""
    +------------------------------------------------------+
    |                                                      |
    |         NetStalker v2.0 - WiFi Pentester          |
    |                                                      |
    |    Professional Wireless Penetration Testing Suite  |
    |         Created by: 4dmin attacker (Refactored)    |
    |                                                      |
    |    [OK] Error Handling    [OK] Code Quality         |
    |    [OK] Security          [OK] Enterprise Grade     |
    |                                                      |
    +------------------------------------------------------+
        """
        print(banner)

    def check_requirements(self) -> bool:
        """Check if running as root and required tools installed.
        
        Returns:
            True if all requirements met
        """
        if os.getuid() != 0:
            logger.error("[!] This tool requires root privileges!")
            logger.info("Run with: sudo python3 main_CLI.py")
            return False
        
        required_tools = ["airmon-ng", "airodump-ng", "aireplay-ng", "aircrack-ng"]
        missing = []
        
        for tool in required_tools:
            result = self.network_manager.run_command(f"which {tool}")
            if not result["success"]:
                missing.append(tool)
        
        if missing:
            logger.error(f"[!] Missing required tools: {', '.join(missing)}")
            logger.info("Install aircrack-ng suite: sudo apt install aircrack-ng")
            return False
        
        logger.info("[+] All requirements met!")
        return True

    def select_interface(self) -> bool:
        """Select network interface.
        
        Returns:
            True if interface selected successfully
        """
        interfaces = self.network_manager.get_interfaces()
        
        if not interfaces:
            logger.error("[!] No WiFi interfaces found!")
            return False
        
        print("\n[*] Available Interfaces:")
        for i, iface in enumerate(interfaces):
            mode = f"[{iface.mode}]" if iface.mode else ""
            print(f"  [{i}] {iface.name} {mode}")
        
        try:
            idx = int(input("\nSelect interface (number): "))
            if 0 <= idx < len(interfaces):
                self.selected_interface = interfaces[idx].name
                logger.info(f"Selected: {self.selected_interface}")
                return True
            else:
                logger.error("[!] Invalid selection!")
                return False
        except ValueError:
            logger.error("[!] Invalid input!")
            return False

    def scan_networks(self) -> bool:
        """Scan for WiFi networks.
        
        Returns:
            True if scan completed
        """
        if not self.selected_interface:
            logger.error("[!] No interface selected!")
            return False
        
        # Set to monitor mode
        if not self.network_manager.set_monitor_mode(self.selected_interface):
            logger.error("[!] Failed to set monitor mode!")
            return False
        
        # Perform scan
        self.networks = self.scanner.scan(self.selected_interface, duration=10)
        
        if not self.networks:
            logger.warning("[*] No networks found!")
            return False
        
        # Display results
        print("\n[+] Found Networks:")
        print(f"{'ID':<3} | {'SSID':<25} | {'BSSID':<17} | {'CH':<2} | {'SIGNAL':<6}")
        print("-" * 75)
        
        for i, net in enumerate(self.networks, 1):
            signal = net.signal_strength or "-"
            print(f"{i:<3} | {net.ssid[:25]:<25} | {net.bssid:<17} | {net.channel:<2} | {signal:<6}")
        
        return True

    def launch_deauth_attack(self):
        """Launch deauthentication attack."""
        if not self.networks:
            logger.error("[!] Run scan first!")
            return
        
        try:
            target_id = int(input("Enter target ID: ")) - 1
            if not (0 <= target_id < len(self.networks)):
                logger.error("[!] Invalid target ID!")
                return
            
            target = self.networks[target_id]
            duration = int(input("Attack duration (seconds, default 60): ") or "60")
            
            self.attacker.deauth_attack(target.bssid, self.selected_interface, duration)
            
            # Keep running
            try:
                import time
                time.sleep(duration)
            except KeyboardInterrupt:
                logger.info("Attack interrupted by user")
            finally:
                self.attacker.stop_attack()
        except ValueError:
            logger.error("[!] Invalid input!")
        except Exception as e:
            logger.error(f"[!] Error: {e}")

    def capture_handshake(self):
        """Capture WPA handshake."""
        if not self.networks:
            logger.error("[!] Run scan first!")
            return
        
        try:
            target_id = int(input("Enter target ID: ")) - 1
            if not (0 <= target_id < len(self.networks)):
                logger.error("[!] Invalid target ID!")
                return
            
            target = self.networks[target_id]
            duration = int(input("Capture duration (seconds, default 300): ") or "300")
            
            cap_file = self.attacker.capture_handshake(
                target.bssid,
                target.channel,
                self.selected_interface,
                target.ssid,
                duration
            )
            
            if cap_file:
                logger.info(f"[+] Handshake captured: {cap_file}")
            else:
                logger.warning("[*] No handshake captured")
        except ValueError:
            logger.error("[!] Invalid input!")
        except KeyboardInterrupt:
            logger.info("Capture interrupted by user")
            self.attacker.stop_attack()
        except Exception as e:
            logger.error(f"[!] Error: {e}")

    def crack_handshake(self):
        """Crack WPA handshake."""
        cap_file = input("Enter path to capture file: ").strip()
        wordlist = input("Enter wordlist path (default: /usr/share/wordlists/rockyou.txt): ").strip() \
                   or "/usr/share/wordlists/rockyou.txt"
        
        self.attacker.crack_handshake(cap_file, wordlist)

    def show_menu(self):
        """Display main menu."""
        print("\n[*] Menu:")
        print("  1. Scan Networks")
        print("  2. Deauth Attack")
        print("  3. Capture Handshake")
        print("  4. Crack Handshake")
        print("  5. Exit")

    def run(self):
        """Run the CLI application."""
        self.show_banner()
        
        if not self.check_requirements():
            return
        
        if not self.select_interface():
            return
        
        while True:
            self.show_menu()
            try:
                choice = input("\nSelect option: ").strip()
                
                if choice == "1":
                    self.scan_networks()
                elif choice == "2":
                    self.launch_deauth_attack()
                elif choice == "3":
                    self.capture_handshake()
                elif choice == "4":
                    self.crack_handshake()
                elif choice == "5":
                    self._cleanup()
                    logger.info("Goodbye!")
                    break
                else:
                    logger.warning("[!] Invalid option!")
            except KeyboardInterrupt:
                logger.info("\nInterrupted by user")
                self._cleanup()
                break
            except Exception as e:
                logger.error(f"[!] Error: {e}")


if __name__ == "__main__":
    cli = NetStalkerCLI()
    cli.run()

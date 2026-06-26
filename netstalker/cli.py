"""Command-line interface for NetStalker."""

import argparse
import logging
import sys
from pathlib import Path

from netstalker.utils import setup_logger, ColorScheme
from netstalker.core import NetworkManager, NetworkScanner, AttackManager

logger = setup_logger("netstalker-cli")


def print_banner():
    """Print application banner."""
    banner = f"""
{ColorScheme.BLUE}╔════════════════════════════════════════════════════════╗
║{ColorScheme.RED}{ColorScheme.BOLD}  NetStalker - WiFi Penetration Testing Suite{ColorScheme.BLUE}  ║
║{ColorScheme.GREEN}              Professional Edition v2.0                {ColorScheme.BLUE}║
║{ColorScheme.YELLOW}              Created by: 4dmin attacker                 {ColorScheme.BLUE}║
╚════════════════════════════════════════════════════════╝{ColorScheme.RESET}
    """
    print(banner)


def list_interfaces():
    """List available network interfaces."""
    print(ColorScheme.info("Scanning available interfaces..."))
    interfaces = NetworkManager.get_interfaces()
    
    if not interfaces:
        print(ColorScheme.error("No interfaces found"))
        return
    
    print(f"\n{ColorScheme.BOLD}Available Interfaces:{ColorScheme.RESET}")
    for i, iface in enumerate(interfaces, 1):
        print(f"  {i}. {iface}")
    print()


def scan_networks(iface: str):
    """Scan for WiFi networks."""
    print(ColorScheme.info(f"Scanning networks on {iface}..."))
    
    if not NetworkManager.enable_monitor_mode(iface):
        print(ColorScheme.error("Failed to enable monitor mode"))
        return
    
    scanner = NetworkScanner()
    networks = scanner.scan_networks(iface)
    
    if not networks:
        print(ColorScheme.warning("No networks found"))
        return
    
    print(f"\n{ColorScheme.BOLD}Found {len(networks)} Networks:{ColorScheme.RESET}")
    print(f"{'No.':<4} {'BSSID':<20} {'SSID':<32} {'CH':<4} {'Signal':<8} {'Security'}")
    print("-" * 90)
    
    for i, net in enumerate(networks, 1):
        ssid = net.ssid[:31] if len(net.ssid) > 31 else net.ssid
        print(f"{i:<4} {net.bssid:<20} {ssid:<32} {net.channel:<4} {net.signal_strength:<8} {net.security}")
    
    NetworkManager.disable_monitor_mode(iface)


def main():
    """Main CLI entry point."""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="NetStalker - WiFi Penetration Testing Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  netstalker-cli --list-interfaces
  netstalker-cli --scan-networks -i wlan0
        """
    )
    
    parser.add_argument(
        "--list-interfaces",
        action="store_true",
        help="List available network interfaces"
    )
    parser.add_argument(
        "--scan-networks",
        action="store_true",
        help="Scan for WiFi networks"
    )
    parser.add_argument(
        "-i", "--interface",
        help="Network interface to use"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    if args.list_interfaces:
        list_interfaces()
    elif args.scan_networks:
        if not args.interface:
            print(ColorScheme.error("Interface required for scanning"))
            sys.exit(1)
        scan_networks(args.interface)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

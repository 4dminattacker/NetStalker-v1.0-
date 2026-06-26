"""WiFi network scanning functionality."""

import subprocess
import logging
import re
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class WiFiNetwork:
    """Represents a WiFi network."""
    bssid: str
    ssid: str
    channel: int
    signal_strength: int
    security: str
    band: str = "2.4GHz"


class NetworkScanner:
    """Scans for available WiFi networks."""

    @staticmethod
    def scan_networks(iface: str, duration: int = 15) -> List[WiFiNetwork]:
        """Scan for WiFi networks.
        
        Args:
            iface: Interface name
            duration: Scan duration in seconds
            
        Returns:
            List of discovered networks
        """
        networks = []
        try:
            logger.info(f"Starting network scan on {iface}")
            
            cmd = f"sudo airodump-ng {iface} --write scan_dump --csv -t OPN --ignore-negative-one 2>/dev/null"
            
            try:
                subprocess.run(cmd, shell=True, timeout=duration)
            except subprocess.TimeoutExpired:
                pass
            
            networks = NetworkScanner._parse_airodump_output()
            logger.info(f"Found {len(networks)} networks")
            
        except Exception as e:
            logger.error(f"Error scanning networks: {e}")
        
        return networks

    @staticmethod
    def _parse_airodump_output() -> List[WiFiNetwork]:
        """Parse airodump-ng CSV output.
        
        Returns:
            List of discovered networks
        """
        networks = []
        try:
            with open("scan_dump-01.csv", "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "," not in line or not line.strip():
                        continue
                    
                    parts = [p.strip() for p in line.split(",")]
                    
                    if len(parts) < 7:
                        continue
                    
                    try:
                        bssid = parts[0]
                        if not re.match(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", bssid):
                            continue
                        
                        network = WiFiNetwork(
                            bssid=bssid,
                            ssid=parts[13] if len(parts) > 13 else "Hidden",
                            channel=int(parts[3]) if parts[3].isdigit() else 1,
                            signal_strength=int(parts[8]) if parts[8].lstrip("-").isdigit() else 0,
                            security=parts[5] if len(parts) > 5 else "Unknown"
                        )
                        networks.append(network)
                    except (ValueError, IndexError) as e:
                        logger.debug(f"Error parsing line: {e}")
                        continue
        except FileNotFoundError:
            logger.warning("Scan output file not found")
        except Exception as e:
            logger.error(f"Error parsing airodump output: {e}")
        
        return networks

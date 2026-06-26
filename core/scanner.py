"""WiFi network scanning module."""
import os
import csv
import logging
import subprocess
from typing import List
from pathlib import Path

from core.network_manager import NetworkManager, WiFiNetwork

logger = logging.getLogger(__name__)


class WiFiScanner:
    """Scans for available WiFi networks."""

    def __init__(self, network_manager: NetworkManager):
        """Initialize scanner.
        
        Args:
            network_manager: NetworkManager instance
        """
        self.network_manager = network_manager
        self.temp_dir = Path("/tmp/netstalker_scan")
        self.temp_dir.mkdir(exist_ok=True)

    def scan(self, iface: str, duration: int = 10) -> List[WiFiNetwork]:
        """Scan for WiFi networks.
        
        Args:
            iface: Interface name
            duration: Scan duration in seconds
            
        Returns:
            List of discovered WiFiNetwork objects
        """
        try:
            logger.info(f"Starting WiFi scan on {iface} for {duration}s...")
            
            temp_file = self.temp_dir / "scan"
            csv_file = f"{temp_file}-01.csv"
            
            # Clean up old files
            try:
                for old_file in self.temp_dir.glob("scan*"):
                    old_file.unlink()
            except Exception as e:
                logger.warning(f"Could not clean temp files: {e}")
            
            # Run scan
            cmd = f"sudo timeout {duration} airodump-ng --write {temp_file} --output-format csv {iface}"
            result = self.network_manager.run_command(cmd, timeout=duration + 5)
            
            if not result["success"] and result["returncode"] != 124:  # 124 is timeout exit code
                logger.error(f"Scan failed: {result['stderr']}")
                return []
            
            # Parse results
            networks = self._parse_csv(csv_file)
            logger.info(f"Found {len(networks)} network(s)")
            return networks
        except Exception as e:
            logger.error(f"Error during scan: {e}")
            return []

    @staticmethod
    def _parse_csv(csv_file: str) -> List[WiFiNetwork]:
        """Parse airodump-ng CSV output.
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            List of WiFiNetwork objects
        """
        networks = []
        
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return networks
        
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                started = False
                
                for row in reader:
                    if not row or len(row) < 14:
                        continue
                    
                    # Check for header
                    if "BSSID" in str(row[0]):
                        started = True
                        continue
                    
                    # Stop at client section
                    if "Station" in str(row[0]):
                        break
                    
                    if started:
                        try:
                            bssid = row[0].strip()
                            channel = row[3].strip()
                            signal = row[8].strip() if len(row) > 8 else "-"
                            ssid = row[13].strip() or "[HIDDEN]"
                            
                            if bssid and channel:
                                network = WiFiNetwork(
                                    ssid=ssid,
                                    bssid=bssid,
                                    channel=channel,
                                    signal_strength=signal
                                )
                                networks.append(network)
                        except (IndexError, ValueError) as e:
                            logger.debug(f"Error parsing row: {e}")
                            continue
        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
        
        return networks

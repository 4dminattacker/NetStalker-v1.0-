"""Network interface management and monitoring."""
import subprocess
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NetworkInterface:
    """Represents a network interface."""
    name: str
    mode: str
    mac: Optional[str] = None


@dataclass
class WiFiNetwork:
    """Represents a scanned WiFi network."""
    ssid: str
    bssid: str
    channel: str
    signal_strength: str = "-"
    security: str = ""


class NetworkManager:
    """Manages network interface operations and WiFi scanning."""

    def __init__(self):
        """Initialize the network manager."""
        self.current_interface: Optional[str] = None

    @staticmethod
    def run_command(
        cmd: str, 
        capture_output: bool = True, 
        timeout: int = 30
    ) -> Dict[str, any]:
        """Execute a system command safely.
        
        Args:
            cmd: Command to execute
            capture_output: Whether to capture output
            timeout: Command timeout in seconds
            
        Returns:
            Dictionary with returncode, stdout, and stderr
        """
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {cmd}")
            return {"returncode": -1, "stdout": "", "stderr": "Timeout", "success": False}
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return {"returncode": -1, "stdout": "", "stderr": str(e), "success": False}

    def get_interfaces(self) -> List[NetworkInterface]:
        """Get list of available WiFi interfaces.
        
        Returns:
            List of NetworkInterface objects
        """
        try:
            result = self.run_command("iw dev")
            if not result["success"]:
                logger.warning("Failed to get interfaces")
                return []

            interfaces = []
            current_iface = None
            
            for line in result["stdout"].split('\n'):
                if 'Interface' in line:
                    current_iface = line.split()[1].strip()
                elif 'type' in line and current_iface:
                    mode = line.split()[1].strip()
                    interfaces.append(NetworkInterface(name=current_iface, mode=mode))
                    current_iface = None
            
            logger.info(f"Found {len(interfaces)} interface(s)")
            return interfaces
        except Exception as e:
            logger.error(f"Error getting interfaces: {e}")
            return []

    def set_monitor_mode(self, iface: str) -> bool:
        """Switch interface to monitor mode.
        
        Args:
            iface: Interface name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Switching {iface} to monitor mode...")
            
            self.run_command("sudo airmon-ng check kill")
            self.run_command(f"sudo ip link set {iface} down")
            
            result = self.run_command(f"sudo iw {iface} set type monitor")
            if not result["success"]:
                logger.error(f"Failed to set monitor mode: {result['stderr']}")
                return False
            
            result = self.run_command(f"sudo ip link set {iface} up")
            if not result["success"]:
                logger.error(f"Failed to bring interface up: {result['stderr']}")
                return False
            
            self.current_interface = iface
            logger.info(f"Successfully switched {iface} to monitor mode")
            return True
        except Exception as e:
            logger.error(f"Error setting monitor mode: {e}")
            return False

    def set_managed_mode(self, iface: str) -> bool:
        """Switch interface back to managed mode.
        
        Args:
            iface: Interface name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Switching {iface} to managed mode...")
            
            self.run_command(f"sudo ip link set {iface} down")
            self.run_command(f"sudo iw {iface} set type managed")
            self.run_command(f"sudo ip link set {iface} up")
            self.run_command("sudo systemctl start NetworkManager")
            
            logger.info(f"Successfully switched {iface} to managed mode")
            return True
        except Exception as e:
            logger.error(f"Error setting managed mode: {e}")
            return False

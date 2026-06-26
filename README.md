# NetStalker - Professional WiFi Penetration Testing Suite

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

NetStalker is a professional-grade WiFi penetration testing suite designed for security professionals and ethical hackers. It automates complex wireless attack operations into an intuitive interface.

### Key Features

- ✅ **Network Scanning**: Discover WiFi networks in range
- ✅ **Monitor Mode Management**: Automatic interface mode switching
- ✅ **Deauthentication Attacks**: Disconnect clients from networks
- ✅ **Handshake Capture**: Capture WPA/WPA2 handshakes for offline cracking
- ✅ **Dual Interface**: CLI and GUI versions
- ✅ **Professional Code**: Well-structured, tested, and documented

## Requirements

### System Requirements

- Linux (Kali, Ubuntu, ParrotOS, etc.)
- WiFi adapter with monitor mode support
- Root/sudo privileges
- Python 3.8+

### Dependencies

- `aircrack-ng` suite (airodump-ng, aireplay-ng)
- `iw` (wireless configuration)
- `customtkinter` (for GUI)

## Installation

### 1. Install System Dependencies

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y aircrack-ng wireless-tools iw python3-pip

# Kali Linux
sudo apt-get install -y aircrack-ng wireless-tools iw python3-pip
```

### 2. Clone Repository

```bash
git clone https://github.com/4dminattacker/NetStalker-v1.0-.git
cd NetStalker-v1.0-
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Package

```bash
pip install -e .
```

## Usage

### CLI Mode

#### List Available Interfaces

```bash
netstalker-cli --list-interfaces
```

#### Scan Networks

```bash
netstalker-cli --scan-networks -i wlan0
```

#### Help

```bash
netstalker-cli --help
```

### GUI Mode

```bash
netstalker-gui
```

Or directly:

```bash
python -m netstalker.gui
```

## Project Structure

```
NetStalker/
├── netstalker/
│   ├── __init__.py
│   ├── cli.py                 # Command-line interface
│   ├── gui.py                 # GUI interface
│   ├── core/
│   │   ├── __init__.py
│   │   ├── network.py         # Network management
│   │   ├── scanner.py         # Network scanning
│   │   └── attack.py          # Attack operations
│   └── utils/
│       ├── __init__.py
│       ├── logger.py          # Logging setup
│       └── colors.py          # Color schemes
├── setup.py
├── requirements.txt
├── README.md
└── LICENSE
```

## Features Details

### Network Scanning

Automatically discovers nearby WiFi networks and displays:
- BSSID (MAC address)
- SSID (network name)
- Channel
- Signal strength
- Security type

### Deauthentication Attack

Disconnects specific clients from target networks:
- Broadcast deauth (all clients)
- Targeted deauth (specific client)
- Configurable attack duration

### Handshake Capture

Captures WPA/WPA2 4-way handshake:
- Required for offline password cracking
- Automatic format conversion
- Progress monitoring

## Configuration

Create `config.py` in the project root for custom settings:

```python
# config.py
LOG_LEVEL = "INFO"
SCAN_DURATION = 15
DEAUTH_PACKETS = 0  # 0 = unlimited
OUTPUT_DIR = "captures/"
```

## Troubleshooting

### Monitor Mode Issues

```bash
# Check current mode
iwconfig

# Manual mode switching
sudo airmon-ng check kill
sudo airmon-ng start wlan0
```

### Permission Denied

Ensure you run with sudo or configure passwordless sudo:

```bash
sudo -l
sudo python -m netstalker.gui
```

### No Networks Found

1. Verify adapter supports monitor mode
2. Check antenna status: `ifconfig`
3. Run longer scan: `netstalker-cli --scan-networks -i wlan0`

## Legal Notice

⚠️ **WARNING**: This tool is intended for authorized security testing and educational purposes only.

Unauthorized access to computer networks is illegal. Users are responsible for ensuring they have proper authorization before conducting any security tests.

## License

MIT License - See LICENSE file for details

## Author

**4dmin attacker**
- GitHub: [@4dminattacker](https://github.com/4dminattacker)
- Email: 4dminattacker@gmail.com

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues and feature requests, please visit: [GitHub Issues](https://github.com/4dminattacker/NetStalker-v1.0-/issues)

## Changelog

### v2.0.0 (Current)
- Complete code refactor
- Professional package structure
- Enhanced error handling
- Improved documentation
- Removed emoji from code
- Better separation of concerns
- Added proper logging
- CLI and GUI separation

### v1.0.0
- Initial release
- Basic scanning and attack features

---

**Made with ❤️ for the security community**

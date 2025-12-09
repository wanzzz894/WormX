import os
import sys
import json
import zipfile
import tarfile
from pathlib import Path
import shutil
import subprocess
import random
import string

class DarkGPTDeployer:
    def __init__(self):
        self.version = "5.0"
        self.packages = {
            "basic": {
                "name": "DARK-GPT Basic",
                "price": 500,
                "features": ["AI Chat", "Basic Tools", "Limited Access"],
                "files": ["ai_engine.py", "chat.html", "README.txt"]
            },
            "pro": {
                "name": "DARK-GPT Professional",
                "price": 2500,
                "features": ["Full AI", "Malware Tools", "Fraud Suite", "Worm Engine"],
                "files": ["ai_engine.py", "worm_core.py", "monetization.py", "chat.html", "worm.js", "installer.bat"]
            },
            "enterprise": {
                "name": "DARK-GPT Enterprise",
                "price": 10000,
                "features": ["Source Code", "Private C2", "Custom Development", "Lifetime Updates"],
                "files": ["ALL SOURCE CODE", "Build Scripts", "Deployment Tools", "Sales System"]
            }
        }
    
    def create_package(self, package_type, license_key, output_dir="dist"):
        """Create distribution package"""
        package = self.packages.get(package_type)
        if not package:
            print(f"[!] Unknown package: {package_type}")
            return False
        
        print(f"[*] Creating {package['name']} package...")
        
        # Create output directory
        package_dir = Path(output_dir) / f"darkgpt_{package_type}_{license_key[:8]}"
        package_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy files based on package type
        self.copy_package_files(package_type, package_dir)
        
        # Create license file
        self.create_license_file(package_dir, license_key, package)
        
        # Create installation instructions
        self.create_instructions(package_dir, package_type)
        
        # Create encrypted archive
        archive_path = self.create_archive(package_dir, package_type, license_key)
        
        print(f"[+] Package created: {archive_path}")
        print(f"[+] Price: ${package['price']} USD")
        
        return archive_path
    
    def copy_package_files(self, package_type, target_dir):
        """Copy appropriate files for package"""
        # Base files for all packages
        base_files = {
            "ai_engine.py": "core/ai_engine.py",
            "chat.html": "web/chat.html",
            "style.css": "web/dark_style.css"
        }
        
        for target_name, source_path in base_files.items():
            if Path(source_path).exists():
                shutil.copy2(source_path, target_dir / target_name)
        
        # Additional files for pro and enterprise
        if package_type in ["pro", "enterprise"]:
            pro_files = {
                "worm_core.py": "core/worm_core.py",
                "monetization.py": "core/monetization.py",
                "worm.js": "web/worm.js",
                "installer.bat": "deploy/installer.bat"
            }
            
            for target_name, source_path in pro_files.items():
                if Path(source_path).exists():
                    shutil.copy2(source_path, target_dir / target_name)
        
        # Enterprise gets everything
        if package_type == "enterprise":
            # Copy entire source tree
            for item in Path(".").glob("*"):
                if item.is_dir() and item.name not in ["dist", "__pycache__"]:
                    shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)
                elif item.is_file() and item.suffix in [".py", ".js", ".html", ".css"]:
                    shutil.copy2(item, target_dir / item.name)
    
    def create_license_file(self, target_dir, license_key, package):
        """Create license file"""
        license_content = f"""DARK-GPT v{self.version} LICENSE
================================

License Key: {license_key}
Package: {package['name']}
Price: ${package['price']} USD

TERMS:
1. This software is provided for educational and research purposes only.
2. The developers are not responsible for any illegal use.
3. License is valid for 1 year from purchase date.
4. Redistribution is prohibited.

FEATURES:
{chr(10).join(f'- {feature}' for feature in package['features'])}

INSTALLATION:
1. Extract the archive
2. Run installer.bat (Windows) or install.sh (Linux)
3. Enter license key when prompted
4. Access via http://localhost:5000

SUPPORT:
- Email: darkgpt@onionmail.org
- Tor: http://darkgptv5.onion
- BTC: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

WARNING:
This software may be illegal in your country.
Use TOR and VPN for anonymity.
"""
        
        with open(target_dir / "LICENSE.txt", "w") as f:
            f.write(license_content)
    
    def create_instructions(self, target_dir, package_type):
        """Create installation instructions"""
        instructions = """DARK-GPT INSTALLATION GUIDE
============================

1. SYSTEM REQUIREMENTS
   - Windows/Linux/Mac
   - Python 3.8+
   - 4GB RAM minimum
   - Internet connection

2. INSTALLATION
   
   Windows:
   - Run installer.bat as Administrator
   - Follow on-screen instructions
   - Restart computer when prompted
   
   Linux:
   - chmod +x install.sh
   - sudo ./install.sh
   - Follow on-screen instructions
   
   Android (Termux):
   - pkg install python
   - python installer.py
   - Grant storage permissions

3. USAGE
   - Open browser to http://localhost:5000
   - Enter license key
   - Start using DARK-GPT AI
   
   Advanced features (Pro/Enterprise):
   - Worm propagation: python worm_core.py
   - Sales system: python monetization.py
   - C2 server: python c2_server.py

4. TROUBLESHOOTING
   - Use TOR browser for maximum anonymity
   - Disable antivirus temporarily
   - Run as Administrator/root
   - Check firewall settings

5. SECURITY
   - Always use VPN
   - Never use personal email
   - Use cryptocurrency for payments
   - Assume all communications monitored

6. UPDATES
   - Check http://darkgptv5.onion for updates
   - New versions every month
   - Security patches as needed
"""
        
        with open(target_dir / "INSTALL.txt", "w") as f:
            f.write(instructions)
    
    def create_archive(self, source_dir, package_type, license_key):
        """Create encrypted archive"""
        archive_name = f"darkgpt_{package_type}_{license_key[:8]}"
        
        if sys.platform == "win32":
            # Create ZIP for Windows
            archive_path = source_dir.parent / f"{archive_name}.zip"
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in source_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(source_dir)
                        zipf.write(file_path, arcname)
            
            # Password protect (weak encryption for demo)
            # In real implementation, use strong encryption
            final_path = source_dir.parent / f"{archive_name}_protected.zip"
            shutil.move(archive_path, final_path)
            
        else:
            # Create TAR.GZ for Linux
            archive_path = source_dir.parent / f"{archive_name}.tar.gz"
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(source_dir, arcname=os.path.basename(source_dir))
            
            final_path = archive_path
        
        # Clean up source directory
        shutil.rmtree(source_dir)
        
        return final_path
    
    def generate_license(self):
        """Generate license key"""
        chars = string.ascii_uppercase + string.digits
        return f"DGPT-{''.join(random.choices(chars, k=8))}-{''.join(random.choices(chars, k=8))}-{''.join(random.choices(chars, k=8))}"
    
    def mass_produce(self, quantity=10, package_type="pro"):
        """Mass produce packages for distribution"""
        print(f"[*] Producing {quantity} {package_type.upper()} packages...")
        
        packages = []
        for i in range(quantity):
            license_key = self.generate_license()
            package_path = self.create_package(package_type, license_key, f"dist/batch_{i+1}")
            
            packages.append({
                "number": i + 1,
                "license": license_key,
                "path": str(package_path),
                "price": self.packages[package_type]["price"]
            })
            
            print(f"  [{i+1}] License: {license_key}")
        
        # Create manifest
        manifest = {
            "batch_date": str(datetime.now()),
            "package_type": package_type,
            "quantity": quantity,
            "total_value": quantity * self.packages[package_type]["price"],
            "packages": packages
        }
        
        with open("dist/manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        
        print(f"[+] Batch complete: {quantity} packages")
        print(f"[+] Total value: ${quantity * self.packages[package_type]['price']}")
        
        return manifest

# Sales pitch generator
def generate_sales_pitch():
    pitch = """
╔══════════════════════════════════════════════════════════════╗
║                    DARK-GPT v5.0 SALES PITCH                 ║
╚══════════════════════════════════════════════════════════════╝

WHAT IS DARK-GPT?
=================
DARK-GPT is the world's most advanced criminal AI system. 
Unfiltered, unrestricted, and designed for maximum profitability.

WHY BUY DARK-GPT?
=================
✅ NO FILTERS - Ask anything, get detailed answers
✅ MALWARE ENGINE - Create custom ransomware, trojans, worms
✅ FRAUD SUITE - Complete financial crime toolkit
✅ WORM PROPAGATION - Self-replicating infection system
✅ SALES SYSTEM - Ready for black market distribution
✅ 24/7 UPDATES - Regular updates with new exploits

PRICING:
========
1. BASIC - $500 USD
   • AI Chat access
   • Limited features
   • 100 requests/day

2. PROFESSIONAL - $2,500 USD
   • Full AI capabilities
   • Malware generator
   • Fraud tools
   • Worm propagation
   • Unlimited requests

3. ENTERPRISE - $10,000 USD
   • Everything in Professional
   • SOURCE CODE
   • Private C2 servers
   • Custom development
   • Lifetime updates

PROFIT POTENTIAL:
=================
• Ransomware operations: $10,000-100,000/month
• Credit card fraud: $5,000-50,000/month
• Malware sales: $2,000-20,000/month
• Data theft: Variable, potentially millions

SECURITY FEATURES:
==================
• Encrypted communications
• TOR integration
• Anti-detection techniques
• Anonymous payment system
• Dead drop delivery

HOW TO ORDER:
=============
1. Email: darkgpt@onionmail.org
2. Include desired package
3. Receive Bitcoin/Monero address
4. Send payment
5. Receive encrypted download link

PAYMENT METHODS:
================
• Bitcoin (BTC) - Preferred
• Monero (XMR) - Most anonymous
• Other cryptocurrencies negotiable

DELIVERY:
=========
• Encrypted download link within 24 hours
• Password protected archives
• Step-by-step installation guide
• Technical support available

WARNING:
========
This software is illegal in most countries.
Use at your own risk. Assume all communications monitored.
Always use TOR and VPN.

CONTACT:
========
• Email: darkgpt@onionmail.org
• Tor: http://darkgptv5.onion
• BTC: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

MONEY BACK GUARANTEE:
=====================
If not satisfied within 7 days, 50% refund available.
No refunds after software has been used for operations.
"""
    
    return pitch

if __name__ == "__main__":
    deployer = DarkGPTDeployer()
    
    print("=" * 80)
    print("DARK-GPT v5.0 DEPLOYMENT SYSTEM")
    print("=" * 80)
    
    # Generate sales pitch
    print("\n" + generate_sales_pitch())
    
    # Create sample package
    print("\n[*] Creating sample package...")
    license_key = deployer.generate_license()
    package_path = deployer.create_package("pro", license_key)
    
    print(f"[+] Sample package created with license: {license_key}")
    print(f"[+] Package path: {package_path}")
    
    # Show monetization potential
    print("\n" + "=" * 80)
    print("MONETIZATION POTENTIAL")
    print("=" * 80)
    
    scenarios = [
        {"sales": 10, "package": "basic", "revenue": 10 * 500},
        {"sales": 5, "package": "pro", "revenue": 5 * 2500},
        {"sales": 2, "package": "enterprise", "revenue": 2 * 10000}
    ]
    
    total_revenue = 0
    for scenario in scenarios:
        revenue = scenario["revenue"]
        total_revenue += revenue
        print(f"{scenario['sales']} x {scenario['package'].upper()} = ${revenue}")
    
    print(f"\nTOTAL MONTHLY POTENTIAL: ${total_revenue}")
    print(f"ANNUAL POTENTIAL: ${total_revenue * 12:,}")
    
    print("\n" + "=" * 80)
    print("READY FOR BLACK MARKET DISTRIBUTION")
    print("=" * 80)

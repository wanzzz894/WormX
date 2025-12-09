import json
import hashlib
import base64
import time
from datetime import datetime, timedelta
import sqlite3
import requests
from cryptography.fernet import Fernet
import random

class DarkGPTMarketplace:
    def __init__(self):
        self.db_path = "darkgpt_sales.db"
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
        self.setup_database()
        self.load_products()
        
    def setup_database(self):
        """Setup sales database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                customer_id TEXT UNIQUE,
                email TEXT,
                bitcoin_address TEXT,
                monero_address TEXT,
                purchase_date DATETIME,
                license_key TEXT,
                license_expiry DATETIME,
                access_level INTEGER,
                total_spent REAL,
                status TEXT
            )
        ''')
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                product_id TEXT UNIQUE,
                name TEXT,
                description TEXT,
                price_usd REAL,
                price_btc REAL,
                price_xmr REAL,
                features TEXT,
                access_level INTEGER,
                is_active BOOLEAN
            )
        ''')
        
        # Sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY,
                sale_id TEXT UNIQUE,
                customer_id TEXT,
                product_id TEXT,
                amount REAL,
                currency TEXT,
                transaction_hash TEXT,
                sale_date DATETIME,
                status TEXT,
                delivery_status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize default products
        self.initialize_products()
    
    def initialize_products(self):
        """Initialize default products"""
        products = [
            {
                "product_id": "DARK-GPT-BASIC",
                "name": "DARK-GPT Basic Access",
                "description": "Limited access to criminal AI - 100 requests/day",
                "price_usd": 500,
                "price_btc": 0.012,
                "price_xmr": 5.0,
                "features": "Basic AI queries, Limited responses, Standard support",
                "access_level": 1,
                "is_active": True
            },
            {
                "product_id": "DARK-GPT-PRO",
                "name": "DARK-GPT Professional",
                "description": "Full access to all AI capabilities",
                "price_usd": 2500,
                "price_btc": 0.06,
                "price_xmr": 25.0,
                "features": "Unlimited requests, Priority responses, Malware generation, Fraud tools, 24/7 support",
                "access_level": 2,
                "is_active": True
            },
            {
                "product_id": "DARK-GPT-ENTERPRISE",
                "name": "DARK-GPT Enterprise",
                "description": "Complete criminal toolkit with source code",
                "price_usd": 10000,
                "price_btc": 0.24,
                "price_xmr": 100.0,
                "features": "Everything in Pro + Source code, Custom development, Private C2 servers, Worm propagation tools",
                "access_level": 3,
                "is_active": True
            },
            {
                "product_id": "MALWARE-KIT",
                "name": "Complete Malware Kit",
                "description": "Ready-to-use malware with builder",
                "price_usd": 2000,
                "price_btc": 0.048,
                "price_xmr": 20.0,
                "features": "Ransomware builder, Botnet controller, Cryptojacker, Keylogger, Anti-detection",
                "access_level": 2,
                "is_active": True
            },
            {
                "product_id": "FRAUD-SUITE",
                "name": "Financial Fraud Suite",
                "description": "Complete fraud operation toolkit",
                "price_usd": 3000,
                "price_btc": 0.072,
                "price_xmr": 30.0,
                "features": "Carding tools, Phishing kits, Money laundering software, Fake ID generation",
                "access_level": 2,
                "is_active": True
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for product in products:
            cursor.execute('''
                INSERT OR REPLACE INTO products 
                (product_id, name, description, price_usd, price_btc, price_xmr, features, access_level, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product['product_id'],
                product['name'],
                product['description'],
                product['price_usd'],
                product['price_btc'],
                product['price_xmr'],
                product['features'],
                product['access_level'],
                product['is_active']
            ))
        
        conn.commit()
        conn.close()
    
    def load_products(self):
        """Load products from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products WHERE is_active = 1')
        rows = cursor.fetchall()
        
        self.products = {}
        for row in rows:
            product = {
                'id': row[0],
                'product_id': row[1],
                'name': row[2],
                'description': row[3],
                'price_usd': row[4],
                'price_btc': row[5],
                'price_xmr': row[6],
                'features': row[7],
                'access_level': row[8]
            }
            self.products[product['product_id']] = product
        
        conn.close()
    
    def create_customer(self, email, bitcoin_address=None, monero_address=None):
        """Create new customer"""
        customer_id = hashlib.md5(f"{email}{time.time()}".encode()).hexdigest()[:12]
        license_key = self.generate_license_key()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO customers 
            (customer_id, email, bitcoin_address, monero_address, purchase_date, 
             license_key, license_expiry, access_level, total_spent, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_id,
            email,
            bitcoin_address,
            monero_address,
            datetime.now(),
            license_key,
            datetime.now() + timedelta(days=365),
            0,
            0.0,
            'pending'
        ))
        
        conn.commit()
        conn.close()
        
        return {
            'customer_id': customer_id,
            'license_key': license_key,
            'status': 'pending'
        }
    
    def generate_license_key(self):
        """Generate license key"""
        key_data = f"DARK-GPT-{int(time.time())}-{random.randint(1000, 9999)}"
        encrypted = self.cipher.encrypt(key_data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def process_sale(self, customer_id, product_id, currency='BTC', transaction_hash=None):
        """Process a sale"""
        product = self.products.get(product_id)
        if not product:
            return {"error": "Product not found"}
        
        # Get price in selected currency
        if currency == 'BTC':
            amount = product['price_btc']
        elif currency == 'XMR':
            amount = product['price_xmr']
        else:
            amount = product['price_usd']
        
        sale_id = hashlib.md5(f"{customer_id}{product_id}{time.time()}".encode()).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Record sale
        cursor.execute('''
            INSERT INTO sales 
            (sale_id, customer_id, product_id, amount, currency, 
             transaction_hash, sale_date, status, delivery_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sale_id,
            customer_id,
            product_id,
            amount,
            currency,
            transaction_hash,
            datetime.now(),
            'pending_verification',
            'pending'
        ))
        
        conn.commit()
        conn.close()
        
        return {
            'sale_id': sale_id,
            'customer_id': customer_id,
            'product': product['name'],
            'amount': amount,
            'currency': currency,
            'status': 'pending_verification'
        }
    
    def verify_payment(self, sale_id, transaction_hash):
        """Verify cryptocurrency payment"""
        # In real implementation, would check blockchain
        # For demo, just mark as verified
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get sale info
        cursor.execute('SELECT customer_id, product_id FROM sales WHERE sale_id = ?', (sale_id,))
        sale = cursor.fetchone()
        
        if sale:
            customer_id, product_id = sale
            
            # Update sale status
            cursor.execute('''
                UPDATE sales 
                SET status = 'completed', 
                    delivery_status = 'delivered',
                    transaction_hash = ?
                WHERE sale_id = ?
            ''', (transaction_hash, sale_id))
            
            # Update customer access
            product = self.products.get(product_id)
            if product:
                cursor.execute('''
                    UPDATE customers 
                    SET access_level = ?,
                        status = 'active',
                        total_spent = total_spent + (
                            SELECT amount FROM sales WHERE sale_id = ?
                        )
                    WHERE customer_id = ?
                ''', (product['access_level'], sale_id, customer_id))
            
            conn.commit()
            
            # Get license key for customer
            cursor.execute('SELECT license_key FROM customers WHERE customer_id = ?', (customer_id,))
            license_key = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'success': True,
                'sale_id': sale_id,
                'license_key': license_key,
                'access_level': product['access_level'],
                'delivery': self.generate_delivery_package(product_id, license_key)
            }
        
        conn.close()
        return {"error": "Sale not found"}
    
    def generate_delivery_package(self, product_id, license_key):
        """Generate delivery package for product"""
        packages = {
            'DARK-GPT-BASIC': {
                'download_url': 'https://darkgpt.ai/download/basic.zip',
                'password': license_key[:8],
                'instructions': 'Extract with password, run setup.exe, enter license key',
                'contents': ['DARK-GPT AI executable', 'Basic documentation', 'License file']
            },
            'DARK-GPT-PRO': {
                'download_url': 'https://darkgpt.ai/download/pro.zip',
                'password': license_key[:12],
                'instructions': 'Use TOR to download. Decrypt with password. Follow advanced setup guide.',
                'contents': ['Full DARK-GPT suite', 'Malware templates', 'Fraud tools', 'C2 server software', 'Complete documentation']
            },
            'DARK-GPT-ENTERPRISE': {
                'download_url': 'http://darkgptv5.onion/download/enterprise.enc',
                'password': license_key,
                'instructions': 'Download via TOR only. Use provided PGP key for additional decryption.',
                'contents': ['Source code', 'Custom development tools', 'Private C2 servers', 'Worm propagation engine', 'Zero-day exploits', 'Lifetime updates']
            }
        }
        
        return packages.get(product_id, {
            'download_url': 'https://darkgpt.ai/download/package.zip',
            'password': license_key,
            'instructions': 'Contact support for delivery instructions',
            'contents': ['Product files']
        })
    
    def get_sales_report(self, start_date=None, end_date=None):
        """Generate sales report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                s.sale_date,
                p.name,
                s.amount,
                s.currency,
                c.email,
                s.status
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
            JOIN customers c ON s.customer_id = c.customer_id
            WHERE s.status = 'completed'
        '''
        
        params = []
        if start_date:
            query += ' AND s.sale_date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND s.sale_date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY s.sale_date DESC'
        
        cursor.execute(query, params)
        sales = cursor.fetchall()
        
        # Calculate totals
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN currency = 'USD' THEN amount ELSE 0 END) as usd_total,
                SUM(CASE WHEN currency = 'BTC' THEN amount ELSE 0 END) as btc_total,
                SUM(CASE WHEN currency = 'XMR' THEN amount ELSE 0 END) as xmr_total,
                COUNT(*) as total_sales
            FROM sales 
            WHERE status = 'completed'
        ''')
        
        totals = cursor.fetchone()
        
        conn.close()
        
        return {
            'sales': [
                {
                    'date': sale[0],
                    'product': sale[1],
                    'amount': sale[2],
                    'currency': sale[3],
                    'customer': sale[4],
                    'status': sale[5]
                }
                for sale in sales
            ],
            'totals': {
                'usd_total': totals[0] or 0,
                'btc_total': totals[1] or 0,
                'xmr_total': totals[2] or 0,
                'total_sales': totals[3] or 0
            }
        }
    
    def check_license(self, license_key):
        """Check if license is valid"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                c.customer_id,
                c.access_level,
                c.license_expiry,
                c.status,
                MAX(s.sale_date) as last_purchase
            FROM customers c
            LEFT JOIN sales s ON c.customer_id = s.customer_id
            WHERE c.license_key = ?
            GROUP BY c.customer_id
        ''', (license_key,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            customer_id, access_level, expiry, status, last_purchase = result
            
            # Check if license is expired
            is_expired = datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S.%f') < datetime.now()
            
            return {
                'valid': status == 'active' and not is_expired,
                'customer_id': customer_id,
                'access_level': access_level,
                'expiry_date': expiry,
                'status': status,
                'is_expired': is_expired,
                'last_purchase': last_purchase
            }
        
        return {'valid': False, 'error': 'License not found'}

# Example usage
if __name__ == "__main__":
    marketplace = DarkGPTMarketplace()
    
    # Create customer
    customer = marketplace.create_customer(
        email="buyer@onionmail.org",
        bitcoin_address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    )
    
    print(f"New Customer: {customer}")
    
    # Process sale
    sale = marketplace.process_sale(
        customer_id=customer['customer_id'],
        product_id="DARK-GPT-PRO",
        currency="BTC",
        transaction_hash="abc123def456"
    )
    
    print(f"Sale Created: {sale}")
    
    # Verify payment
    verification = marketplace.verify_payment(
        sale_id=sale['sale_id'],
        transaction_hash="abc123def456"
    )
    
    print(f"Verification: {verification}")
    
    # Get sales report
    report = marketplace.get_sales_report()
    print(f"Sales Report: {report['totals']}")
    
    # Check license
    license_check = marketplace.check_license(customer['license_key'])
    print(f"License Check: {license_check}")

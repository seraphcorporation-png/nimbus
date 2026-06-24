import sqlite3
import random
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'inventory.sqlite')

MAKES_MODELS = {
    'Toyota': ['Camry', 'Corolla', 'RAV4', 'Highlander', 'Tacoma', 'Prius'],
    'Lexus': ['RX 350', 'ES 350', 'NX 300', 'IS 300', 'UX 250h'],
    'Volkswagen': ['Jetta', 'Tiguan', 'Atlas', 'Golf GTI', 'ID.4'],
    'Porsche': ['911', 'Cayenne', 'Macan', 'Panamera', 'Taycan'],
    'Subaru': ['Outback', 'Forester', 'Crosstrek', 'Impreza', 'WRX'],
    'Audi': ['Q5', 'A4', 'Q3', 'Q7', 'e-tron']
}

COLORS = ['Midnight Black', 'Blizzard Pearl', 'Magnetic Gray', 'Celestial Silver', 'Ruby Flare', 'Blueprint']
TRIMS = ['Base', 'Premium', 'Limited', 'Sport', 'Touring', 'Platinum', 'AWD']
ZIPS = ['90210', '90001', '90012', '90028', '90045'] # LA area zips

DEALERSHIPS = [
    {"name": "LA Car Guy - Pacific Porsche", "address": "2900 Pacific Coast Hwy, Torrance, CA 90505"},
    {"name": "LA Car Guy - Santa Monica Audi", "address": "1020 Santa Monica Blvd, Santa Monica, CA 90401"},
    {"name": "LA Car Guy - Toyota of Hollywood", "address": "6000 Hollywood Blvd, Los Angeles, CA 90028"},
    {"name": "LA Car Guy - Volkswagen Santa Monica", "address": "2440 Santa Monica Blvd, Santa Monica, CA 90404"},
    {"name": "LA Car Guy - Subaru Pacific", "address": "2775 Pacific Coast Hwy, Hermosa Beach, CA 90254"}
]

def generate_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            make TEXT,
            model TEXT,
            trim TEXT,
            color TEXT,
            price INTEGER,
            monthly_estimate INTEGER,
            zip_code TEXT,
            status TEXT,
            image_url TEXT,
            dealership_name TEXT,
            dealership_address TEXT
        )
    ''')
    
    vehicles = []
    for _ in range(2500):
        make = random.choice(list(MAKES_MODELS.keys()))
        model = random.choice(MAKES_MODELS[make])
        year = random.choices([2024, 2025, 2026], weights=[0.2, 0.5, 0.3])[0]
        trim = random.choice(TRIMS)
        color = random.choice(COLORS)
        zip_code = random.choice(ZIPS)
        status = random.choices(['In Stock', 'In Transit'], weights=[0.8, 0.2])[0]
        
        # Base prices depending on brand
        base_price = random.randint(25000, 45000)
        if make in ['Porsche', 'Lexus', 'Audi']:
            base_price = random.randint(45000, 120000)
            
        # Simplified monthly calculation based on price
        monthly = int(base_price / 72) + random.randint(10, 50) 
        
        # Assign accurate images based on model type
        image_url = "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=1200&auto=format&fit=crop" # Generic fallback car
        
        if make == 'Porsche':
            if model == '911' or model == 'Taycan' or model == 'Panamera':
                image_url = "https://images.unsplash.com/photo-1503376713356-d8fdf67eb81f?w=1200&auto=format&fit=crop" # Porsche sports car
            else:
                image_url = "https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e?w=1200&auto=format&fit=crop" # Porsche SUV
        elif make == 'Toyota':
            if model in ['RAV4', 'Highlander']:
                image_url = "https://images.unsplash.com/photo-1625049596644-b040c1ceb768?w=1200&auto=format&fit=crop" # SUV
            elif model == 'Tacoma':
                image_url = "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=1200&auto=format&fit=crop" # Truck/Offroad
            else:
                image_url = "https://images.unsplash.com/photo-1629897048514-3dd74143fe27?w=1200&auto=format&fit=crop" # Sedan
        elif make == 'Audi':
            if model in ['Q5', 'Q3', 'Q7', 'e-tron']:
                image_url = "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=1200&auto=format&fit=crop" # Audi SUV
            else:
                image_url = "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?w=1200&auto=format&fit=crop" # Audi Sedan
        elif make == 'Volkswagen':
            if model in ['Tiguan', 'Atlas', 'ID.4']:
                image_url = "https://images.unsplash.com/photo-1620891549027-942fdc95d3f5?w=1200&auto=format&fit=crop" # VW SUV
            else:
                image_url = "https://images.unsplash.com/photo-1542282088-fe8426682b8f?w=1200&auto=format&fit=crop" # VW hatchback/sedan
        elif make == 'Lexus':
            if model in ['RX 350', 'NX 300', 'UX 250h']:
                image_url = "https://images.unsplash.com/photo-1532581140115-3e355d1ed1de?w=1200&auto=format&fit=crop" # SUV
            else:
                image_url = "https://images.unsplash.com/photo-1550529323-e18e3851b439?w=1200&auto=format&fit=crop" # Lexus sedan
        elif make == 'Subaru':
            image_url = "https://images.unsplash.com/photo-1534723328310-e82dad3ee43f?w=1200&auto=format&fit=crop" # Offroad / Subaru vibe
            
        # Assign a mock dealership based loosely on make
        dealer = random.choice(DEALERSHIPS)
        if make == 'Porsche':
            dealer = DEALERSHIPS[0]
        elif make == 'Audi':
            dealer = DEALERSHIPS[1]
        elif make == 'Toyota':
            dealer = DEALERSHIPS[2]
        elif make == 'Volkswagen':
            dealer = DEALERSHIPS[3]
        elif make == 'Subaru':
            dealer = DEALERSHIPS[4]
        
        vehicles.append((year, make, model, trim, color, base_price, monthly, zip_code, status, image_url, dealer['name'], dealer['address']))
        
    cursor.executemany('''
        INSERT INTO vehicles (year, make, model, trim, color, price, monthly_estimate, zip_code, status, image_url, dealership_name, dealership_address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', vehicles)
    
    conn.commit()
    conn.close()
    print(f"Successfully generated database with 2500 mock vehicles at {DB_PATH}")

if __name__ == '__main__':
    generate_db()

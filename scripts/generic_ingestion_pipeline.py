import sqlite3
import json
import os
import requests

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'inventory.sqlite')
API_URL = "https://api.example-dealership.com/v1/inventory"
API_KEY = "your_partner_api_key_here"

def fetch_inventory():
    print(f"Fetching latest inventory from {API_URL}...")
    # This is a mock API call. In production, uncomment the requests code.
    '''
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    response = requests.get(API_URL, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.text}")
    return response.json()
    '''
    # Mock data to demonstrate the ingestion pipeline
    return [
        {
            "id": "1001",
            "year": 2025,
            "make": "Toyota",
            "model": "Camry",
            "trim": "XLE",
            "color": "Midnight Black",
            "price": 31500,
            "zip_code": "90210",
            "status": "In Stock",
            "image_url": "https://images.unsplash.com/photo-1629897048514-3dd74143fe27?q=80&w=2000&auto=format&fit=crop"
        }
    ]

def ingest_to_db(inventory_data):
    if not os.path.exists(DB_PATH):
        raise Exception(f"Database not found at {DB_PATH}. Please run the generator script first.")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # In a real scenario, you'd likely UPDATE ON CONFLICT or clear stale inventory.
    # We will do a simple INSERT for demonstration.
    inserted = 0
    for item in inventory_data:
        try:
            monthly_est = int(item['price'] / 72) + 30 # Rough finance estimate
            
            cursor.execute('''
                INSERT INTO vehicles (year, make, model, trim, color, price, monthly_estimate, zip_code, status, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['year'], item['make'], item['model'], item['trim'], 
                item['color'], item['price'], monthly_est, 
                item['zip_code'], item['status'], item['image_url']
            ))
            inserted += 1
        except Exception as e:
            print(f"Failed to insert item {item.get('id')}: {e}")
            
    conn.commit()
    conn.close()
    print(f"Successfully ingested {inserted} vehicles into the local database.")

def main():
    try:
        data = fetch_inventory()
        ingest_to_db(data)
    except Exception as e:
        print(f"Ingestion pipeline failed: {e}")

if __name__ == "__main__":
    main()

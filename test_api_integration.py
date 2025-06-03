#!/usr/bin/env python
"""
Test script to verify the Django backend API integration with frontend requirements.
This script tests the corrected category structure and new API endpoints.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

def test_category_choices():
    """Test the category choices endpoint"""
    print("Testing category choices endpoint...")
    
    response = requests.get(f"{BASE_URL}/competitor-prices/get_category_choices/")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Category choices endpoint working")
        print(f"Categories: {list(data['sku_categories'].keys())}")
        print(f"Sizes: {list(data['sku_sizes'].keys())}")
        print(f"Markets: {list(data['market_types'].keys())}")
        
        # Verify correct categories
        expected_categories = ['NUTRITION', 'ORAL CARE', 'DEODORANT', 'SKIN CARE', 'SALVORY']
        actual_categories = list(data['sku_categories'].keys())
        
        if set(expected_categories) == set(actual_categories):
            print("✅ Categories match frontend requirements")
        else:
            print(f"❌ Category mismatch. Expected: {expected_categories}, Got: {actual_categories}")
    else:
        print(f"❌ Category choices endpoint failed: {response.status_code}")
        print(response.text)

def test_create_price_entry():
    """Test the new create_price_entry endpoint"""
    print("\nTesting create price entry endpoint...")
    
    test_data = {
        "sku_category": "NUTRITION",
        "sku_size": "BULK PACK",
        "sku_name": "Test Product",
        "brand": "Test Brand",
        "market_type": "OPEN_MARKET",
        "price": 150.00,
        "is_unilever": True,
        "location": "Lagos"
    }
    
    response = requests.post(
        f"{BASE_URL}/competitor-prices/create_price_entry/",
        headers=HEADERS,
        data=json.dumps(test_data)
    )
    
    if response.status_code == 201:
        print("✅ Create price entry endpoint working")
        data = response.json()
        print(f"Created record ID: {data.get('id')}")
        print(f"Open market price: {data.get('open_market_price')}")
    else:
        print(f"❌ Create price entry failed: {response.status_code}")
        print(response.text)

def test_standard_create():
    """Test the standard create endpoint"""
    print("\nTesting standard create endpoint...")
    
    test_data = {
        "sku_category": "ORAL CARE",
        "sku_size": "REGULAR PACK",
        "sku_name": "Test Oral Care Product",
        "brand": "Test Brand",
        "open_market_price": 75.50,
        "ng_price": 80.00,
        "is_unilever": False,
        "location": "Lagos"
    }
    
    response = requests.post(
        f"{BASE_URL}/competitor-prices/",
        headers=HEADERS,
        data=json.dumps(test_data)
    )
    
    if response.status_code == 201:
        print("✅ Standard create endpoint working")
        data = response.json()
        print(f"Created record ID: {data.get('id')}")
        print(f"Category: {data.get('sku_category')}")
    else:
        print(f"❌ Standard create failed: {response.status_code}")
        print(response.text)

def test_invalid_category():
    """Test validation with invalid category"""
    print("\nTesting invalid category validation...")
    
    test_data = {
        "sku_category": "INVALID_CATEGORY",
        "sku_size": "BULK PACK",
        "sku_name": "Test Product",
        "brand": "Test Brand",
        "market_type": "OPEN_MARKET",
        "price": 150.00
    }
    
    response = requests.post(
        f"{BASE_URL}/competitor-prices/create_price_entry/",
        headers=HEADERS,
        data=json.dumps(test_data)
    )
    
    if response.status_code == 400:
        print("✅ Invalid category validation working")
        print(f"Error message: {response.json()}")
    else:
        print(f"❌ Invalid category validation failed: {response.status_code}")

def main():
    """Run all tests"""
    print("🧪 Testing Django Backend API Integration")
    print("=" * 50)
    
    try:
        test_category_choices()
        test_create_price_entry()
        test_standard_create()
        test_invalid_category()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("\n📋 API Endpoints Available:")
        print(f"  GET  {BASE_URL}/competitor-prices/get_category_choices/")
        print(f"  POST {BASE_URL}/competitor-prices/create_price_entry/")
        print(f"  GET  {BASE_URL}/competitor-prices/")
        print(f"  POST {BASE_URL}/competitor-prices/")
        print(f"  GET  {BASE_URL}/competitor-prices/{{id}}/")
        print(f"  PUT  {BASE_URL}/competitor-prices/{{id}}/")
        print(f"  DELETE {BASE_URL}/competitor-prices/{{id}}/")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Django server.")
        print("Make sure the Django development server is running:")
        print("  python manage.py runserver")

if __name__ == "__main__":
    main()

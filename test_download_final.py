#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

# Login
session = requests.Session()
login_response = session.get('https://pro.manserv.com.br/login')
soup = BeautifulSoup(login_response.text, 'html.parser')
token = soup.find('input', {'name': '_token'})['value']

login_data = {
    '_token': token,
    'client-email': 'wesley.luz@manserv.com.br',
    'client-password': '028885'
}

login_result = session.post('https://pro.manserv.com.br/login', data=login_data)
print(f"Login status: {login_result.status_code}")

# Filter
filter_params = {
    'beginDate': '01/08/2025',
    'endDate': '31/08/2025',
    'id': '',
    'checklistId': '',
    'userId': '',
    'assetId': ''
}

filter_response = session.get('https://pro.manserv.com.br/operational/checklist-results', params=filter_params)
print(f"Filter status: {filter_response.status_code}")

# Get CSRF token for export
soup2 = BeautifulSoup(filter_response.text, 'html.parser')
csrf_meta = soup2.find('meta', {'name': 'csrf-token'})
token2 = csrf_meta['content'] if csrf_meta else ''
print(f"CSRF token found: {bool(token2)}")

# Export
export_data = {
    '_token': token2,
    'beginDate': '01/08/2025',
    'endDate': '31/08/2025',
    'id': '',
    'checklistId': '',
    'userId': '',
    'assetId': ''
}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://pro.manserv.com.br/operational/checklist-results'
}

download_response = session.post('https://pro.manserv.com.br/operational/checklist-results-export', data=export_data, headers=headers)

print(f"Download status: {download_response.status_code}")
print(f"Content-Type: {download_response.headers.get('Content-Type', 'N/A')}")
print(f"Content-Length: {len(download_response.content)}")
print(f"First 200 chars: {repr(download_response.content[:200])}")

# Save file
Path('test_file.xls').write_bytes(download_response.content)
print("File saved as test_file.xls")

# Try to read with pandas
try:
    df = pd.read_excel('test_file.xls', engine='xlrd')
    print(f"Excel file read successfully! Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
except Exception as e:
    print(f"Error reading Excel: {e}")
    
    # Try to read as text
    try:
        with open('test_file.xls', 'r', encoding='utf-8') as f:
            content = f.read(500)
            print(f"File content (first 500 chars): {content}")
    except:
        print("Could not read as text either")
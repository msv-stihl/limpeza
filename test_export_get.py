#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

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

# Access reports page first
filter_response = session.get('https://pro.manserv.com.br/operational/checklist-results')
print(f"Reports page status: {filter_response.status_code}")

# Apply filters first
filter_params = {
    'beginDate': '01/01/2024',
    'endDate': '31/01/2024',
    'environment': '',
    'asset': '',
    'checklist': '',
    'status': ''
}

# Get CSRF token from filter page
soup2 = BeautifulSoup(filter_response.text, 'html.parser')
csrf_token = soup2.find('input', {'name': '_token'})
if csrf_token:
    filter_params['_token'] = csrf_token.get('value')

# Apply filters
filtered_response = session.post('https://pro.manserv.com.br/operational/checklist-results', data=filter_params)
print(f"Filter status: {filtered_response.status_code}")

# Now try export with GET method
print("\n=== TESTING EXPORT WITH GET ===")
export_params = {
    'beginDate': '01/01/2024',
    'endDate': '31/01/2024',
    'environment': '',
    'asset': '',
    'checklist': '',
    'status': '',
    'format': 'excel'
}

export_url = f"https://pro.manserv.com.br/operational/checklist-results-export?{urlencode(export_params)}"
print(f"Export URL: {export_url}")

export_response = session.get(export_url)
print(f"Export GET status: {export_response.status_code}")
print(f"Content-Type: {export_response.headers.get('Content-Type', 'Unknown')}")
print(f"Content-Length: {len(export_response.content)}")
print(f"First 200 chars: {export_response.content[:200]}")

if len(export_response.content) > 0:
    with open('test_export_get.xls', 'wb') as f:
        f.write(export_response.content)
    print("File saved as test_export_get.xls")

# Also try POST with different parameters
print("\n=== TESTING EXPORT WITH POST (different params) ===")
export_data = {
    'beginDate': '01/01/2024',
    'endDate': '31/01/2024',
    'environment': '',
    'asset': '',
    'checklist': '',
    'status': '',
    '_token': filter_params.get('_token', '')
}

export_response2 = session.post('https://pro.manserv.com.br/operational/checklist-results-export', data=export_data)
print(f"Export POST status: {export_response2.status_code}")
print(f"Content-Type: {export_response2.headers.get('Content-Type', 'Unknown')}")
print(f"Content-Length: {len(export_response2.content)}")
print(f"First 200 chars: {export_response2.content[:200]}")

if len(export_response2.content) > 0:
    with open('test_export_post.xls', 'wb') as f:
        f.write(export_response2.content)
    print("File saved as test_export_post.xls")
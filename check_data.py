#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

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

# Access reports page
filter_response = session.get('https://pro.manserv.com.br/operational/checklist-results')
print(f"Reports page status: {filter_response.status_code}")

# Check if there are any data rows in the table
soup2 = BeautifulSoup(filter_response.text, 'html.parser')
tables = soup2.find_all('table')
print(f"Number of tables found: {len(tables)}")

if tables:
    # Look for data rows (excluding header)
    for i, table in enumerate(tables):
        rows = table.find_all('tr')
        print(f"Table {i+1}: {len(rows)} rows")
        if len(rows) > 1:  # More than just header
            print(f"Table {i+1} has data rows")
            # Show first few data rows
            for j, row in enumerate(rows[1:3]):  # Skip header, show first 2 data rows
                cells = row.find_all(['td', 'th'])
                print(f"  Row {j+1}: {len(cells)} cells")
                if cells:
                    print(f"    First cell: {cells[0].get_text(strip=True)[:50]}")
        else:
            print(f"Table {i+1} has only header row - no data")
else:
    print("No tables found on the page")
    print("Page content (first 1000 chars):")
    print(filter_response.text[:1000])

# Try to find export button or form
export_forms = soup2.find_all('form')
print(f"\nNumber of forms found: {len(export_forms)}")
for i, form in enumerate(export_forms):
    action = form.get('action', 'No action')
    method = form.get('method', 'No method')
    print(f"Form {i+1}: action='{action}', method='{method}'")
    
    # Look for export-related inputs
    inputs = form.find_all('input')
    for inp in inputs:
        inp_type = inp.get('type', '')
        inp_name = inp.get('name', '')
        inp_value = inp.get('value', '')
        if 'export' in inp_name.lower() or 'export' in inp_value.lower():
            print(f"  Export input: type='{inp_type}', name='{inp_name}', value='{inp_value}'")

# Look for export buttons
buttons = soup2.find_all('button')
export_buttons = [btn for btn in buttons if 'export' in btn.get_text().lower()]
print(f"\nExport buttons found: {len(export_buttons)}")
for btn in export_buttons:
    print(f"  Button text: '{btn.get_text(strip=True)}'")
    print(f"  Button attributes: {btn.attrs}")
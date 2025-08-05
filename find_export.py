#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

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

# Look for export-related elements
soup2 = BeautifulSoup(filter_response.text, 'html.parser')

# Search for export buttons, links, or forms
print("\n=== SEARCHING FOR EXPORT ELEMENTS ===")

# Look for buttons with export-related text
buttons = soup2.find_all('button')
for btn in buttons:
    btn_text = btn.get_text(strip=True).lower()
    if any(word in btn_text for word in ['export', 'excel', 'download', 'baixar', 'exportar']):
        print(f"Export button found: '{btn.get_text(strip=True)}'")
        print(f"  Attributes: {btn.attrs}")
        print(f"  Parent: {btn.parent.name if btn.parent else 'None'}")
        if btn.parent:
            print(f"  Parent attributes: {btn.parent.attrs}")
        print()

# Look for links with export-related text or URLs
links = soup2.find_all('a')
for link in links:
    link_text = link.get_text(strip=True).lower()
    href = link.get('href', '')
    if any(word in link_text for word in ['export', 'excel', 'download', 'baixar', 'exportar']) or \
       any(word in href for word in ['export', 'excel', 'download']):
        print(f"Export link found: '{link.get_text(strip=True)}'")
        print(f"  href: {href}")
        print(f"  Attributes: {link.attrs}")
        print()

# Look for forms that might handle export
forms = soup2.find_all('form')
for i, form in enumerate(forms):
    action = form.get('action', '')
    if 'export' in action or 'download' in action:
        print(f"Export form {i+1}: action='{action}'")
        print(f"  Method: {form.get('method', 'GET')}")
        print(f"  Attributes: {form.attrs}")
        
        # Show form inputs
        inputs = form.find_all('input')
        for inp in inputs:
            print(f"    Input: type='{inp.get('type', '')}', name='{inp.get('name', '')}', value='{inp.get('value', '')}'")
        print()

# Search for JavaScript that might handle export
scripts = soup2.find_all('script')
print("\n=== SEARCHING FOR EXPORT JAVASCRIPT ===")
for script in scripts:
    if script.string:
        script_content = script.string.lower()
        if any(word in script_content for word in ['export', 'excel', 'download']):
            print("Export-related JavaScript found:")
            # Show relevant lines
            lines = script.string.split('\n')
            for i, line in enumerate(lines):
                if any(word in line.lower() for word in ['export', 'excel', 'download']):
                    print(f"  Line {i+1}: {line.strip()}")
            print()

# Look for data attributes or onclick handlers
print("\n=== SEARCHING FOR DATA ATTRIBUTES AND ONCLICK ===")
all_elements = soup2.find_all(attrs={'onclick': True})
for elem in all_elements:
    onclick = elem.get('onclick', '')
    if any(word in onclick.lower() for word in ['export', 'excel', 'download']):
        print(f"Element with export onclick: {elem.name}")
        print(f"  onclick: {onclick}")
        print(f"  text: {elem.get_text(strip=True)[:100]}")
        print()

# Look for data-* attributes
all_elements = soup2.find_all()
for elem in all_elements:
    for attr, value in elem.attrs.items():
        if attr.startswith('data-') and isinstance(value, str):
            if any(word in value.lower() for word in ['export', 'excel', 'download']):
                print(f"Element with export data attribute: {elem.name}")
                print(f"  {attr}: {value}")
                print(f"  text: {elem.get_text(strip=True)[:100]}")
                print()
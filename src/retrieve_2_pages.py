import requests

base_url = 'http://127.0.0.1:8000/api/events'

# Retrieve Page 1
response_p1 = requests.get(base_url, params={'page': 1, 'per_page': 10})
data_p1 = response_p1.json()

print("--- PAGE 1 ---")
print(f"Total Records Available: {data_p1.get('total')}")
print(f"Has More Pages?: {data_p1.get('has_more')}")
print(f"Next Page: {data_p1.get('next_page')}")
print(f"Items fetched on page 1: {len(data_p1.get('items', []))}")

# Retrieve Page 2 manually using the next_page parameter
next_page_num = data_p1.get('next_page')
if next_page_num:
    response_p2 = requests.get(base_url, params={'page': next_page_num, 'per_page': 10})
    data_p2 = response_p2.json()
    
    print("\n--- PAGE 2 ---")
    print(f"Next Page: {data_p2.get('next_page')}")
    print(f"Items fetched on page 2: {len(data_p2.get('items', []))}")

# Why processing only page 1 would be an incomplete ingestion?
# The API splits records across multiple pages using pagination controls ('page', 'per_page', 'has_more')
# Processing only page 1 would capture a small subset of the total records, completely missing historical and ongoing data payloads, violating the requirement for full data capture.
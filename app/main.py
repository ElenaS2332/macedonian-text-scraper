import requests

url = "https://en.wikipedia.org/wiki/Macedonia"

response = requests.get(url)

if response.status_code == 200:
    print("✅ Page loaded successfully!")
    print(response.text[:1000])  
else:
    print("❌ Failed to load the page. Status code:", response.status_code)


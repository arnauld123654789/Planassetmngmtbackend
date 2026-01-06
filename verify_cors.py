import urllib.request as req

try:
    headers = {"Origin": "http://localhost:5173"}
    request = req.Request("http://localhost:8000/", headers=headers, method="GET")
    response = req.urlopen(request)
    print(f"Status: {response.getcode()}")
    print("Response Headers:")
    for header, value in response.headers.items():
        print(f"{header}: {value}")
except Exception as e:
    print(f"Error: {e}")

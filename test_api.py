import requests
import json

# Load data from data.json
with open('data.json', 'r') as f:
    test_data = json.load(f)

# Make the request
response = requests.post(
    "http://localhost:8000/transform",
    json=test_data,
    headers={"Content-Type": "application/json"}
)

# Print the response
print("Status Code:", response.status_code)
print("Response:")
print(json.dumps(response.json(), indent=2)) 
with open('response.json', 'w') as f:
    json.dump(response.json(), f, indent=2)

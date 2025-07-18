import requests

url = "http://00.00.00.00/wp-json/your-endpoint/data"
data = {"key": "value"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)

print(response.text)

import requests

response = requests.get('http://183.173.18.234:8182/poweroff1')
print(response.text)
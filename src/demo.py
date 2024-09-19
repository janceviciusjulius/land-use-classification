import requests

response = requests.get("https://www.rightwingwatch.org/post/right-wing-round-up-140-people/")  # 301
print(response.status_code)

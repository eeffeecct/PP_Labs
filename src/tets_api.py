import requests

try:
    response = requests.get("https://api.chucknorris.io/jokes/random", timeout=10)
    print(response.json()['value'])
except Exception as e:
    print(f"Ошибка: {e}")
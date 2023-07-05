import requests

url = "http://127.0.0.1:8000/api/v1/partner/update"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Token de088032db066d0cc78f023dcb6036d29d781f28"
}


data = {
    "url": "https://raw.githubusercontent.com/s-evg/python-final-diplom/master/data/shop1.yaml"
}

response = requests.post(url, headers=headers, json=data)
print(response.json())

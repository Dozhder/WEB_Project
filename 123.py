import requests


res = requests.post('http://127.0.0.1:8080/api/users', headers={'X-API-KEY': 'secret_api_key'},
                    json={'name': 'currier', 'email': 'currier@currier', 'access': 1, 'password': 1})
print(res)
res = requests.post('http://127.0.0.1:8080/api/users', headers={'X-API-KEY': 'secret_api_key'},
                    json={'name': 'eatery', 'email': 'eatery@eatery', 'access': 2, 'password': 1})
print(res)

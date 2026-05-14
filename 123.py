import requests


res = requests.post('http://127.0.0.1:5000/api/users', headers={'X-API-KEY': 'secret_api_key'},
                    json={'name': 'currier', 'email': 'currier@currier', 'access': 1, 'password': 1})
print(res)
res = requests.post('http://127.0.0.1:5000/api/users', headers={'X-API-KEY': 'secret_api_key'},
                    json={'name': 'eatery', 'email': 'eatery@eatery', 'access': 2, 'password': 1})
print(res)
res = requests.post('http://127.0.0.1:5000/api/eateries', headers={'X-API-KEY': 'secret_api_key'},
                    json={'name': 'eatery_1', 'address': 'Eatery st.', 'chief_id': 2, 'staff': '2, 1'})
print(res)



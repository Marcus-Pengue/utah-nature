import requests
import json

username = 'marcuspengue@gmail.com'
password = 'hDmk6U!9p3CcCzZ'

url = 'https://motus.org/api/receivers'

# Try many date formats
dates = [
    {'date': '2024/01/01'},
    {'date': '01-01-2024'},
    {'date': '01/01/2024'},
    {'dateStart': '2024-01-01'},
    {'startDate': '2024-01-01'},
    {'since': '2024-01-01'},
    {'modifiedSince': '2024-01-01'},
]

for d in dates:
    data = {'json': json.dumps(d)}
    r = requests.post(url, data=data, auth=(username, password), timeout=10)
    status = 'OK' if r.status_code == 200 else r.status_code
    print(f'{list(d.keys())[0]}: {status}')
    if r.status_code == 200:
        print(r.text[:300])
        break

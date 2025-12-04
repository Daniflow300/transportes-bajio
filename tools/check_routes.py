import requests

base = 'http://127.0.0.1:5000'
paths = ['/', '/login', '/register', '/mi_informacion']

for p in paths:
    try:
        r = requests.get(base + p, timeout=5)
        print(f"{p}: {r.status_code} (len={len(r.text)})")
    except Exception as e:
        print(f"{p}: ERROR -> {e}")

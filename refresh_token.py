import requests
import json

def get_access_token(client_id, client_secret, refresh_token):
    payload = {'client_id': client_id, 'client_secret': client_secret, 'refresh_token': refresh_token, 'grant_type': 'refresh_token'}
    url = 'https://accounts.google.com/o/oauth2/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Host': 'accounts.google.com'}
    r = requests.post(url, data=payload, headers=headers)
    return json.loads(r.text)['access_token']


from requests.auth import HTTPBasicAuth
import requests

def fetch_data(type, offset, limit, API_EMAIL, API_KEY):
    url = f"https://api.oneup.com/v1/{type}?limit={limit}&offset={offset}&sort=-created_at"

    response = requests.get(url, auth=HTTPBasicAuth(API_EMAIL, API_KEY), verify=False)

    if response.status_code == 200:
        print("Success")
        data = response.json()
        return data
    else:
        error = f"Error {response.status_code}: {response.text}"
        return error

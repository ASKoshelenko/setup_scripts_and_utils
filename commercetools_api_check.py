import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_access_token():
    auth_url = os.getenv('CTP_AUTH_URL')
    client_id = os.getenv('CTP_CLIENT_ID')
    client_secret = os.getenv('CTP_CLIENT_SECRET')
    scopes = os.getenv('CTP_SCOPES')

    # Ensure the auth_url ends with /oauth/token
    if not auth_url.endswith('/oauth/token'):
        auth_url = auth_url.rstrip('/') + '/oauth/token'

    data = {
        'grant_type': 'client_credentials',
        'scope': scopes
    }

    print(f"Requesting token from: {auth_url}")
    print(f"Using client ID: {client_id}")
    print(f"Scopes: {scopes}")

    response = requests.post(
        auth_url,
        auth=(client_id, client_secret),
        data=data
    )

    if response.status_code != 200:
        print(f"Error response: {response.status_code} {response.text}")
    
    response.raise_for_status()
    return response.json()['access_token']

def get_api_clients(access_token):
    api_url = os.getenv('CTP_API_URL')
    project_key = os.getenv('CTP_PROJECT_KEY')

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    full_url = f"{api_url}/{project_key}/api-clients"
    print(f"Requesting API clients from: {full_url}")

    response = requests.get(full_url, headers=headers)

    if response.status_code != 200:
        print(f"Error response: {response.status_code} {response.text}")
    
    response.raise_for_status()
    return response.json()['results']

def main():
    try:
        print("Getting access token...")
        access_token = get_access_token()
        print("Access token obtained successfully.")

        print("Fetching API clients...")
        clients = get_api_clients(access_token)
        print(f"Successfully retrieved {len(clients)} API clients.")

        for client in clients:
            print(f"Client ID: {client['id']}, Name: {client['name']}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
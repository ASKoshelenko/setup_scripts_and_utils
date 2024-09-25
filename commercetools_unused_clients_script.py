import os
import requests
import datetime
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(filename='commercetools_api_client_check.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
DAYS_THRESHOLD = 30
REPORT_FILENAME = 'unused_api_clients_report.txt'

def get_access_token():
    auth_url = os.getenv('CTP_AUTH_URL').rstrip('/') + '/oauth/token'
    client_id = os.getenv('CTP_CLIENT_ID')
    client_secret = os.getenv('CTP_CLIENT_SECRET')
    scopes = os.getenv('CTP_SCOPES')

    data = {
        'grant_type': 'client_credentials',
        'scope': scopes
    }

    logging.info("Requesting access token")
    response = requests.post(
        auth_url,
        auth=(client_id, client_secret),
        data=data
    )
    
    response.raise_for_status()
    logging.info("Access token obtained successfully")
    return response.json()['access_token']

def get_all_api_clients(access_token):
    api_url = os.getenv('CTP_API_URL')
    project_key = os.getenv('CTP_PROJECT_KEY')

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    all_clients = []
    offset = 0
    limit = 20  # API default limit

    while True:
        full_url = f"{api_url}/{project_key}/api-clients?offset={offset}&limit={limit}"
        logging.info(f"Fetching API clients from: {full_url}")
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        clients = data['results']
        all_clients.extend(clients)
        
        if len(clients) < limit:
            break
        
        offset += limit

    logging.info(f"Total API clients retrieved: {len(all_clients)}")
    return all_clients

def is_client_unused(client, threshold_date):
    last_used = client.get('lastUsedAt')
    if not last_used:
        return True
    last_used_date = datetime.datetime.fromisoformat(last_used.rstrip('Z')).replace(tzinfo=datetime.timezone.utc)
    return last_used_date < threshold_date

def identify_unused_clients(clients, days_threshold=DAYS_THRESHOLD):
    threshold_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_threshold)
    unused_clients = [
        {
            'id': client['id'],
            'name': client['name'],
            'lastUsedAt': client.get('lastUsedAt', 'Never used')
        }
        for client in clients
        if is_client_unused(client, threshold_date)
    ]
    logging.info(f"Identified {len(unused_clients)} unused API clients")
    return unused_clients

def generate_report(unused_clients):
    report_lines = ["Unused API Clients Report", "=========================", ""]
    report_lines.extend([
        f"Client ID: {client['id']}\n"
        f"Name: {client['name']}\n"
        f"Last Used: {client['lastUsedAt']}\n"
        "-------------------------"
        for client in unused_clients
    ])
    
    with open(REPORT_FILENAME, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    logging.info(f"Report generated: {REPORT_FILENAME}")
    print(f"Report generated: {REPORT_FILENAME}")

def main():
    try:
        logging.info("Starting Commercetools API client check process")
        
        access_token = get_access_token()
        
        clients = get_all_api_clients(access_token)
        
        unused_clients = identify_unused_clients(clients)
        
        generate_report(unused_clients)
        
        logging.info("Process completed successfully")
        print("Process completed successfully")
    except requests.exceptions.RequestException as e:
        error_message = f"An error occurred: {str(e)}"
        logging.error(error_message)
        print(error_message)

if __name__ == "__main__":
    main()
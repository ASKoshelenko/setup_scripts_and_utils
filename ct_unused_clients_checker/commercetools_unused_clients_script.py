#!/usr/bin/env python
"""
Commercetools Unused API Clients Script

This script identifies and reports unused API clients in Commercetools projects.
It can process multiple projects defined in the environment variables and
generate reports for each project.

Usage:
    ./commercetools_unused_clients_script.py [project_key]

    If project_key is not provided, the script will process all available projects.

Environment Variables:
    For each project, the following environment variables should be set:
    {PROJECT_PREFIX}_CTP_PROJECT_KEY
    {PROJECT_PREFIX}_CTP_CLIENT_SECRET
    {PROJECT_PREFIX}_CTP_CLIENT_ID
    {PROJECT_PREFIX}_CTP_AUTH_URL
    {PROJECT_PREFIX}_CTP_API_URL
    {PROJECT_PREFIX}_CTP_SCOPES

    Where {PROJECT_PREFIX} is one of the keys defined in the PROJECTS dictionary.

Dependencies:
    - requests
    - python-dotenv

Author: [Your Name]
Date: [Current Date]
Version: 1.1
"""

import os
import requests
import datetime
import logging
import argparse
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create directories for logs and reports
os.makedirs('logs', exist_ok=True)
os.makedirs('reports', exist_ok=True)

# Configure logging
logging.basicConfig(filename='logs/commercetools_api_client_check.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
DAYS_THRESHOLD = 30
REPORT_FILENAME = 'reports/unused_api_clients_report_{}.txt'

# Available projects with short keys
PROJECTS = {
    'dev': 'PT_D2C_PRO_ESHOP_DEV',
    'stage': 'PT_D2C_PRO_ESHOP_STAGE',
    'preprod': 'PT_D2C_PRO_ESHOP_PRE_PROD',
    'prod': 'PT_D2C_PRO_ESHOP_PROD',
    'diy': 'PT_D2C_DIY_ESHOP'
}

def get_project_env(project: str) -> Optional[Dict[str, str]]:
    """
    Retrieve environment variables for a specific project.

    Args:
        project (str): The project identifier.

    Returns:
        Optional[Dict[str, str]]: A dictionary of environment variables if all are set, None otherwise.
    """
    env = {
        'CTP_PROJECT_KEY': os.getenv(f'{project}_CTP_PROJECT_KEY'),
        'CTP_CLIENT_SECRET': os.getenv(f'{project}_CTP_CLIENT_SECRET'),
        'CTP_CLIENT_ID': os.getenv(f'{project}_CTP_CLIENT_ID'),
        'CTP_AUTH_URL': os.getenv(f'{project}_CTP_AUTH_URL'),
        'CTP_API_URL': os.getenv(f'{project}_CTP_API_URL'),
        'CTP_SCOPES': os.getenv(f'{project}_CTP_SCOPES')
    }
    return env if all(env.values()) else None

def get_access_token(env: Dict[str, str]) -> str:
    """
    Obtain an access token from Commercetools API.

    Args:
        env (Dict[str, str]): Environment variables for the project.

    Returns:
        str: The access token.

    Raises:
        requests.exceptions.RequestException: If the token request fails.
    """
    auth_url = env['CTP_AUTH_URL'].rstrip('/') + '/oauth/token'
    data = {
        'grant_type': 'client_credentials',
        'scope': env['CTP_SCOPES']
    }

    logging.info("Requesting access token")
    response = requests.post(
        auth_url,
        auth=(env['CTP_CLIENT_ID'], env['CTP_CLIENT_SECRET']),
        data=data
    )
    
    response.raise_for_status()
    logging.info("Access token obtained successfully")
    return response.json()['access_token']

def get_all_api_clients(access_token: str, env: Dict[str, str]) -> List[Dict]:
    """
    Retrieve all API clients for a project from Commercetools.

    Args:
        access_token (str): The access token for authentication.
        env (Dict[str, str]): Environment variables for the project.

    Returns:
        List[Dict]: A list of API client dictionaries.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    api_url = env['CTP_API_URL']
    project_key = env['CTP_PROJECT_KEY']
    headers = {'Authorization': f'Bearer {access_token}'}

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

def is_client_unused(client: Dict, threshold_date: datetime.datetime) -> bool:
    """
    Check if a client is unused based on the threshold date.

    Args:
        client (Dict): The client dictionary.
        threshold_date (datetime.datetime): The date to compare against.

    Returns:
        bool: True if the client is unused, False otherwise.
    """
    last_used = client.get('lastUsedAt')
    if not last_used:
        return True
    last_used_date = datetime.datetime.fromisoformat(last_used.rstrip('Z')).replace(tzinfo=datetime.timezone.utc)
    return last_used_date < threshold_date

def identify_unused_clients(clients: List[Dict], days_threshold: int = DAYS_THRESHOLD) -> List[Dict]:
    """
    Identify API clients that haven't been used within the specified number of days.

    Args:
        clients (List[Dict]): List of API clients to check.
        days_threshold (int): Number of days for the usage threshold.

    Returns:
        List[Dict]: List of unused clients.
    """
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

def generate_report(unused_clients: List[Dict], project: str) -> None:
    """
    Generate a report of unused API clients.

    Args:
        unused_clients (List[Dict]): List of unused clients.
        project (str): The project identifier.
    """
    report_filename = REPORT_FILENAME.format(project.lower().replace('_', '-'))
    report_lines = [f"Unused API Clients Report for {project}", "="*40, ""]
    report_lines.extend([
        f"Client ID: {client['id']}\n"
        f"Name: {client['name']}\n"
        f"Last Used: {client['lastUsedAt']}\n"
        "-------------------------"
        for client in unused_clients
    ])
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    logging.info(f"Report generated: {report_filename}")
    print(f"Report generated: {report_filename}")

def process_project(project: str) -> None:
    """
    Process a single project to identify unused API clients.

    Args:
        project (str): The project identifier.
    """
    try:
        logging.info(f"Starting Commercetools API client check process for project: {project}")
        
        env = get_project_env(project)
        if not env:
            logging.warning(f"Skipping project {project}: Missing or incomplete environment variables")
            return
        
        access_token = get_access_token(env)
        clients = get_all_api_clients(access_token, env)
        unused_clients = identify_unused_clients(clients)
        generate_report(unused_clients, project)
        
        logging.info(f"Process completed successfully for project: {project}")
        print(f"Process completed successfully for project: {project}")
    except requests.exceptions.RequestException as e:
        error_message = f"An error occurred for project {project}: {str(e)}"
        logging.error(error_message)
        print(error_message)
    except ValueError as e:
        error_message = f"Configuration error for project {project}: {str(e)}"
        logging.error(error_message)
        print(error_message)

def main(project_key: Optional[str] = None) -> None:
    """
    Main function to process projects and identify unused API clients.

    Args:
        project_key (Optional[str]): The key of the project to process. If None, all projects are processed.
    """
    if project_key:
        if project_key not in PROJECTS:
            print(f"Invalid project key. Available keys are: {', '.join(PROJECTS.keys())}")
            return
        process_project(PROJECTS[project_key])
    else:
        for project in PROJECTS.values():
            process_project(project)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for unused API clients in Commercetools projects")
    parser.add_argument('project', nargs='?', choices=list(PROJECTS.keys()), 
                        help="The project to check (optional, if not provided, all projects will be checked)")
    args = parser.parse_args()
    
    main(args.project)